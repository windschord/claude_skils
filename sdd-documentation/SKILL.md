---
name: sdd-documentation
description: ソフトウェア設計ドキュメント（SDD）を作成・管理・実装します。requirements/、design/、tasks/の作成から、タスク実行・逆順レビューまでの全工程を統括します。SDDワークフロー全体の管理が必要な場合に使用してください。
---

# SDD ドキュメンテーションスキル

ソフトウェア設計ドキュメント（SDD）の作成・管理・実装を統括するオーケストレータースキルです。

## 概要

このスキルは、以下の4つのサブスキルを連携させて、要件定義から実装までの全工程を管理します：

| サブスキル | 役割 | 成果物 |
|-----------|------|--------|
| **requirements-defining** | EARS記法による要件定義 | docs/requirements/ |
| **software-designing** | 技術アーキテクチャ設計 | docs/design/ |
| **task-planning** | AIエージェント向けタスク分解 | docs/tasks/ |
| **task-executing** | タスク実行・逆順レビュー | 実装コード |

## ドキュメント構成

```
docs/
├── requirements/           # 要件定義
│   ├── index.md           # 目次・概要
│   ├── stories/           # ユーザーストーリー詳細
│   │   └── US-XXX.md
│   └── nfr/               # 非機能要件
│       └── performance.md
├── design/                # 設計
│   ├── index.md           # 目次・アーキテクチャ概要
│   ├── components/        # コンポーネント詳細
│   │   └── [name].md
│   ├── api/               # API設計詳細
│   │   └── [name].md
│   ├── database/          # データベーススキーマ
│   │   └── schema.md
│   └── decisions/         # 技術的決定事項
│       └── DEC-XXX.md
└── tasks/                 # タスク管理
    ├── index.md           # 目次・進捗サマリ
    └── phase-N/           # フェーズ別タスク
        └── TASK-XXX.md
```

## このスキルを使用する場面

### 一括初期化
- 新規プロジェクトでSDDドキュメント一式が必要な場合
- docsディレクトリと3つのドキュメントカテゴリを作成したい場合

### 全体管理
- 3つのドキュメント間の整合性を確認したい場合
- 逆順レビュー（タスク → 設計 → 要件）を実施したい場合
- ドキュメント全体の品質をチェックしたい場合

### 実装フェーズ
- docs/tasks/に沿って実装を行う場合
- 実装後の逆順レビュー（実装→タスク→設計→要件）が必要な場合
- タスクのステータス管理とGitコミットを統一したい場合

### 個別作業が必要な場合
特定の工程のみ実施する場合は、各サブスキルを直接使用してください：
- 要件定義のみ → `requirements-defining`
- 設計のみ → `software-designing`
- タスク計画のみ → `task-planning`
- 実装のみ → `task-executing`

## ワークフロー

### 標準フロー（推奨）

```text
┌─────────────────────────────────────────────────────────────┐
│                   sdd-documentation                          │
│                    （このスキル）                             │
│                                                              │
│  1. 初期化                                                   │
│     └─ docs/ディレクトリ構造を作成                          │
│                          ↓                                   │
│  2. requirements-defining                                    │
│     └─ EARS記法で要件定義 → docs/requirements/               │
│                          ↓                                   │
│  3. software-designing                                       │
│     └─ 技術設計を文書化 → docs/design/                       │
│                          ↓                                   │
│  4. task-planning                                            │
│     └─ タスク分解 → docs/tasks/                              │
│                          ↓                                   │
│  5. ドキュメント逆順レビュー                                 │
│     └─ tasks/ → design/ → requirements/ の整合性確認        │
│                          ↓                                   │
│  6. task-executing                                           │
│     └─ タスク実行 → 実装コード                               │
│     └─ ステータス更新 → tasks/index.md                       │
│     └─ コミットテンプレート → Git                            │
│                          ↓                                   │
│  7. 実装逆順レビュー                                         │
│     └─ 実装 → tasks/ → design/ → requirements/ の整合性確認 │
│                          ↓                                   │
│  8. 完了                                                     │
└─────────────────────────────────────────────────────────────┘
```

### 各ステップでのユーザー確認

```text
docs/requirements/ 作成完了
  ↓
ユーザー確認・承認
  ↓
docs/design/ 作成完了
  ↓
ユーザー確認・承認
  ↓
docs/tasks/ 作成完了
  ↓
ユーザー確認・承認
  ↓
ドキュメント逆順レビュー
  ↓
タスク実行開始
  ↓
各タスク完了ごとにコミット・ステータス更新
  ↓
実装逆順レビュー
  ↓
完了
```

## ドキュメント初期化

「docsディレクトリを初期化してください」「SDDドキュメントを作成してください」と依頼されたら：

1. **docsディレクトリ構造の作成**
   ```
   docs/
   ├── requirements/
   │   ├── stories/
   │   └── nfr/
   ├── design/
   │   ├── components/
   │   ├── api/
   │   ├── database/
   │   └── decisions/
   └── tasks/
       ├── phase-1/
       └── phase-2/
   ```

2. **requirements/index.md（要件定義書目次）の作成**
   - テンプレート: `requirements-defining/assets/templates/requirements_index_template_ja.md`

