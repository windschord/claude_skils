# セルフレビューレポートフォーマット

このファイルはレポートファイル（`.self-review/review-YYYY-MM-DD-HHMMSS.json`）の出力フォーマットを定義します。

## 出力フォーマット

レポートファイルは以下のJSON構造で出力する。メインClaudeが再レビュー時に読み込んで前回指摘との差分確認に使用する。

```json
{
  "metadata": {
    "version": "2.0.0",
    "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
    "branch": "feature/xxx",
    "base_branch": "main",
    "diff_method": "branch",
    "files_changed": 5,
    "lines_added": 120,
    "lines_deleted": 30
  },
  "summary": {
    "critical": 0,
    "warning": 0,
    "suggestion": 0,
    "nitpick": 0,
    "total": 0
  },
  "findings": [
    {
      "id": "F-001",
      "file": "src/example.ts",
      "line": "42-45",
      "severity": "critical",
      "category": "security",
      "title": "問題の端的な説明",
      "reason": "なぜ問題なのか、根拠",
      "fix": {
        "old_text": "置換対象テキスト",
        "new_text": "置換後テキスト"
      },
      "fix_strategy": {
        "approach": "推奨する修正アプローチ",
        "alternatives": [],
        "impact": "影響範囲",
        "effort": "small|medium|large"
      },
      "context": "前後3行のコード断片",
      "rule": "OWASP-A03",
      "verification_hint": "修正後の確認ポイント",
      "source_agent": "A",
      "resolution": null
    }
  ],
  "cross_checks": [
    {
      "pattern": "検出した問題パターン",
      "files_checked": ["確認済みファイル一覧"],
      "additional_occurrences": ["他ファイル:行番号"]
    }
  ],
  "files": [
    {
      "path": "src/example.ts",
      "lines_added": 50,
      "lines_deleted": 10,
      "priority": "high|medium|low",
      "category": "セキュリティ関連|API / データベース|ビジネスロジック|設定・インフラ|UI/表示|テスト|ドキュメント"
    }
  ],
  "previous_review": null
}
```

## 再レビュー時のフォーマット

再レビュー時は`previous_review`フィールドに前回情報を含める:

```json
{
  "previous_review": {
    "timestamp": "前回レビューのタイムスタンプ",
    "report_file": "前回レポートのファイルパス",
    "status_summary": {
      "resolved": 0,
      "partially-resolved": 0,
      "unresolved": 0,
      "wont-fix": 0,
      "regressed": 0
    },
    "findings_status": [
      {
        "id": "F-001",
        "status": "resolved|partially-resolved|unresolved|wont-fix|regressed",
        "comment": "状態判定の根拠"
      }
    ]
  }
}
```

## フィールド説明

| フィールド | 用途 |
|-----------|------|
| `metadata` | メインClaudeがレポートの基本情報を即座に把握するため |
| `summary` | 指摘件数の集計。ユーザー報告時にそのまま使用 |
| `findings` | 全指摘の構造化データ。`fix`はEditツールに直接渡せる形式 |
| `findings[].source_agent` | どのエージェントが検出したか（デバッグ・品質確認用） |
| `findings[].resolution` | 初回レビュー時は`null`。修正適用後に結果を記録 |
| `cross_checks` | 横断チェック結果。同一パターンの問題を漏れなく把握 |
| `files` | 変更ファイルの分類情報。再レビュー時のスコープ確認用 |
| `previous_review` | 再レビュー時のみ。前回指摘の修正状況追跡用 |

> **注**: ai-code-reviewとの差異として、本フォーマットでは`scope`フィールドと`fix.description`フィールドを含まない。

## resolution記録（修正適用後）

修正を適用した場合、該当findingの`resolution`を更新する:

```json
{
  "resolution": {
    "status": "fixed|skipped|deferred",
    "applied_at": "YYYY-MM-DDTHH:MM:SSZ",
    "comment": "修正内容や見送り理由"
  }
}
```

### resolution.statusと再レビュー時statusの対応関係

| resolution.status（修正直後） | 再レビュー時の判定結果 |
|------------------------------|---------------------|
| `fixed` | → `resolved` または `regressed`（修正が正しいか再確認） |
| `skipped` | → `unresolved` または `wont-fix`（ユーザー意図による） |
| `deferred` | → `unresolved`（後続対応として残存） |
