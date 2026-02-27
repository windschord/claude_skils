# PRレビューコメントテンプレート

## 使用方法

このテンプレートをPRのサマリーコメントとして投稿する。
初回レビューと再レビューでセクション構成が異なる。

---

## 初回レビュー用サマリーテンプレート

```markdown
## Code Review Summary

### 概要

| 項目 | 内容 |
|------|------|
| PR | #[PR番号] [PRタイトル] |
| レビュー日 | [YYYY-MM-DD] |
| 変更ファイル数 | [N]ファイル |
| 追加行数 | +[N] |
| 削除行数 | -[N] |

### レビュー結果

| 観点 | critical | warning | suggestion | nitpick |
|------|----------|---------|------------|---------|
| セキュリティ | [N] | [N] | [N] | [N] |
| ドキュメント乖離 | [N] | [N] | [N] | [N] |
| 　└ 内部整合性 | [N] | [N] | [N] | [N] |
| 可読性・複雑度 | [N] | [N] | [N] | [N] |
| ライブラリ選定 | [N] | [N] | [N] | [N] |
| PR説明の適切性 | [N] | [N] | [N] | [N] |
| 既知脆弱性の検出 | [N] | [N] | [N] | [N] |
| **合計** | **[N]** | **[N]** | **[N]** | **[N]** |

※「内部整合性」はドキュメント乖離のサブカテゴリ。「ドキュメント乖離」行には内部整合性を除いた件数を記載し、合計行はすべての行の合算とする（二重カウントしない）。

### 総合判定

- [ ] Approve - 指摘なし、またはnitpickのみ
- [ ] Request Changes - critical/warningの指摘あり
- [ ] Comment - suggestionのみ

### 主要な指摘

> 詳細はインラインコメントおよびAI向けサマリーを参照してください。

#### Critical

- **[指摘タイトル]** (`[ファイル名]`)

#### Warning

- **[指摘タイトル]** (`[ファイル名]`)

※ suggestion / nitpick はインラインコメントのみに記載し、サマリーでは省略する。

<details>
<summary>AI向けレビューサマリー（構造化データ）</summary>

```json
{
  "review": {
    "pr_number": "[PR番号]",
    "date": "[YYYY-MM-DD]",
    "verdict": "approve | request_changes | comment",
    "stats": {
      "files_changed": "[N]",
      "additions": "[N]",
      "deletions": "[N]"
    },
    "findings": [
      {
        "id": "F-001",
        "file": "[ファイルパス]",
        "line": "[行番号]",
        "severity": "critical | warning | suggestion | nitpick",
        "category": "security | docs-drift | internal-consistency | readability | library | pr-description | known-vulnerability",
        "title": "[指摘タイトル]",
        "description": "[問題の説明]",
        "fix": {
          "old_text": "[置換対象のコードテキスト（該当行の正確な文字列）]",
          "new_text": "[置換後のコードテキスト]",
          "description": "[old_text/new_textで表現しきれない場合の補足説明（任意）]"
        },
        "context": "[該当行の前後3行程度のコード断片（ファイルを読み直さなくても位置特定できるようにする）]",
        "scope": "fix-in-this-pr | fix-in-follow-up | wont-fix",
        "rule": "[関連ルール: OWASP-A03, SRP等]",
        "verification_hint": "[修正後に確認すべきチェックポイント]"
      }
    ]
  }
}
```

#### findings各フィールドの説明

| フィールド | 説明 |
|-----------|------|
| `fix.old_text` | Edit ツールの `old_string` にそのまま渡せる、ファイル内でユニークな置換対象テキスト |
| `fix.new_text` | Edit ツールの `new_string` にそのまま渡せる置換後テキスト |
| `fix.description` | テキスト置換だけでは表現できない修正（ファイル追加・削除、設定変更等）の補足説明。`old_text`/`new_text` で十分な場合は省略可 |
| `context` | 該当行の前後約3行を含むコード断片。行番号のズレがあってもこのコンテキストで正確な位置を特定できる |
| `scope` | `fix-in-this-pr`: 本PRで修正すべき / `fix-in-follow-up`: 後続PRで対応 / `wont-fix`: 修正不要（理由を `description` に記載） |
| `rule` | 指摘の根拠となるルール・パターン名。例: `OWASP-A03`（セキュリティ）、`SRP`（設計原則）、`cyclomatic-complexity`（複雑度）等 |
| `verification_hint` | 修正Claudeが修正適用後に確認すべきチェックポイント。関連ファイルとの整合性、同一PR内の類似箇所等を記載 |

</details>

---
各指摘の詳細はインラインコメントを参照してください。
```

---

## 再レビュー用サマリーテンプレート

