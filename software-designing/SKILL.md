---
name: software-designing
description: 技術設計書を作成・編集する。「アーキテクチャを設計して」「コンポーネント設計して」「API設計して」「データベーススキーマを設計して」等の依頼時に使用。requirements/が存在する場合は整合性を確認する。docs/sdd/design/に設計ドキュメントを出力する。
metadata:
  version: "1.0.0"
---

# 設計スキル

技術アーキテクチャ、コンポーネント設計、API設計、データベーススキーマを文書化する設計書を作成する。

## 成果物

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

## 前提条件

docs/sdd/requirements/が存在する場合:
1. 要件を読み込み、設計との整合性を確認
2. すべての要件（REQ-XXX）に対応する設計要素があるか確認
3. 要件にない機能が設計に含まれていないか確認（過剰設計防止）

## ワークフロー

1. **要件確認**: docs/sdd/requirements/が存在すれば内容を確認
2. **情報分類**: 明示された情報と不明な情報を分類。不明点があればユーザーに確認
3. **ディレクトリ作成**: `docs/sdd/design/` 以下のサブディレクトリを作成
4. **各ドキュメント作成**: テンプレートを使用して設計書を作成
5. **整合性確認**: requirements/との整合性をチェック
6. **ユーザー確認**: 承認を得て完了

## 要件との整合性チェック

| チェック項目 | 確認内容 |
|-------------|---------|
| 機能カバレッジ | すべてのREQ-XXXに対応する設計要素があるか |
| 非機能要件対応 | NFR-XXXが設計に反映されているか |
| 過剰設計チェック | requirements/にない機能が設計に含まれていないか |

## ユーザーとの対話

確認が必要な場面:
- アーキテクチャパターンの選択
- 技術スタックの選定
- データモデルの構造
- 外部サービスとの連携方法

選択肢を提示する際は推奨理由を付ける。

## 検証チェックリスト

- [ ] アーキテクチャ概要が記載されている
- [ ] 主要コンポーネントが定義されている
- [ ] 技術的決定事項と根拠が記載されている
- [ ] requirements/の全要件に対応する設計要素がある
- [ ] CI/CD設計が含まれている
- [ ] 品質基準が定義されている（カバレッジ80%、Linter、複雑性）

## 後続スキルとの連携

作成完了後、task-planningで設計に基づきタスクを分解する。逆順レビュー（タスク → 設計 → 要件）で整合性が確認される。

## リソース

### テンプレート
- 目次: [assets/templates/design_index_template_ja.md](assets/templates/design_index_template_ja.md)
- コンポーネント: [assets/templates/component_template_ja.md](assets/templates/component_template_ja.md)
- API: [assets/templates/api_template_ja.md](assets/templates/api_template_ja.md)
- データベース: [assets/templates/database_template_ja.md](assets/templates/database_template_ja.md)
- 技術的決定: [assets/templates/decision_template_ja.md](assets/templates/decision_template_ja.md)

### リファレンス
- 設計パターン: [references/design_patterns_ja.md](references/design_patterns_ja.md)
- CI/CDガイド: [references/cicd_guide_ja.md](references/cicd_guide_ja.md)
- EARS記法（要件参照用）: [references/ears_notation_ja.md](references/ears_notation_ja.md)

### 命名規則

| ファイル種別 | 命名規則 | 例 |
|-------------|---------|-----|
| コンポーネント | ケバブケース | `user-service.md` |
| API | リソース名 | `users.md` |
| 技術的決定 | `DEC-XXX.md` | `DEC-001.md` |

### リンク形式

index.mdでは `[詳細](components/component-a.md) @components/component-a.md` のようにマークダウン形式と@形式を併記する。
