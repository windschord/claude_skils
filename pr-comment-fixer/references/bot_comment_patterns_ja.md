# botコメントパターンリファレンス

レビュアーbotごとのコメント構造パターンと抽出方法を定義する。各botはコメントの投稿先・フォーマットが異なるため、bot種別に応じた解析が必要。

## bot判定方法

コメントの`user.login`フィールドで判定する:

| bot | user.login | 判定パターン |
|-----|-----------|-------------|
| CodeRabbit | `coderabbitai[bot]` | 完全一致 |
| Copilot | `copilot[bot]` | 完全一致 |
| GitHub Actions | `github-actions[bot]` | 完全一致 |
| SonarCloud | `sonarcloud[bot]` | 完全一致 |
| Snyk | `snyk-bot` | 完全一致 |
| その他 | - | 汎用パーサーで処理 |

`[bot]`サフィックスの有無でもbot/人間を大まかに判定できるが、全てのbotが`[bot]`サフィックスを持つとは限らない。

## CodeRabbit

### コメント投稿先

| コメント種別 | 投稿先API | 取得方法 |
|-------------|----------|---------|
| Actionable（Major/Minor） | インラインスレッド | `pulls/comments` + GraphQL `reviewThreads` |
| Nitpick | Review body内の`<details>`タグ | `pulls/reviews`のbodyフィールド |
| Summary | Issue Comment | `issues/comments` |

### Nitpickコメントの構造（Review body内）

CodeRabbitのレビュー本文（body）には、以下の構造でNitpickが埋め込まれる:

```html
<details>
<summary>🧹 Nitpick comments (3)</summary>

1. **path/to/file.ts (line 42)**: Consider using `const` instead of `let` here since the variable is never reassigned.

2. **path/to/file.ts (line 85-87)**: The error message could be more descriptive.

3. **docs/README.md**: Minor typo in the description.

</details>
```

### Nitpick抽出パターン

**Step 1: `<details>`ブロックの抽出**

Nitpickセクションを含む`<details>`ブロックを特定する。`summary`タグにNitpickを示すキーワードが含まれるブロックを対象とする。

判定キーワード（summaryタグ内）:
- `Nitpick`
- `nitpick`
- `🧹`

**Step 2: 個別コメントの抽出**

`<details>`ブロック内の番号付きリストから、個別のコメントを抽出する。

各コメントのパターン:
- `**ファイルパス (line 行番号)**: コメント本文`
- `**ファイルパス (line 開始行-終了行)**: コメント本文`
- `**ファイルパス**: コメント本文`（行番号なし）

抽出対象:
- `path`: ファイルパス（`**`と`**`の間）
- `line`: 行番号（`(line N)` または `(line N-M)` から。なければnull）
- `body`: コメント本文（`: `以降）

### Actionableコメントの構造（インラインスレッド）

通常のインラインコメントとして投稿される。`pulls/comments`APIで取得可能。

特徴:
- `path`と`line`が明示的にAPIレスポンスに含まれる
- `diff_hunk`でコンテキストを確認できる
- GraphQL `reviewThreads`で`isResolved`を確認できる

### Summaryコメントの構造（Issue Comment）

PRの全体要約として投稿される。通常、修正対象のコメントではないため、スキップ対象とする。

判定方法: bodyが以下のいずれかで始まる場合はSummary
- `## Summary by CodeRabbit`
- `## Walkthrough`
- `<!-- This is an auto-generated comment by CodeRabbit -->`

### 実例: PR #220のReview body（Nitpick埋め込み）

Review ID: 3943619906

```markdown
<details>
<summary>🧹 Nitpick comments (2)</summary>

1. `docs/sdd/tasks/network-filtering/index.md` の整合表に TASK-019 / REQ-009 のエントリが欠けている

2. `src/app/api/environments/__tests__/route.test.ts` のネットワークフィルタリングモックに beforeEach でデフォルト戻り値を設定すると、各テストの意図が明確になる

</details>
```

注意: この例ではファイルパスはバッククォートで囲まれ、行番号は含まれていない。パーサーはバッククォート内のパスも抽出できる必要がある。

## Copilot

### コメント投稿先

| コメント種別 | 投稿先API | 取得方法 |
|-------------|----------|---------|
| インラインコメント | インラインスレッド | `pulls/comments` + GraphQL `reviewThreads` |
| Review body | Review本文 | `pulls/reviews`のbodyフィールド（通常は空） |

### インラインコメントの特徴

- `path`と`line`が明示的
- コード修正の提案を含むことが多い
- suggestion形式（suggestionコードブロック）を使用する場合がある

### suggestion形式の検出

````markdown
```suggestion
const result = await fetchData();
```
````

suggestion形式のコメントは、API応答の`start_line`・`line`（または同等の範囲フィールド）で特定した置換対象レンジを提案コードで置き換えて対応する。単一行前提で処理せず、複数行suggestion（`start_line`〜`line`）を正確に扱い、diffコンテキストの整合性を検証した上で適用すること。不一致が検出された場合はauto-fixを中止しmanual-requiredにフォールバックする。

## 汎用パーサー

CodeRabbitとCopilot以外のbot（SonarCloud, Snyk, GitHub Actions等）や、パターンが一致しないコメントに対する汎用的な処理。

### 処理方針

1. **インラインコメント**: `path`と`line`がAPIレスポンスに含まれるため、そのまま使用
2. **Review body**: プレーンテキストとして全文を1つのコメントとして扱う
3. **Issue Comment**: ファイルパスと行番号の抽出を試み、失敗した場合はmanual-requiredに分類

### ファイルパス検出のヒューリスティック

Review bodyやIssue Comment内のテキストからファイルパスを推定する:

1. バッククォート内のパス: `` `src/path/to/file.ts` ``
2. 太字内のパス: `**src/path/to/file.ts**`
3. 拡張子を持つ文字列: 既知の拡張子（`.ts`, `.js`, `.py`, `.go`等）で終わるパス風の文字列

行番号の検出:
1. `line N` / `line N-M` パターン
2. `L42` / `L42-L50` パターン
3. `(行番号)` / `(N行目)` パターン

## コメント分類基準

### 種別（type）

| 種別 | 説明 | 対応方針 |
|------|------|---------|
| `actionable` | コード修正が必要な指摘 | auto-fixまたはmanual |
| `nitpick` | 軽微な改善提案 | auto-fix |
| `suggestion` | コード提案（suggestブロック等） | auto-fix |
| `praise` | 良い点への言及 | スキップ |
| `question` | 質問・確認 | manual-required |
| `summary` | PR全体の要約 | スキップ |

### 重要度（severity）

| 重要度 | 説明 | 優先度 |
|--------|------|--------|
| `critical` | セキュリティ脆弱性、データ損失リスク | 最優先で対応 |
| `major` | バグ、ロジックエラー、機能不全 | 優先対応 |
| `minor` | コード品質、パフォーマンス改善 | 通常対応 |
| `nitpick` | スタイル、命名、ドキュメント | 最後に対応 |

### praise/summaryの自動判定

以下のパターンに該当するコメントはスキップ対象:

- praise: 本文に肯定的表現のみ（`LGTM`, `Great`, `Nice`, `Well done`等）
- summary: CodeRabbitの`## Summary`, `## Walkthrough`セクション
- 解決済み: GraphQL `isResolved: true`のスレッド
