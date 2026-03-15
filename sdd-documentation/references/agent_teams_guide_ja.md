# 並列処理ガイド（Agent tool活用）


<!-- TOC -->
## 目次

- [概要](#概要)
- [並列処理の2つの手段](#並列処理の2つの手段)
  - [Agent tool（推奨・標準）](#agent-tool推奨標準)
  - [エージェントチーム（補完的・オプション）](#エージェントチーム補完的オプション)
- [並列処理判定フローチャート（全スキル共通）](#並列処理判定フローチャート全スキル共通)
- [Agent tool vs エージェントチーム 比較](#agent-tool-vs-エージェントチーム-比較)
  - [各SDDフェーズでの推奨](#各sddフェーズでの推奨)
- [Agent toolによる並列実行パターン](#agent-toolによる並列実行パターン)
  - [基本パターン: isolation: worktree](#基本パターン-isolation-worktree)
  - [基本パターン: 読み取り専用（worktreeなし）](#基本パターン-読み取り専用worktreeなし)
- [SDDワークフローでの活用マップ](#sddワークフローでの活用マップ)
- [パターン1: 並列タスク実行](#パターン1-並列タスク実行)
  - [バックグラウンド実行の活用](#バックグラウンド実行の活用)
- [パターン2: 並列レビュー](#パターン2-並列レビュー)
- [パターン3: 並列仮説調査（トラブルシューティング）](#パターン3-並列仮説調査トラブルシューティング)
- [パターン4: 並列ドキュメントチェック（フルスキャン）](#パターン4-並列ドキュメントチェックフルスキャン)
- [パターン5: Jules CLI + Agent tool ハイブリッド実行](#パターン5-jules-cli--agent-tool-ハイブリッド実行)
- [並列処理のベストプラクティス](#並列処理のベストプラクティス)
  - [1. プロンプトに十分なコンテキストを含める](#1-プロンプトに十分なコンテキストを含める)
  - [2. worktree使用の判断](#2-worktree使用の判断)
  - [3. 結果統合のフロー](#3-結果統合のフロー)
  - [4. バックグラウンド実行の活用](#4-バックグラウンド実行の活用)
  - [5. エラーハンドリング](#5-エラーハンドリング)
- [並列処理を使用しない場合](#並列処理を使用しない場合)
- [エージェントチームの利用（Agent toolで不十分な場合のみ）](#エージェントチームの利用agent-toolで不十分な場合のみ)
- [トラブルシューティング](#トラブルシューティング)
  - [worktreeの変更が統合できない](#worktreeの変更が統合できない)
  - [サブエージェントが期待した出力を返さない](#サブエージェントが期待した出力を返さない)
  - [並列実行で一部のタスクのみ失敗](#並列実行で一部のタスクのみ失敗)
<!-- /TOC -->

## 概要

このガイドは、SDDワークフローにおける並列処理の活用方法を説明します。**Agent tool**（`isolation: worktree`オプション付き）を主要な並列実行手段とし、独立したタスクを複数のサブエージェントが同時に処理することで開発効率を向上させます。

**原則: 条件を満たす場合は並列処理を積極的に使用する。「使えたら使う」ではなく「条件を満たせば使う」が原則。**

## 並列処理の2つの手段

### Agent tool（推奨・標準）

Claude Codeの標準機能であるAgent toolを使用し、サブエージェントを並列起動する手法。

- **常に利用可能**（実験的機能フラグ不要）
- `isolation: worktree` で各サブエージェントが独立したgit worktreeで動作し、**並行作業中の上書き衝突を防止**（統合時のマージコンフリクトは手動解決が必要）
- 1つのメッセージで複数のAgent toolを呼び出すことで並列実行
- 各サブエージェントは独自のコンテキストウィンドウを持ち、メインセッションを圧迫しない

### エージェントチーム（補完的・オプション）

メンバー間の議論・相互反証が必要な場合にのみ使用する従来手法。

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` の有効化が必要
- メンバー間で直接メッセージ送信が可能（相互反証に有効）
- オーバーヘッドが大きいため、議論が不要な場合はAgent toolを優先

## 並列処理判定フローチャート（全スキル共通）

```text
┌─────────────────────────────────────────────────────┐
│            並列処理判定                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Q1. 並列実行可能な独立したタスク/調査が2つ以上？     │
│      YES → Q2へ                                     │
│      NO  → 順次実行                                  │
│                                                     │
│  Q2. タスク間に依存関係がない？                       │
│      YES → Q3へ                                     │
│      NO  → 順次実行                                  │
│                                                     │
│  Q3. メンバー間の議論・相互反証が必要？               │
│      YES → エージェントチーム                         │
│      NO  → Q4へ                                      │
│                                                     │
│  Q4. ファイル変更を伴うか？                           │
│      YES → Agent tool（isolation: worktree）         │
│      NO（読み取り専用）→ Agent tool（worktreeなし）   │
│                                                     │
│  補足:                                               │
│  ・2タスクでもAgent toolなら低コストで並列化可能      │
│  ・3タスク以上は積極的に並列化すること                │
│  ・worktreeにより並行作業中の上書き衝突を防止できる   │
│    ただし統合時にマージコンフリクトが発生し得る       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Agent tool vs エージェントチーム 比較

| 基準 | Agent tool（推奨） | エージェントチーム |
|------|-------------------|-------------------|
| **利用条件** | 常に利用可能 | 実験的フラグ必要 |
| **ファイル競合** | worktreeで上書き衝突を防止（統合時コンフリクト可能） | 手動でファイル分離が必要 |
| **並列起動** | 1メッセージで複数起動 | チーム作成が必要 |
| **コンテキスト** | 各自独立 | 各自独立 + メンバー間通信 |
| **通信** | メインに結果を返すのみ | メンバー間で直接通信可能 |
| **オーバーヘッド** | 低い | 高い |
| **最適な用途** | 独立した並列タスク全般 | 議論・協力が必要な複雑な調査 |

### 各SDDフェーズでの推奨

| フェーズ | 推奨方式 | 理由 |
|---------|---------|------|
| task-executing（2タスク以上） | Agent tool + worktree | 各タスクが独立したworktreeで安全に並列実装 |
| task-executing（Jules利用可能） | Jules + Agent tool ハイブリッド | 定型タスクをJulesに、複雑タスクをAgent toolに |
| sdd-troubleshooting（3仮説以上） | Agent tool（読み取り専用調査） | 調査は読み取りのみでworktree不要。相互反証が必要ならエージェントチーム |
| sdd-document-management（フルスキャン） | Agent tool + worktree | 5機能の独立した並列チェック |
| 逆順レビュー（3層チェック） | Agent tool（読み取り専用） | レビューは読み取りのみ |
| 要件定義・設計 | 単一セッション | ユーザー対話が中心 |

## Agent toolによる並列実行パターン

### 基本パターン: isolation: worktree

各サブエージェントがgit worktree（独立した作業ツリー）で動作するため、並行作業中の上書き衝突を防止できる。ただし統合時に同じファイルの同じ箇所を変更した場合はマージコンフリクトが発生するため、手動解決が必要。

```text
メインセッション
├── Agent tool (isolation: worktree) → サブエージェント1: TASK-001
├── Agent tool (isolation: worktree) → サブエージェント2: TASK-002
└── Agent tool (isolation: worktree) → サブエージェント3: TASK-003
      ↓ 各worktreeで独立して実装
      ↓ 完了後、変更はworktreeブランチに保存
メインセッション: 結果を統合・コミット
```

### 基本パターン: 読み取り専用（worktreeなし）

調査やレビューなど、ファイルを変更しない作業はworktreeなしで起動し、オーバーヘッドを削減。

```text
メインセッション
├── Agent tool → レビュアー1: requirements ↔ design 整合性
├── Agent tool → レビュアー2: design ↔ tasks 整合性
└── Agent tool → レビュアー3: implementation ↔ docs 同期
      ↓ 各自が読み取り専用で分析
メインセッション: 結果を統合・報告
```

## SDDワークフローでの活用マップ

```text
SDDフェーズ          並列処理          条件・トリガー                    方式
──────────────────────────────────────────────────────────────────────────
1. 要件定義          不要               ユーザー対話が中心                -
2. 設計              不要               ユーザー対話が中心                -
3. タスク計画        不要（設計時考慮）  並列実行を前提にタスク設計        -
4. 逆順レビュー      条件付き           3層すべて存在する場合             Agent tool
5. タスク実行        条件付き必須        並列可能タスク2つ以上の場合       Agent tool + worktree
6. トラブルシュート   条件付き           原因候補3つ以上の場合             Agent tool
7. ドキュメント管理   フルスキャン時     フルスキャン選択時                Agent tool + worktree
```

## パターン1: 並列タスク実行

**使用フェーズ**: タスク実行（task-executing）

**条件**:
- 2つ以上の独立したタスク
- タスク間に依存関係なし
- 同一ファイルを変更する可能性が低い（高い場合は統合時コンフリクト多発のため順次実行を推奨）

**Agent tool呼び出しパターン**:

1つのメッセージ内で複数のAgent toolを同時に呼び出すことで並列実行する。

```text
【Agent tool 呼び出し1】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    以下のSDDタスクを実装してください。

    タスクファイル: docs/sdd/tasks/phase-1/TASK-001.md
    [タスクファイルの完全な内容をここに貼り付け]

    参照設計: docs/sdd/design/components/auth-service.md
    参照要件: docs/sdd/requirements/stories/US-001.md

    実装ルール:
    - タスクファイルのTDD手順に従う
    - 受入基準をすべて満たす
    - テストを実装し、すべて通過させる
    - 完了後にコミットを作成（メッセージ: feat(auth): implement login endpoint [TASK-001]）

【Agent tool 呼び出し2】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    以下のSDDタスクを実装してください。

    タスクファイル: docs/sdd/tasks/phase-1/TASK-002.md
    [タスクファイルの完全な内容をここに貼り付け]
    ...（同様の構造）

【Agent tool 呼び出し3】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    以下のSDDタスクを実装してください。

    タスクファイル: docs/sdd/tasks/phase-1/TASK-003.md
    [タスクファイルの完全な内容をここに貼り付け]
    ...（同様の構造）
```

**結果の統合手順**:

```text
1. 各サブエージェントの完了を確認
2. worktreeの変更をメインブランチにマージ
   - 変更があった場合、worktreeのブランチが返される
   - git merge または cherry-pick で統合
3. テスト全体を再実行して統合後の動作を確認
4. docs/sdd/tasks/index.md のステータスを一括更新
5. TodoWriteを同期
6. 逆順レビューを実施
```

### バックグラウンド実行の活用

長時間かかるタスクは `run_in_background: true` で起動し、他のタスクと並行して進行させる。

```text
【Agent tool 呼び出し（バックグラウンド）】
  subagent_type: general-purpose
  isolation: worktree
  run_in_background: true
  prompt: |
    以下のSDDタスクを実装してください...
```

バックグラウンドエージェントは完了時に自動通知されるため、ポーリング不要。

## パターン2: 並列レビュー

**使用フェーズ**: 逆順レビュー

**条件**:
- ドキュメントが3層（requirements/design/tasks）すべて存在
- 実装コードが存在する場合は実装同期チェックも追加

**Agent tool呼び出しパターン（読み取り専用、worktreeなし）**:

```text
【Agent tool 呼び出し1】
  subagent_type: general-purpose
  prompt: |
    以下の2つのドキュメント群の整合性をチェックしてください。

    チェック対象:
    - docs/sdd/requirements/ 配下の全ファイル
    - docs/sdd/design/ 配下の全ファイル

    チェック項目:
    - すべての要件（REQ-XXX）に対応する設計要素があるか
    - 設計に要件にない機能（過剰設計）がないか
    - 用語の一貫性

    結果を以下の形式で報告:
    - 不整合リスト（重要度: 高/中/低）
    - 各不整合の詳細と修正提案

【Agent tool 呼び出し2】
  subagent_type: general-purpose
  prompt: |
    以下の2つのドキュメント群の整合性をチェックしてください。

    チェック対象:
    - docs/sdd/design/ 配下の全ファイル
    - docs/sdd/tasks/ 配下の全ファイル

    チェック項目:
    - すべての設計要素に対応するタスクがあるか
    - タスクに設計にない実装が含まれていないか
    - 技術スタック・API仕様の一致

    結果を同形式で報告。

【Agent tool 呼び出し3】（実装コードが存在する場合のみ）
  subagent_type: general-purpose
  prompt: |
    実装コードとドキュメントの同期状態をチェックしてください。

    チェック対象:
    - src/ 配下の実装コード
    - docs/sdd/design/ の設計仕様
    - docs/sdd/tasks/ のタスク仕様

    チェック項目:
    - API実装がAPI設計と一致するか
    - データモデルがスキーマ定義と一致するか
    - コンポーネントの公開インターフェースが設計と一致するか
```

## パターン3: 並列仮説調査（トラブルシューティング）

**使用フェーズ**: トラブルシューティング（sdd-troubleshooting）

**条件**:
- 原因候補が3つ以上
- 各仮説の調査が独立して実行可能

**方式の選択**:
- 調査のみ（コード変更なし）→ Agent tool（worktreeなし）
- 相互反証が重要 → エージェントチーム（メンバー間通信可能）

**Agent tool呼び出しパターン（読み取り専用）**:

```text
【Agent tool 呼び出し1】
  subagent_type: general-purpose
  prompt: |
    以下の仮説について調査してください。

    問題: [問題の概要]
    仮説1: データフロー・状態管理の問題

    調査対象ファイル: src/state/, src/hooks/
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

## パターン4: 並列ドキュメントチェック（フルスキャン）

**使用フェーズ**: ドキュメント管理（sdd-document-management）フルスキャン時

**Agent tool呼び出しパターン（レポート作成 → worktreeあり）**:

```text
【Agent tool 呼び出し1】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    SDDドキュメントの整合性チェックを実行してください。

    チェック対象: docs/sdd/requirements/, docs/sdd/design/, docs/sdd/tasks/
    レポートテンプレート: sdd-document-management/assets/templates/consistency_report_template_ja.md

    手順:
    1. テンプレートを読み込む
    2. 3層間の整合性をチェック
    3. レポートを docs/sdd/reports/consistency/[今日の日付].md に作成

【Agent tool 呼び出し2】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    実装同期チェックを実行してください。

    チェック対象: src/ と docs/sdd/design/
    レポートテンプレート: sdd-document-management/assets/templates/sync_report_template_ja.md
    レポート出力先: docs/sdd/reports/sync/[今日の日付].md

【Agent tool 呼び出し3】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    アーカイブ対象を検出してください。

    チェック対象: docs/sdd/tasks/, docs/sdd/design/decisions/, docs/sdd/troubleshooting/
    レポートテンプレート: sdd-document-management/assets/templates/archive_report_template_ja.md
    レポート出力先: docs/sdd/reports/archive/[今日の日付].md

【Agent tool 呼び出し4】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    ファイル最適化分析を実行してください。

    チェック対象: docs/sdd/ 配下の全ファイル
    レポートテンプレート: sdd-document-management/assets/templates/optimize_report_template_ja.md
    レポート出力先: docs/sdd/reports/optimize/[今日の日付].md

【Agent tool 呼び出し5】
  subagent_type: general-purpose
  isolation: worktree
  prompt: |
    CLAUDE.mdと実装コードの乖離を検出してください。

    チェック対象: CLAUDE.md vs src/（実装コード）
    参照ガイド: sdd-document-management/references/claude_md_sync_ja.md
    レポート出力先: docs/sdd/reports/claude-md-sync/[今日の日付].md
```

**結果統合後のフロー**:

```text
1. 5つのサブエージェントの完了を確認
2. 各worktreeからレポートファイルを取得・統合
3. 統合サマリーを作成
4. ★ ユーザー承認 ★
5. 承認後、修正は順次実行（ファイル競合回避）
```

## パターン5: Jules CLI + Agent tool ハイブリッド実行

**使用フェーズ**: タスク実行（task-executing）でJules CLIが利用可能な場合

**条件**:
- Jules CLIが利用可能（`jules --version`で確認）
- 3つ以上の独立したタスク
- 開発ブランチが指定されている

**実行フロー**:

```text
メインセッション（オーケストレーター）
├── Jules依頼（非同期PR作成）:
│   ├── jules "TASK-001の依頼文" → 非同期でPR作成
│   ├── jules "TASK-002の依頼文" → 非同期でPR作成
│   └── jules "TASK-003の依頼文" → 非同期でPR作成
├── Agent tool (isolation: worktree) 並列実行:
│   ├── サブエージェント1: TASK-004（環境依存タスク）
│   └── サブエージェント2: TASK-005（複雑なリファクタリング）
└── 進捗管理:
    ├── jules list で定期確認
    ├── Agent toolの完了通知を受け取り
    ├── PRレビュー・マージ
    └── docs/sdd/tasks/ + TodoWrite 一括更新
```

**タスク割り当て判定基準**:

| 実行先 | 向いているタスク |
|--------|-----------------|
| **Jules** | 独立・定型的・明確な受入基準・標準パターン（CRUD、API、モデル定義） |
| **Agent tool + worktree** | 複雑なリファクタリング・環境依存・密結合な変更 |

**依存関係グループの順次進行**:

```text
グループA（並列: Jules-1, Jules-2, Agent tool-1, Agent tool-2）
  ↓ 全PRマージ + Agent完了 + worktree変更統合
開発ブランチを最新に更新（git pull）
  ↓
グループB（並列: Jules-3, Jules-4, Agent tool-3）
  ↓ 全PRマージ + Agent完了
逆順レビュー
```

## 並列処理のベストプラクティス

### 1. プロンプトに十分なコンテキストを含める

サブエージェントはメインセッションの会話履歴を引き継がないため、プロンプトに必要な情報をすべて含める:

```text
必須情報:
- タスクファイルの完全な内容（パスだけでなく中身）
- 参照すべき設計ドキュメントのパス
- 使用する技術スタック
- コーディング規約
- コミットメッセージの形式
- 受入基準の詳細
```

### 2. worktree使用の判断

| 作業内容 | worktree | 理由 |
|---------|---------|------|
| コード実装 | **必要** | ファイル変更が発生 |
| ドキュメント作成 | **必要** | ファイル作成が発生 |
| コードレビュー | 不要 | 読み取りのみ |
| 仮説調査 | 不要 | 読み取りのみ |
| テスト実行 | 状況による | テスト生成がある場合は必要 |

### 3. 結果統合のフロー

```text
Agent tool完了
  ↓
変更ありのworktree → ブランチ名が返される
  ↓
git merge <worktree-branch> でメインに統合
  ↓
コンフリクトがあれば手動解決
  ↓
統合テストを実行
  ↓
ステータス更新・TodoWrite同期
```

### 4. バックグラウンド実行の活用

```text
長時間タスク（例: 大規模テスト）:
  → run_in_background: true で起動
  → 完了時に自動通知される
  → ポーリング・sleep不要

短時間タスク（例: コードレビュー）:
  → フォアグラウンドで起動
  → 結果を待ってから次のステップへ
```

### 5. エラーハンドリング

```text
サブエージェントが失敗した場合:
1. 失敗した結果を確認
2. 原因を分析（プロンプト不足? コンフリクト? テスト失敗?）
3. 修正してリトライ（新しいAgent toolとして起動）
4. 他のサブエージェントの結果は有効なまま保持

worktreeマージでコンフリクト:
1. コンフリクト箇所を確認
2. 手動で解決（またはサブエージェントに依頼）
3. 解決後にテスト実行
```

## 並列処理を使用しない場合

以下の場合は順次実行を使用する:

| 状況 | 理由 | 代替手段 |
|------|------|---------|
| 1個のタスク | 並列化不要 | 単一Agent tool |
| 順序依存タスク | 前タスクの結果が次に必要 | 順次実行 |
| 要件定義・設計フェーズ | ユーザー対話が中心 | 単一セッション |
| Jules CLIのみで十分 | ローカル実行不要 | Jules CLIスキル単体 |

## エージェントチームの利用（Agent toolで不十分な場合のみ）

以下の場合はエージェントチーム（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`）を検討:

| 状況 | 理由 |
|------|------|
| トラブルシューティングで相互反証が必要 | メンバー間で発見を直接共有・議論できる |
| 複雑な統合作業でリアルタイム調整が必要 | メンバー間通信で即座に方針調整できる |

**注意**: エージェントチームはほとんどの場合、Agent toolで代替可能。メンバー間通信が真に必要な場合にのみ使用する。

## トラブルシューティング

### worktreeの変更が統合できない

1. コンフリクトの内容を確認: `git diff`
2. 手動でコンフリクトを解決
3. 必要に応じてサブエージェントに再実装を依頼

### サブエージェントが期待した出力を返さない

1. プロンプトの情報量を確認（タスクファイルの中身を含めているか）
2. 制約条件を明確にして再起動
3. Exploreエージェントで事前調査してからgeneral-purposeで実装

### 並列実行で一部のタスクのみ失敗

1. 成功したタスクの結果は先にマージ
2. 失敗タスクの原因を分析
3. 修正して個別にリトライ
