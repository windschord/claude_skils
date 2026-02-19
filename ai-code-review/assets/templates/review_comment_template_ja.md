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
| 可読性・複雑度 | [N] | [N] | [N] | [N] |
| ライブラリ選定 | [N] | [N] | [N] | [N] |
| **合計** | **[N]** | **[N]** | **[N]** | **[N]** |

### 総合判定

- [ ] Approve - 指摘なし、またはnitpickのみ
- [ ] Request Changes - critical/warningの指摘あり
- [ ] Comment - suggestionのみ

### 指摘サマリー（人間向け）

#### Critical

1. **[指摘タイトル]** ([ファイル名]:[行番号])
   [指摘内容の要約]

#### Warning

1. **[指摘タイトル]** ([ファイル名]:[行番号])
   [指摘内容の要約]

#### Suggestion

1. **[指摘タイトル]** ([ファイル名]:[行番号])
   [指摘内容の要約]

<details>
<summary>AI向けレビューサマリー</summary>

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
        "category": "security | docs-drift | readability | library",
        "title": "[指摘タイトル]",
        "description": "[問題の説明]",
        "fix": "[修正方法]",
        "rule": "[関連ルール: OWASP-A03, SRP等]"
      }
    ]
  }
}
```

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
| 可読性・複雑度 | [N] | [N] | [N] | [N] |
| ライブラリ選定 | [N] | [N] | [N] | [N] |
| **合計** | **[N]** | **[N]** | **[N]** | **[N]** |

### 総合判定

- [ ] Approve - 前回指摘がすべてresolved、かつ新規criticalなし
- [ ] Request Changes - unresolved/regressedの指摘あり、または新規critical/warningあり
- [ ] Comment - 新規suggestionのみ

<details>
<summary>AI向け再レビューサマリー</summary>

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
        "comment": "[確認コメント]"
      }
    ],
    "new_findings": [
      {
        "id": "F-101",
        "file": "[ファイルパス]",
        "line": "[行番号]",
        "severity": "critical | warning | suggestion | nitpick",
        "category": "security | docs-drift | readability | library",
        "title": "[指摘タイトル]",
        "description": "[問題の説明]",
        "fix": "[修正方法]",
        "rule": "[関連ルール]"
      }
    ]
  }
}
```

</details>

---
各指摘の詳細はインラインコメントを参照してください。
```

---

## インラインコメントテンプレート（個別指摘）

初回・再レビュー共通で使用する。

```markdown
**[critical]** セキュリティ

SQLインジェクションの脆弱性があります。ユーザー入力が直接SQL文に結合されているため、
悪意ある入力でデータベースが操作される可能性があります。

修正前:
`db.query("SELECT * FROM users WHERE id = " + userId)`

修正後（推奨）:
`db.query("SELECT * FROM users WHERE id = ?", [userId])`

パラメータ化クエリを使用することで、入力値がSQL文の構造を変更できなくなります。

<details>
<summary>AI向け指示</summary>

- file: src/repositories/userRepository.ts
- line: 42
- severity: critical
- category: security
- issue: SQL injection via string concatenation in user query
- fix: Replace string concatenation with parameterized query. Change `db.query("SELECT * FROM users WHERE id = " + userId)` to `db.query("SELECT * FROM users WHERE id = ?", [userId])`
- rule: OWASP-A03 (Injection)

</details>
```

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
