---
name: self-review
description: ローカルの変更差分（git diff）を3つのサブエージェントで並列レビューし、結果を統合して修正を適用する。PR作成前やタスク完了前のローカル品質チェックに使用する。ai-code-reviewと同一の6観点・重大度基準を適用する。
metadata:
  version: "2.0.0"
---

# セルフレビュースキル

ローカルの変更差分をサブエージェントで並列レビューし、PR作成前に品質問題を検出・修正するスキルです。ai-code-reviewと同一の6観点・重大度基準を使用しますが、GitHub API不要でローカル完結します。

## 重要な原則

```text
+---------------------------------------------------------------+
| セルフレビューの鉄則                                             |
+---------------------------------------------------------------+
| 1. 推測でレビューしない - 必ずコードを読んで根拠を示す              |
| 2. 6つの観点を漏れなくチェックする                                |
| 3. 指摘には必ず根拠（該当コード・行番号）を添える                   |
| 4. 数値・事実を根拠にする場合は必ずソースを確認する                  |
| 5. 重大度を正確に分類し、過剰な指摘を避ける                        |
| 6. critical/warningはユーザー承認なしに修正しない                  |
| 7. suggestion/nitpickも修正前にユーザーに提示する                 |
+---------------------------------------------------------------+
```

## アーキテクチャ

```text
メインClaude（オーケストレーター）
    |
    +-- 1. 差分取得・ファイル分類（メインが実行）
    |
    +-- 2. 3サブエージェントを並列起動（Agent tool）
    |       |
    |       +-- エージェントA: セキュリティ + 既知脆弱性
    |       +-- エージェントB: 可読性・複雑度
    |       +-- エージェントC: ドキュメント乖離 + ライブラリ選定 + 変更説明の適切性
    |
    +-- 3. 結果の統合・重複排除（メインが実行）
    |
    +-- 4. ユーザーへの報告・承認確認（メインが実行）
    |
    +-- 5. 修正適用（メインが実行）
```

## レビュー観点（6つ）

| # | 観点 | category値 | 担当エージェント |
|---|------|-----------|----------------|
| 1 | セキュリティ | `security`, `iam-permissions` | A |
| 2 | ドキュメントとの乖離 | `docs-drift`, `internal-consistency` | C |
| 3 | 可読性・複雑度 | `readability` | B |
| 4 | ライブラリ選定の妥当性 | `library` | C |
| 5 | 変更説明の適切性 [^1] | `change-description` | C |
| 6 | 既知脆弱性の検出 | `known-vulnerability` | A |

[^1]: ai-code-reviewの「PR説明の適切性」（category: `pr-description`）に対応。ローカルレビュー用に名称とcategory値を変更。

**各観点の詳細レビュー基準**: [../ai-code-review/references/review_guide_ja.md](../ai-code-review/references/review_guide_ja.md)

**重大度の定義:**

| 重大度 | 意味 | 修正要否 |
|--------|------|---------|
| critical | セキュリティ脆弱性、データ損失の可能性、本番障害のリスク | 修正必須 |
| warning | バグの可能性、パフォーマンス問題、設計上の懸念 | 修正推奨 |
| suggestion | より良い実装方法の提案、リファクタリング案 | 任意 |
| nitpick | スタイル、命名、些細な改善 | 任意 |

## このスキルを使用する場面

- 実装完了後、PRを作成する前に品質を確認したい場合
- SDDタスクをDONEにする前の最終チェック（逆順レビューと併用）
- 特定のファイルやディレクトリの変更のみをレビューしたい場合

## ワークフロー

```text
レビュー対象の指定
      |
1. 差分取得・ファイル分類（メイン）
      |
2. サブエージェント並列起動（Agent tool × 3）
   → 各エージェントはJSON形式で結果を返す
      |
3. 結果統合・重複排除・横断チェック（メイン）
      |
4. ユーザーへ報告・承認確認（メイン）
      |
5. 修正適用（メイン、Editツール）
      |
6. 修正後の再チェック（必要な場合）
```

## ステップ1: 差分取得・ファイル分類

メインClaude自身が実行する。

```bash
# ベースブランチの自動判定
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
# フォールバック: main → master → エラー
if [ -z "$BASE" ]; then
  if git show-ref --verify --quiet refs/remotes/origin/main; then
    BASE="main"
  elif git show-ref --verify --quiet refs/remotes/origin/master; then
    BASE="master"
  else
    echo "ERROR: ベースブランチが見つかりません。明示的に指定してください。" >&2
    exit 1
  fi
fi

# 変更ファイル一覧
git diff ${BASE}...HEAD --name-only

# 変更統計
git diff ${BASE}...HEAD --stat

# 差分全体
git diff ${BASE}...HEAD
```

