---
name: software-designing
description: 【非推奨】設計書を永続化しない運用へ移行したため非推奨。設計は実装時にPR本文とGitHubコメントへ記載し、要求の管理は requirement-management を使用すること。既存の docs/sdd/design/ を保守・参照する場合にのみ使用する。アーキテクチャ設計、コンポーネント定義、API設計、データベーススキーマのMarkdown文書を作成・編集する。Do NOT use for 新規プロジェクトの設計（設計はPR本文に記載すること）。
metadata:
  version: "1.0.0"
---

# 設計スキル（非推奨）

> **⚠️ このスキルは非推奨です。**
>
> 設計書を永続化しない運用へ移行しました。設計書は書いた瞬間から実装とずれ始め、ずれた設計書は整合性チェックの対象を増やすだけになるためです。
>
> | | 非推奨（本スキル） | 移行先 |
> |---|---|---|
> | 設計の記録先 | `docs/sdd/design/`（永続化） | PR本文とGitHubコメント（永続化しない） |
> | 要求との紐付け | ドキュメント間の相互リンク | 要求の `verification` とPRのURL（`design_refs`） |
> | 要求の管理 | requirements-defining | `requirement-management` |
>
> 運用の詳細は `sdd/requirement-management/references/design_in_pr_ja.md`、移行手順は同 `references/migration_from_sdd_ja.md` を参照してください。
> 既存の `docs/sdd/design/` を保守・参照する場合にのみ、以下の手順を使用します。

技術アーキテクチャ、コンポーネント設計、API設計、データベーススキーマを文書化する設計書を作成します。

## 概要

このスキルは、以下の成果物を作成・管理します：
- **docs/sdd/design/index.md**: 設計概要（目次）
- **docs/sdd/design/components/*.md**: コンポーネント詳細
- **docs/sdd/design/api/*.md**: API設計詳細
- **docs/sdd/design/database/schema.md**: データベーススキーマ
- **docs/sdd/design/decisions/DEC-XXX.md**: 技術的決定事項

## ドキュメント構成

```text
docs/sdd/design/
├── index.md                 # 目次・アーキテクチャ概要
├── components/
│   ├── component-a.md       # コンポーネント詳細
│   └── component-b.md
├── api/
│   ├── users.md             # API設計詳細
│   └── items.md
├── database/
│   └── schema.md            # データベーススキーマ
└── decisions/
    ├── DEC-001.md           # 技術的決定事項
    └── DEC-002.md
```

## このスキルを使用する場面

### 新規作成時
- 技術アーキテクチャを文書化したい場合
- コンポーネント設計を明確にしたい場合
- API設計を定義したい場合
- データベーススキーマを設計したい場合

### 既存ドキュメントの修正時
- docs/sdd/design/の設計内容を更新・変更する場合
- 新しいコンポーネントを追加する場合

## 前提条件

### requirements/との連携
docs/sdd/requirements/が存在する場合：
1. 要件を読み込み、設計との整合性を確認
2. すべての要件（REQ-XXX）に対応する設計要素があるか確認
3. 要件にない機能が設計に含まれていないか確認

## 設計原則

### コンポーネント設計
1. **単一責任の原則**: 各コンポーネントは1つの明確な目的を持つ
2. **疎結合**: コンポーネント間の依存関係を最小限に
3. **高凝集**: 関連する機能を同じコンポーネントに
4. **インターフェース定義**: 明確な入出力を定義

### API設計
- RESTful原則に従う
- 適切なHTTPステータスコードを使用
- バージョニング戦略を定義
- エラーレスポンスの一貫性

### データベース設計
- 正規化と非正規化のバランス
- インデックス戦略
- トランザクション境界

## ワークフロー

1. **要件確認**: docs/sdd/requirements/が存在すれば内容を確認
2. **情報分類**: 明示された情報と不明な情報を分類
3. **不明点確認**: 必要な情報をユーザーに確認
4. **ディレクトリ作成**: `docs/sdd/design/` 以下のサブディレクトリを作成
5. **各ドキュメント作成**: テンプレートを使用
6. **整合性確認**: requirements/との整合性をチェック
7. **ユーザー確認**: 承認を得て完了

## 検証チェックリスト

- [ ] アーキテクチャ概要が記載されている
- [ ] 主要コンポーネントが定義されている
- [ ] 技術的決定事項と根拠が記載されている
- [ ] 情報の明確性チェックが完了している
- [ ] requirements/の全要件に対応する設計要素がある
- [ ] CI/CD設計が含まれている
- [ ] 品質基準が定義されている（カバレッジ80%、ミューテーションスコア85%、Linter、複雑性）

## 要件との整合性チェック

docs/sdd/requirements/が存在する場合、以下を確認：

| チェック項目 | 確認内容 |
|-------------|---------|
| 機能カバレッジ | すべての要件（REQ-XXX）に対応する設計要素があるか |
| 非機能要件対応 | NFR-XXXの要件が設計に反映されているか |
| 過剰設計チェック | requirements/にない機能が設計に含まれていないか |

## ユーザーとの対話ガイドライン

### 確認が必要な場面
- アーキテクチャパターンの選択
- 技術スタックの選定
- データモデルの構造
- 外部サービスとの連携方法

### 推奨度付き選択肢の提示

```text
技術スタックについて確認させてください：

A) Next.js + TypeScript
   推奨理由：モダンで型安全、SSR/SSG対応

B) React + JavaScript
   推奨理由：シンプルで導入が容易

どれを選択しますか？
```

## 後続スキルとの連携

docs/sdd/design/の作成完了後：
- **task-planning**: design/を基にタスクを分解

task-planningスキルで逆順レビュー（タスク → 要求）が行われます。設計は逆順レビューの対象外です（PR本文の設計ノートと実装を突き合わせます）。

## リソース

### テンプレート
- 目次テンプレート: `assets/templates/design_index_template_ja.md`
- コンポーネントテンプレート: `assets/templates/component_template_ja.md`
- APIテンプレート: `assets/templates/api_template_ja.md`
- データベーステンプレート: `assets/templates/database_template_ja.md`
- 技術的決定テンプレート: `assets/templates/decision_template_ja.md`

### リファレンス
- 設計パターン: `references/design_patterns_ja.md`
- CI/CDガイド: `references/cicd_guide_ja.md`
- EARS記法（要件参照用）: `references/ears_notation_ja.md`

### 命名規則

| ファイル種別 | 命名規則 | 例 |
|-------------|---------|-----|
| コンポーネント | ケバブケース | `user-service.md`, `auth-handler.md` |
| API | リソース名 | `users.md`, `items.md` |
| 技術的決定 | `DEC-XXX.md` | `DEC-001.md`, `DEC-002.md` |
