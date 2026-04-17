---
name: sdd-troubleshooting
description: エラー・バグ・問題を体系的に分析し修正方針を策定する。テスト失敗、ビルドエラー、実行時エラー、動作不良、バグ報告に対応し、根本原因を分析してから修正を行う。Do NOT use for 根本原因分析が不要な軽微な修正（typo、設定値変更、フォーマット修正など）。
metadata:
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
2. ★ 並列調査判定 ★（原因候補が3つ以上 → Agent toolで並列調査）
      ↓
   ┌─ YES → Agent toolで並列調査（下記参照）
   └─ NO  → 単一セッションで分析続行
      ↓
3. 根本原因の分析（コードを追跡して原因を特定）
      ↓
4. 仕様との照合（docs/sdd/requirements/, docs/sdd/design/）
      ↓
5. 修正方針の策定（どう直すか、影響範囲は）
      ↓
6. ★ ユーザー承認 ★（必須ゲート - 承認なしで実装禁止）
      ↓
7. タスク分割 → docs/sdd/tasks/に追加
```

**詳細な分析手法**: [references/analysis_guide_ja.md](references/analysis_guide_ja.md)

## このスキルを使用する場面

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

- **要件定義との照合**: docs/sdd/requirements/を参照
- **設計との照合**: docs/sdd/design/を参照
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
- docs/sdd/tasks/に追加

**タスクテンプレート**: [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md)

## 成果物の保存

```text
docs/sdd/troubleshooting/
└── [YYYY-MM-DD]-[issue-name]/
    └── analysis.md
```

**分析レポートテンプレート**: [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md)

## SDDワークフローとの統合

```text
sdd-documentation
    ├── requirements-defining → docs/sdd/requirements/
    ├── software-designing   → docs/sdd/design/
    ├── task-planning        → docs/sdd/tasks/
    ├── task-executing       → 実装コード
    └── sdd-troubleshooting  → 問題分析・修正タスク（このスキル）
```

連携するドキュメント:
- **参照**: docs/sdd/requirements/（仕様照合用）
- **参照**: docs/sdd/design/（仕様照合用）
- **更新**: docs/sdd/tasks/（修正タスク追加）
- **作成**: docs/sdd/troubleshooting/（分析レポート）

## Agent toolによる並列調査（条件を満たす場合は積極的に使用）

### 概要

原因が不明な複雑なバグの場合、Agent toolを使用して複数の仮説を並列で調査する。各サブエージェントが異なる仮説を担当し、並列に調査を進めることで、より迅速に根本原因に到達する。

**重要**: ワークフローのステップ2で以下の条件を評価し、満たす場合は**必ずAgent toolで並列調査**すること。

### 適用条件（ステップ2で必ず判定）

1. 原因の候補（並列調査対象）が3つ以上ある
2. 仮説間に依存関係がない（独立して調査可能）

- **すべてYES** → Agent toolで並列調査
- **いずれかNO** → 単一セッションで分析続行

### Agent tool呼び出しパターン

調査は読み取り専用のため`isolation: worktree`は不要。1つのメッセージで複数のAgent toolを同時に呼び出す。

```text
【Agent tool 呼び出し1】
  subagent_type: general-purpose
  prompt: |
    以下の仮説について調査してください。

    問題: [問題の概要]
    仮説1: データフロー・状態管理の問題
    調査対象: src/state/, src/hooks/

    調査手順:
    1. 関連コードを読み取り
    2. データフローを追跡
    3. 問題の有無を判定
    4. 証拠（該当コード箇所）を収集

    結果を以下の形式で報告:
    - 仮説の支持/棄却
    - 根拠（具体的なコード箇所と説明）
    - 追加発見事項

【Agent tool 呼び出し2】
  subagent_type: general-purpose
  prompt: |
    仮説2: API通信・認証の問題
    調査対象: src/api/, src/auth/
    ...（同様の構造）

【Agent tool 呼び出し3】
  subagent_type: general-purpose
  prompt: |
    仮説3: 非同期処理・タイミングの問題
    調査対象: src/services/, src/workers/
    ...（同様の構造）
```

**注意**: 相互反証が特に重要な場合は、エージェントチーム（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`）の使用を検討。メンバー間で直接発見を共有・反証できる。

**並列処理パターンの詳細**: `sdd-documentation/references/agent_teams_guide_ja.md`

### 並列調査後のフロー

```text
1. 各サブエージェントの調査結果を統合
2. 最も有力な根本原因を特定
3. 通常のフローに戻る:
   - 仕様との照合
   - 修正方針の策定
   - ★ ユーザー承認 ★
   - タスク分割
```

## TodoWrite連携

### 修正タスクの同期

sdd-troubleshootingで修正タスクをdocs/sdd/tasks/に追加した場合、TodoWriteにも同期します:

```text
1. 修正タスクをdocs/sdd/tasks/に作成
2. TodoWriteに修正タスクをpendingで追加:
   todos = [
     ...既存のtodo...,
     { content: "[TASK-XXX] [BugFix] 問題の修正", status: "pending", activeForm: "[TASK-XXX] 問題を修正中" }
   ]
```

### タスクIDの命名

修正タスクには`[BugFix]`プレフィックスを付けてTodoWriteに登録し、通常タスクと区別:

```text
[TASK-010] [BugFix] 認証トークンの有効期限チェック修正
```

## リソース

| リソース | 内容 |
|---------|------|
| [references/analysis_guide_ja.md](references/analysis_guide_ja.md) | 分析テクニック、問題分類、チェックリスト |
| [assets/templates/analysis_report_template_ja.md](assets/templates/analysis_report_template_ja.md) | 分析レポートテンプレート |
| [assets/templates/bugfix_task_template_ja.md](assets/templates/bugfix_task_template_ja.md) | バグ修正タスクテンプレート |