ユーザーが明示指定した場合はそれに従う（`--cached`、特定パス等）。

差分取得方法（レポートの`metadata.diff_method`値）:

| diff_method値 | 対応コマンド |
|--------------|------------|
| `branch` | `git diff ${BASE}...HEAD`（デフォルト） |
| `cached` | `git diff --cached` |
| `head` | `git diff HEAD` |
| `working` | `git diff` |
| `path` | `git diff ${BASE}...HEAD -- <path>` |

ファイル分類の優先度:

| 優先度 | カテゴリ | 例 |
|--------|---------|-----|
| 高 | セキュリティ関連 | 認証、認可、暗号化、入力処理、Terraform IAM |
| 高 | API / データベース | エンドポイント、マイグレーション、スキーマ |
| 中 | ビジネスロジック | ドメインロジック、サービス層 |
| 中 | 設定・インフラ | CI/CD、Docker、依存関係 |
| 低 | UI/表示 | テンプレート、スタイルシート |
| 低 | テスト | テストコード（セキュリティテストは優先度高） |
| 低 | ドキュメント | README、コメント更新 |

## ステップ2: サブエージェント並列起動

**3つのサブエージェントをAgent toolで同時に起動する。**

各サブエージェントへのプロンプトには以下を含める:

1. 担当観点の明示
2. レビュー対象のファイル一覧とベースブランチ
3. レビュー基準の参照先（`ai-code-review/references/review_guide_ja.md`の該当セクション）
4. **出力フォーマットの指定**（後述のJSON形式）
5. 観点5（変更説明の適切性）はローカル用読み替えルール

**サブエージェントへのプロンプトテンプレート**: [references/self_review_guide_ja.md](references/self_review_guide_ja.md)

### サブエージェントの出力フォーマット（必須）

各サブエージェントは、レビュー結果を以下のJSON形式で返すこと。**このフォーマット以外の出力は不要（説明文・マークダウン表等は不要）。**

```json
{
  "agent": "A|B|C",
  "perspectives": ["担当観点名"],
  "findings": [
    {
      "id": "F-NNN",
      "file": "src/example.ts",
      "line": "42-45",
      "severity": "critical|warning|suggestion|nitpick",
      "category": "security|iam-permissions|docs-drift|internal-consistency|readability|library|change-description|known-vulnerability",
      "title": "問題の端的な説明",
      "reason": "なぜ問題なのか、根拠（該当コードの引用を含む）",
      "fix": {
        "old_text": "Editツールにそのまま渡せる置換対象テキスト",
        "new_text": "置換後テキスト"
      },
      "fix_strategy": {
        "approach": "推奨する修正アプローチ",
        "alternatives": ["代替案（あれば）"],
        "impact": "他ファイル・コンポーネントへの波及",
        "effort": "small|medium|large"
      },
      "context": "該当行の前後3行程度のコード断片（位置特定用）",
      "rule": "関連ルール名（例: OWASP-A03, SRP）",
      "verification_hint": "修正後に確認すべきポイント"
    }
  ],
  "cross_checks": [
    {
      "pattern": "検出した問題パターン",
      "files_checked": ["確認済みファイル一覧"],
      "additional_occurrences": ["同一パターンが見つかった他のファイル:行番号"]
    }
  ],
  "summary": {
    "critical": 0,
    "warning": 0,
    "suggestion": 0,
    "nitpick": 0
  }
}
```

### フォーマットの設計根拠

- `fix.old_text`/`fix.new_text`: メインClaudeがEditツールにそのまま渡せる
- `context`: 行番号ズレがあっても位置を特定できる
- `cross_checks`: 横断チェック結果をメインに返し、メインが統合判断する
- `summary`: メインが各エージェントの結果を即座に集計できる
- **説明文やマークダウンは不要**: メインClaudeがJSONを直接解釈し、ユーザー向け報告はメインが生成する
- **ai-code-reviewとの差異**: `scope`フィールド（PR対応範囲の判定）はローカルレビューでは不要なため省略。`fix.description`（ai-code-review側でも任意）もローカルでは省略

> **注**: レポート出力時にメインClaudeが`source_agent`（検出エージェント）と`resolution`（修正状況、初期値null）を各findingに追加する。サブエージェントはこれらを出力しない。

## ステップ3: 結果統合

メインClaudeが3エージェントの結果を統合する。

1. 全エージェントの`findings`を結合し、各findingに`source_agent`を付与
2. 重複排除: 同一ファイル・同一行の指摘が複数エージェントから出た場合は統合
3. `cross_checks`の統合: エージェント間で同一パターンの横断結果をマージ
4. 重大度の高い順にソート
5. IDの振り直し（F-001から連番）
6. `summary`に`total`を算出して追加（サブエージェント出力にはtotalなし）
7. `files`配列を生成: ステップ1のファイル分類結果（パス・変更行数・優先度・カテゴリ）を格納