3. **design/index.md（設計書目次）の作成**
   - テンプレート: `software-designing/assets/templates/design_index_template_ja.md`

4. **tasks/index.md（タスク管理書目次）の作成**
   - テンプレート: `task-planning/assets/templates/tasks_index_template_ja.md`

## 逆順レビュープロセス

### レビューの流れ

```text
docs/tasks/ → docs/design/ → docs/requirements/
```

### ステップ1: タスク → 設計の整合性チェック

| チェック項目 | 確認内容 |
|-------------|---------|
| コンポーネント対応 | タスクが参照するコンポーネントはdesign/components/に定義されているか |
| API対応 | タスクで実装するAPIはdesign/api/と一致しているか |
| データモデル対応 | タスクで使用するデータ構造はdesign/database/と一致しているか |
| 技術スタック | タスクで使用する技術はdesign/decisions/と一致しているか |

### ステップ2: 設計 → 要件の整合性チェック

| チェック項目 | 確認内容 |
|-------------|---------|
| 機能カバレッジ | すべての要件（REQ-XXX）に対応する設計要素があるか |
| 非機能要件対応 | NFR-XXXの要件が設計に反映されているか |
| 過剰設計チェック | requirements/にない機能が設計に含まれていないか |

### 不整合発見時の報告

```text
ドキュメントの整合性チェックで以下の不整合を発見しました：

【タスク → 設計の不整合】
1. tasks/phase-2/TASK-003.mdで「PaymentService」を実装するとありますが、
   design/components/にPaymentServiceの定義がありません。

【設計 → 要件の不整合】
2. design/components/に「通知機能」がありますが、
   requirements/stories/に対応する要件がありません。

【過不足】
3. REQ-005（レポート出力機能）に対応するタスクがありません。

これらについて確認させてください：
1. PaymentServiceの設計を追加しますか？
2. 通知機能は必要ですか？
3. REQ-005のタスクを追加しますか？
```

## 検証チェックリスト

### 全体チェック
- [ ] docs/ディレクトリ構造が存在する
- [ ] requirements/index.md、design/index.md、tasks/index.mdが存在する
- [ ] 3ドキュメント間の整合性が取れている
- [ ] 逆順レビューが完了している

### 要件定義書
- [ ] ユーザーストーリーが明確に定義されている
- [ ] すべての要件がEARS記法に従っている
- [ ] 要件IDが一意である（REQ-XXX、NFR-XXX）
- [ ] 各要件がテスト可能である

### 設計書
- [ ] アーキテクチャ概要が記載されている
- [ ] 主要コンポーネントが定義されている
- [ ] 技術的決定事項と根拠が記載されている
- [ ] 情報の明確性チェックが完了している

### タスク管理書
- [ ] タスクが適切な粒度に分解されている（20-40分程度）
- [ ] 各タスクに受入基準がある
- [ ] TDD手順が含まれている
- [ ] 推測に基づく実装指示が含まれていない

## EARS記法クイックリファレンス

| パターン | 形式 | 使用場面 |
|---------|------|----------|
| 基本 | `システムは〜しなければならない` | 常時適用される要件 |
| イベント | `〜の時、システムは〜しなければならない` | イベント駆動要件 |
| 条件 | `もし〜ならば、システムは〜しなければならない` | 状態依存要件 |
| 継続 | `〜の間、システムは〜しなければならない` | 継続的要件 |
| 場所 | `〜において、システムは〜しなければならない` | コンテキスト固有要件 |

## ユーザーとの対話ガイドライン

### 情報分類プロセス

すべてのドキュメント作成において：

1. **明示された情報**: ユーザーが明確に述べた要件、仕様、制約
2. **不明な情報**: 推測が必要な項目（「おそらく〜」は不明として扱う）

### 確認の形式

```text
ドキュメント作成の前に、以下の点を確認させてください：

【明示された情報】
- [ユーザーから明示的に指定された内容]

【不明/要確認の情報】
1. [項目1]: [選択肢A] / [選択肢B] / その他
2. [項目2]: [具体的な質問]

上記の不明点について教えていただけますか？
```

## サブスキルへのリンク

- 要件定義: `requirements-defining/SKILL.md`
- 設計: `software-designing/SKILL.md`
- タスク計画: `task-planning/SKILL.md`
- タスク実行: `task-executing/SKILL.md`

## Gitコミットテンプレート

task-executingスキルで使用するコミットテンプレート：

### 実装コミット
```text
[タスクID] タスクタイトル

## 実装内容
- 実装した機能の説明

## 受入基準の達成状況
- [x] 基準1
- [x] 基準2

## 関連ドキュメント
- docs/tasks/[phase]/TASK-XXX.md: タスク詳細
- docs/design/components/[name].md: 関連コンポーネント
- docs/requirements/stories/US-XXX.md: 関連要件

## テスト
- テスト実行結果
```

### ステータス更新コミット
```text
Update tasks.md: タスクID completed

タスクタイトルを完了としてマーク。
完了サマリー: [1行の要約]
```

## リソース

- ワークフローガイド: `references/workflow_guide_ja.md`
- 各サブスキルのテンプレート・リファレンスは各スキルディレクトリを参照
