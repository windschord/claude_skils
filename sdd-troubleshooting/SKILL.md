---
name: sdd-troubleshooting
description: エラー・バグ・問題を体系的に分析し修正方針を策定する。テスト失敗、ビルドエラー、実行時エラー、動作不良、バグ報告に対応。「エラーを調べて」「バグを修正して」「テストが失敗した」「動作がおかしい」等の問題指摘・修正依頼時に使用。根本原因を分析してからユーザー承認を得て修正する。
metadata:
  version: "1.0.0"
---

# SDDトラブルシューティングスキル

あらゆるエラー・バグに対して体系的に根本原因を分析し、仕様に基づいた修正方針を策定する。

## 鉄則

1. 修正コードを書く前に、必ず根本原因を特定する
2. 推測に基づく修正は禁止
3. 修正方針は必ずユーザー承認を得てから実装に進む

## ワークフロー

```text
エラー/バグ発生
  → 1. 問題事象の確認（現象、再現手順、期待動作）
  → 2. 並列調査判定（原因候補3つ以上 → Agent toolで並列調査）
  → 3. 根本原因の分析（コードを追跡して原因を特定）
  → 4. 仕様との照合（docs/sdd/requirements/, docs/sdd/design/）
  → 5. 修正方針の策定（修正内容、影響範囲、リスク）
  → 6. ★ ユーザー承認 ★（必須ゲート）
  → 7. タスク分割 → docs/sdd/tasks/に追加 → task-executingで実装
```

詳細な分析手法は [references/analysis_guide_ja.md](references/analysis_guide_ja.md) を参照。

## 各ステップの概要

### ステップ1: 問題事象の確認

| 項目 | 内容 |
|-----|------|
| 現象 | 何が起きているか |
| 期待動作 | 本来どう動くべきか |
| 再現手順 | どうすれば再現できるか |
| 発生環境 | どの環境で起きるか |
| エラー情報 | エラーメッセージ、ログ、スタックトレース |

### ステップ2-3: 根本原因の分析

1. 関連コードの特定（エラーメッセージ、スタックトレースから）
2. コードフローの追跡（入力から出力まで）
3. 原因の特定（なぜその問題が発生するか明確化）

### ステップ4: 仕様との照合

- **実装バグ**: 仕様は正しいが実装が間違っている
- **仕様バグ**: 仕様自体に問題がある
- **仕様漏れ**: 仕様に記載がない

### ステップ5-6: 修正方針の策定とユーザー承認

```text
【修正方針サマリー】
- 問題: [問題の概要]
- 原因: [原因の概要]
- 修正内容: [修正の概要]
- 影響範囲: [影響範囲の概要]
```

### ステップ7: タスク分割

適切な粒度（20-40分程度）で1タスク1責務。docs/sdd/tasks/に追加。テンプレートは [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md) を参照。

## Agent toolによる並列調査

### 適用条件（ステップ2で判定）

1. 原因の候補が3つ以上ある
2. 仮説間に依存関係がない（独立して調査可能）

すべてYES → Agent toolで並列調査。いずれかNO → 単一セッションで分析続行。

調査は読み取り専用のため `isolation: worktree` は不要。1つのメッセージで複数のAgent toolを同時に呼び出す。各サブエージェントには仮説・調査対象・調査手順を指定し、「仮説の支持/棄却」「根拠」「追加発見」を報告させる。

並列調査後、結果を統合して最も有力な根本原因を特定し、通常のフローに戻る。

詳細は [sdd-documentation/references/agent_teams_guide_ja.md](../sdd-documentation/references/agent_teams_guide_ja.md) を参照。

## 成果物の保存

```text
docs/sdd/troubleshooting/
└── [YYYY-MM-DD]-[issue-name]/
    └── analysis.md
```

分析レポートテンプレート: [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md)

## TodoWrite連携

修正タスクをdocs/sdd/tasks/に追加した場合、`[TASK-XXX] [BugFix] 修正内容` の形式でTodoWriteにpendingとして同期する。

## リソース

| リソース | 内容 |
|---------|------|
| [references/analysis_guide_ja.md](references/analysis_guide_ja.md) | 分析テクニック、問題分類、チェックリスト |
| [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md) | 分析レポートテンプレート |
| [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md) | バグ修正タスクテンプレート |