## ステップ4: ユーザーへの報告・承認確認

統合結果をユーザーに分かりやすく提示する。

出力形式（ユーザー向け）:

```text
## セルフレビュー結果

対象: {branch} vs {base} | ファイル: {N}件 | +{add}/-{del}行

| 重大度 | 件数 |
|--------|------|
| critical | X |
| warning | X |
| suggestion | X |
| nitpick | X |

### 指摘一覧

1. **[critical]** `src/auth.ts:42` セキュリティ: SQLインジェクションの可能性
   修正: パラメータ化クエリに置換 (effort: small)
2. **[warning]** `src/utils.ts:15` 可読性: 循環的複雑度が高い（12）
   修正: 条件分岐を早期リターンに分解 (effort: medium)
...
```

critical/warningがある場合は`AskUserQuestion`で修正方針を確認:

```text
AskUserQuestion:
  question: "指摘について、どのように対応しますか？"
  options:
    - label: "すべて修正する"
      description: "critical/warningの指摘をすべて修正します"
    - label: "選択して修正する"
      description: "修正する指摘を個別に選択します"
    - label: "レポートのみ出力"
      description: "修正は行わず、レポートファイルに出力します"
    - label: "対応しない"
      description: "確認のみとし、修正は行いません"
```

## ステップ5: 修正適用

承認された指摘の`fix.old_text`/`fix.new_text`をEditツールで適用する。

- 1指摘ずつ適用（一括適用しない）
- 各修正前にReadツールで最新状態を確認
- 修正困難な場合はユーザーに具体的手順を提示

## ステップ6: 修正後の再チェック

critical/warningの修正適用後、修正箇所を再読み込みしてリグレッションがないか確認する。

## レポートファイル出力（オプション）

ユーザーが「レポートのみ出力」を選択した場合、統合済みJSONをファイルに出力する。

出力先: `.self-review/review-YYYY-MM-DD-HHMMSS.json`

**レポートテンプレート**: [assets/templates/self_review_report_template_ja.md](assets/templates/self_review_report_template_ja.md)

## 再レビュー

前回のレポートファイル（`.self-review/`）が存在する場合、再レビューとして前回指摘の修正状況を確認できる。

1. `.self-review/`から最新のレポートファイルを読み込む
2. 前回`findings`の各指摘について修正状況を確認:

| 状態 | 説明 |
|------|------|
| resolved | 修正済み |
| partially-resolved | 一部修正されたが不十分 |
| unresolved | 未修正 |
| wont-fix | 修正しない判断がされた |
| regressed | 修正により別の問題が発生 |

3. 新規変更に対してサブエージェント並列レビューを実施
4. 前回指摘の修正状況 + 新規指摘を統合して報告

## SDDワークフローとの連携

```text
タスク実装完了
    |
    +-- 逆順レビュー（task-executing）: ドキュメント整合性
    |     tasks/ → design/ → requirements/
    |
    +-- セルフレビュー（self-review）: コード品質
          3エージェント並列レビュー → 修正 → PR作成
```

SDDプロジェクトの場合、エージェントCの「ドキュメント乖離」観点でSDD文書（requirements/、design/、tasks/）との整合も確認する。逆順レビュー実施済みの場合はその結果をプロンプトに含め、重複指摘を避ける。

## 禁止事項

```text
- 推測に基づくレビュー（コードを読まずに指摘する）
- 個人の好みだけを根拠にした指摘
- 裏取りなしに数値・事実を断定する指摘
- 変更範囲外のコードへの指摘（ただしセキュリティ問題と横断チェックで発見した同一パターンの問題は例外。横断チェックでは変更ファイルと関連する未変更ファイルも確認するが、指摘はパターンの共有と注意喚起に留め、修正対象は変更範囲内に限定する）
- 過剰な nitpick
- ユーザーの承認なしにcritical/warningの修正を適用すること
- レビュー結果を報告せず修正だけ行うこと（必ず先に結果を提示する）
- サブエージェントがJSON以外の形式で結果を返すこと
```

## リソース

| リソース | 内容 |
|---------|------|
| [../ai-code-review/references/review_guide_ja.md](../ai-code-review/references/review_guide_ja.md) | 6観点の詳細レビューガイドライン（ai-code-reviewと共有） |
| [references/self_review_guide_ja.md](references/self_review_guide_ja.md) | サブエージェントプロンプト・差分取得・修正適用・SDD連携 |
| [assets/templates/self_review_report_template_ja.md](assets/templates/self_review_report_template_ja.md) | レポート出力フォーマット |
