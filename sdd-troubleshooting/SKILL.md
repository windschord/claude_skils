---
name: sdd-troubleshooting
description: |
  Analyzes and resolves errors, bugs, and system issues through systematic root cause analysis.
  Handles test failures, build errors, runtime exceptions, and unexpected behavior.
  Compares issues against specifications (requirements/design docs) and creates fix plans with user approval.
  Use when: tests fail, builds break, runtime errors occur, features malfunction, or bugs are reported.
version: "1.0.0"
---

# SDDトラブルシューティングスキル

デバッグ・エラー修正・問題分析のための中核スキル。あらゆる問題に対して体系的に分析し、仕様に基づいた修正方針を策定します。

## 重要な原則

```text
┌─────────────────────────────────────────────────────────────────┐
│ エラー・バグ発生時の鉄則                                          │
├─────────────────────────────────────────────────────────────────┤
│ 1. 修正コードを書く前に、必ず根本原因を特定する                    │
│ 2. 推測に基づく修正は禁止（「たぶんこれが原因」はNG）             │
│ 3. 修正方針は必ずユーザー承認を得てから実装に進む                 │
│ 4. 原因不明のまま「とりあえず動くように」は禁止                   │
└─────────────────────────────────────────────────────────────────┘
```

## ワークフロー概要

```text
エラー/バグ発生
      ↓
1. 問題事象の確認（現象、再現手順、期待動作）
      ↓
2. 根本原因の分析（コードを追跡して原因を特定）
      ↓
3. 仕様との照合（docs/requirements/, docs/design/）
      ↓
4. 修正方針の策定（どう直すか、影響範囲は）
      ↓
5. ★ ユーザー承認 ★（必須ゲート - 承認なしで実装禁止）
      ↓
6. タスク分割 → docs/tasks/に追加
```

**詳細な分析手法**: [references/analysis_guide_ja.md](references/analysis_guide_ja.md)

## 使用場面

**以下のいずれかに該当する場合は、このスキルを使用する。**

### テスト・ビルドエラー時
- テストが失敗した場合
- ビルドエラー、コンパイルエラー、型エラー
- lint/静的解析エラー
- CI/CDパイプラインの失敗

### 実行時エラー・例外発生時
- 例外やエラーがスローされた場合
- クラッシュ・異常終了
- タイムアウト・ハング

### デバッグ時
- 期待と異なる動作をしている
- データが正しく処理されない
- 機能が動作しない

### 問題報告時
- ユーザーからの動作不良報告
- バグや不具合の発見

### 禁止パターン

```text
❌ エラーメッセージを見てなんとなく修正
❌ とりあえずtry-catchで囲む
❌ 似たエラーを以前直したから同じ修正
❌ 検索で見つけた解決策をそのまま適用
❌ 原因はわからないが動くようになった

✅ このスキルで根本原因を特定 → 修正方針を承認 → 実装
```

## 各ステップの概要

### ステップ1: 問題事象の確認

収集する情報:

| 項目 | 内容 |
|-----|------|
| 現象 | 何が起きているか |
| 期待動作 | 本来どう動くべきか |
| 再現手順 | どうすれば再現できるか |
| 発生環境 | どの環境で起きるか |
| エラー情報 | エラーメッセージ、ログ、スタックトレース |

### ステップ2: 根本原因の分析

1. 関連コードの特定（エラーメッセージ、スタックトレースから）
2. コードフローの追跡（入力から出力まで）
3. 原因の特定（なぜその問題が発生するか明確化）

**分析テクニック**: [references/analysis_guide_ja.md](references/analysis_guide_ja.md)

### ステップ3: 仕様との照合

- **要件定義との照合**: docs/requirements/を参照
- **設計との照合**: docs/design/を参照
- **乖離の分類**:
  - 実装バグ（仕様は正しいが実装が間違っている）
  - 仕様バグ（仕様自体に問題がある）
  - 仕様漏れ（仕様に記載がない）

### ステップ4: 修正方針の策定

検討項目:
- 修正アプローチ（複数ある場合は比較）
- 修正対象ファイル
- 影響範囲
- リスク評価
- 仕様更新の要否

### ステップ5: ユーザー承認（必須）

**修正方針をユーザーに提示し、承認を得てから次に進む。**

```text
修正方針について承認をお願いします。

【修正方針サマリー】
- 問題: [問題の概要]
- 原因: [原因の概要]
- 修正内容: [修正の概要]
- 影響範囲: [影響範囲の概要]

上記の修正方針で進めてよろしいでしょうか？
```

### ステップ6: タスク分割

- 適切な粒度（20-40分程度）
- 1タスク1責務
- 依存関係を明確化
- docs/tasks/に追加

**タスクテンプレート**: [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md)

## 成果物の保存

```text
docs/troubleshooting/
└── [YYYY-MM-DD]-[issue-name]/
    └── analysis.md
```

**分析レポートテンプレート**: [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md)

## SDDワークフローとの統合

```text
sdd-documentation
    ├── requirements-defining → docs/requirements/
    ├── software-designing   → docs/design/
    ├── task-planning        → docs/tasks/
    ├── task-executing       → 実装コード
    └── sdd-troubleshooting  → 問題分析・修正タスク（このスキル）
```

連携するドキュメント:
- **参照**: docs/requirements/（仕様照合用）
- **参照**: docs/design/（仕様照合用）
- **更新**: docs/tasks/（修正タスク追加）
- **作成**: docs/troubleshooting/（分析レポート）

## リソース

| リソース | 内容 |
|---------|------|
| [references/analysis_guide_ja.md](references/analysis_guide_ja.md) | 分析テクニック、問題分類、チェックリスト |
| [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md) | 分析レポートテンプレート |
| [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md) | バグ修正タスクテンプレート |