```markdown
## Re-Review Summary

### 概要

| 項目 | 内容 |
|------|------|
| PR | #[PR番号] [PRタイトル] |
| 再レビュー日 | [YYYY-MM-DD] |
| 前回レビュー日 | [YYYY-MM-DD] |
| 新規変更ファイル数 | [N]ファイル |

### 前回指摘の修正状況

| # | 指摘ID | 指摘内容 | 重大度 | 状態 | コメント |
|---|--------|---------|--------|------|---------|
| 1 | F-001 | [指摘概要] | critical | resolved | [修正確認コメント] |
| 2 | F-002 | [指摘概要] | warning | unresolved | [未修正の理由や追加コメント] |
| 3 | F-003 | [指摘概要] | suggestion | partially-resolved | [部分修正の状況] |

**修正状況サマリー:**
- resolved: [N]件
- partially-resolved: [N]件
- unresolved: [N]件
- wont-fix: [N]件
- regressed: [N]件

### 新規指摘

| 観点 | critical | warning | suggestion | nitpick |
|------|----------|---------|------------|---------|
| セキュリティ | [N] | [N] | [N] | [N] |
| ドキュメント乖離 | [N] | [N] | [N] | [N] |
| 　└ 内部整合性 | [N] | [N] | [N] | [N] |
| 可読性・複雑度 | [N] | [N] | [N] | [N] |
| ライブラリ選定 | [N] | [N] | [N] | [N] |
| PR説明の適切性 | [N] | [N] | [N] | [N] |
| 既知脆弱性の検出 | [N] | [N] | [N] | [N] |
| **合計** | **[N]** | **[N]** | **[N]** | **[N]** |

※「内部整合性」はドキュメント乖離のサブカテゴリ。「ドキュメント乖離」行には内部整合性を除いた件数を記載し、合計行はすべての行の合算とする（二重カウントしない）。

### 総合判定

- [ ] Approve - 前回指摘がすべてresolved、かつ新規criticalなし
- [ ] Request Changes - unresolved/regressedの指摘あり、または新規critical/warningあり
- [ ] Comment - 新規suggestionのみ

<details>
<summary>AI向け再レビューサマリー（構造化データ）</summary>

```json
{
  "re_review": {
    "pr_number": "[PR番号]",
    "date": "[YYYY-MM-DD]",
    "previous_review_date": "[YYYY-MM-DD]",
    "verdict": "approve | request_changes | comment",
    "previous_findings_status": [
      {
        "id": "F-001",
        "status": "resolved | partially-resolved | unresolved | wont-fix | regressed",
        "comment": "[確認コメント]",
        "scope": "fix-in-this-pr | fix-in-follow-up | wont-fix"
      }
    ],
    "new_findings": [
      {
        "id": "F-101",
        "file": "[ファイルパス]",
        "line": "[行番号]",
        "severity": "critical | warning | suggestion | nitpick",
        "category": "security | docs-drift | internal-consistency | readability | library | pr-description | known-vulnerability",
        "title": "[指摘タイトル]",
        "description": "[問題の説明]",
        "fix": {
          "old_text": "[置換対象のコードテキスト]",
          "new_text": "[置換後のコードテキスト]",
          "description": "[補足説明（任意）]"
        },
        "context": "[該当行の前後3行程度のコード断片]",
        "scope": "fix-in-this-pr | fix-in-follow-up | wont-fix",
        "rule": "[関連ルール]",
        "verification_hint": "[修正後に確認すべきチェックポイント]"
      }
    ]
  }
}
```

フィールド定義は初回レビューテンプレートと共通。`previous_findings_status` に `scope` を追加し、未修正の指摘に対しても本PRで対応すべきか後続で対応すべきかを明示する。

</details>

---
各指摘の詳細はインラインコメントを参照してください。
```

---

## インラインコメントテンプレート（個別指摘）

初回・再レビュー共通で使用する。

```markdown
**[critical]** セキュリティ

SQLインジェクションの脆弱性があります。ユーザー入力が直接SQL文に結合されています。
パラメータ化クエリを使用してください。

<details>
<summary>AI向け指示</summary>

```json
{
  "id": "F-001",
  "file": "src/repositories/userRepository.ts",
  "line": 42,
  "severity": "critical",
  "category": "security",
  "title": "SQL injection via string concatenation",
  "fix": {
    "old_text": "db.query(\"SELECT * FROM users WHERE id = \" + userId)",
    "new_text": "db.query(\"SELECT * FROM users WHERE id = ?\", [userId])"
  },
  "context": "async findById(userId: string) {\n  // ユーザーをIDで取得\n  const result = await db.query(\"SELECT * FROM users WHERE id = \" + userId)\n  return result.rows[0]\n}",
  "scope": "fix-in-this-pr",
  "rule": "OWASP-A03 (Injection)",
  "verification_hint": "修正後、同リポジトリ内の他のクエリ関数（findByEmail, findAll等）にも同様の文字列結合がないか確認"
}
```

</details>
```

**テンプレートの設計方針:**

- **人間向け（メインボディ）**: 問題の概要と推奨修正方針を簡潔に記載。詳細なコード差分はAI向けJSONに集約し重複を避ける
- **AI向け（detailsブロック）**: `fix.old_text`/`fix.new_text`で機械的に修正を適用可能。`context`で正確な位置を特定可能。`verification_hint`で修正後のチェックポイントを提示

---

## 再レビュー時の修正確認インラインコメントテンプレート

前回指摘の修正が確認できた場合に使用する。

```markdown
**[resolved]** 前回指摘 F-001 の修正確認

前回指摘したSQLインジェクションの脆弱性が、パラメータ化クエリへの変更により
適切に修正されていることを確認しました。

<details>
<summary>AI向け指示</summary>

- finding_id: F-001
- status: resolved
- verification: Confirmed parameterized query is now used at src/repositories/userRepository.ts:42

</details>
```
