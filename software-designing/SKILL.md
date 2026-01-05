---
name: software-designing
description: 技術設計書を作成・編集します。アーキテクチャ設計、コンポーネント定義、API設計、データベーススキーマの文書化が必要な場合に使用してください。requirements/が存在する場合は整合性を確認します。
---

# 設計スキル

技術アーキテクチャ、コンポーネント設計、API設計、データベーススキーマを文書化する設計書を作成します。

## 概要

このスキルは、以下の成果物を作成・管理します：
- **docs/design/index.md**: 設計概要（目次）
- **docs/design/components/*.md**: コンポーネント詳細
- **docs/design/api/*.md**: API設計詳細
- **docs/design/database/schema.md**: データベーススキーマ
- **docs/design/decisions/DEC-XXX.md**: 技術的決定事項

## ドキュメント構成

```
docs/design/
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
- 技術的決定事項を記録したい場合

### 既存ドキュメントの修正時
- docs/design/の設計内容を更新・変更する場合
- 新しいコンポーネントを追加する場合
- API仕様を変更する場合
- アーキテクチャの見直しが必要な場合

## 前提条件

### requirements/との連携
docs/requirements/が存在する場合：
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
- ペイロードの検証とサニタイゼーション

### データベース設計
- 正規化と非正規化のバランス
- インデックス戦略
- トランザクション境界
- バックアップとリカバリ計画

## Mermaid図の活用

### コンポーネント図
```mermaid
graph TD
    A[コンポーネントA] --> B[コンポーネントB]
    B --> C[コンポーネントC]
```

### シーケンス図
```mermaid
sequenceDiagram
    participant ユーザー
    participant システム
    participant データベース

    ユーザー->>システム: リクエスト
    システム->>データベース: クエリ
    データベース-->>システム: レスポンス
    システム-->>ユーザー: 結果
```

## ワークフロー

### 新規作成フロー

1. **要件確認**: docs/requirements/が存在すれば内容を確認
2. **情報分類**: 明示された情報と不明な情報を分類
3. **不明点確認**: 必要な情報をユーザーに確認
4. **ディレクトリ作成**: `docs/design/` 以下のサブディレクトリを作成
5. **index.md作成**: 目次とアーキテクチャ概要を記述
6. **コンポーネント設計**: 各コンポーネントを `components/*.md` に記述
7. **API設計**: 各APIを `api/*.md` に記述
8. **データベース設計**: `database/schema.md` を作成
9. **技術的決定**: 重要な決定を `decisions/DEC-XXX.md` に記録
10. **index.md更新**: 作成した各ドキュメントへのリンクを追加
11. **整合性確認**: requirements/との整合性をチェック
12. **ユーザー確認**: 承認を得て完了

### コンポーネント追加フロー

1. **新規ファイル作成**: `components/[name].md` を作成
2. **コンポーネントテンプレートに従う**: 目的・責務・インターフェースを記述
3. **index.md更新**: コンポーネント一覧テーブルにリンクを追加
4. **関連ドキュメント更新**: 依存関係のあるコンポーネントに相互リンクを追加

## 検証チェックリスト

- [ ] アーキテクチャ概要が記載されている
- [ ] 主要コンポーネントが定義されている
- [ ] インターフェースが明確である
- [ ] 技術的決定事項と根拠が記載されている
- [ ] 必要に応じて図表が含まれている
- [ ] 情報の明確性チェックが完了している
- [ ] 不明/要確認の情報がすべて解消されている
- [ ] requirements/の全要件に対応する設計要素がある
- [ ] CI/CD設計が含まれている（品質ゲート、GitHub Actions）
- [ ] 品質基準が定義されている（カバレッジ80%、Linter、複雑性）

## 要件との整合性チェック

docs/requirements/が存在する場合、以下を確認：

| チェック項目 | 確認内容 |
|-------------|---------|
| 機能カバレッジ | すべての要件（REQ-XXX）に対応する設計要素があるか |
| 非機能要件対応 | NFR-XXXの要件が設計に反映されているか |
| 過剰設計チェック | requirements/にない機能が設計に含まれていないか |

### 不整合発見時

```text
設計と要件の整合性チェックで以下の不整合を発見しました：

【設計 → 要件の不整合】
1. design/components/に「通知機能」がありますが、requirements/storiesに対応する要件がありません

【要件 → 設計の不整合】
2. REQ-005（レポート出力機能）に対応する設計がありません

これらについて確認させてください：
1. 通知機能は必要ですか？対応する要件を追加しますか？
2. REQ-005の設計を追加しますか？
```

## ユーザーとの対話ガイドライン

### 確認が必要な場面

- アーキテクチャパターンの選択
- 技術スタックの選定
- データモデルの構造
- 外部サービスとの連携方法
- セキュリティ・パフォーマンス要件の具体化

### 推奨度付き選択肢の提示

```text
技術スタックについて確認させてください：

A) Next.js + TypeScript
   推奨理由：モダンで型安全、SSR/SSG対応

B) React + JavaScript
   推奨理由：シンプルで導入が容易

C) Vue.js + TypeScript
   推奨理由：学習コストが低い

どれを選択しますか？
```

## CI/CD・品質基準の設計

### 必須品質基準

設計段階で以下の品質基準を定義し、GitHub Actionsで自動検証する：

| 項目 | 基準値 | ツール例 |
|------|--------|---------|
| テストカバレッジ | 80%以上 | Jest, pytest, go test |
| Linter | エラー0件 | ESLint, Ruff, golangci-lint |
| コード複雑性 | 低（循環的複雑度10以下） | SonarQube, lizard, gocyclo |

### GitHub Actions CI設定

design.mdには以下のCI設定を含める：

```yaml
# .github/workflows/ci.yml の設計
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests with coverage
        run: npm test -- --coverage
      - name: Check coverage threshold
        run: |
          # カバレッジ80%未満で失敗
          coverage=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$coverage < 80" | bc -l) )); then
            echo "Coverage ${coverage}% is below 80%"
            exit 1
          fi

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: npm run lint

  complexity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check code complexity
        run: npx lizard -CCN 10 src/
```

### 設計書への記載項目

design.mdの「技術的決定事項」セクションに以下を含める：

```text
## CI/CD設計

### 品質ゲート
- テストカバレッジ: 80%以上
- Linter: [選択したツール]でエラー0件
- コード複雑性: 循環的複雑度10以下

### CI/CDパイプライン
- トリガー: push/PRでmain/developブランチ
- 必須チェック: test, lint, complexity
- 成功条件: すべてのチェックがパス

### 採用ツール
- テスト: [Jest/pytest/etc.]
- カバレッジ: [Istanbul/coverage.py/etc.]
- Linter: [ESLint/Ruff/etc.]
- 複雑性: [lizard/SonarQube/etc.]
```

### 言語別推奨ツール

| 言語 | テスト/カバレッジ | Linter | 複雑性 |
|------|------------------|--------|--------|
| TypeScript/JS | Jest + Istanbul | ESLint | lizard |
| Python | pytest + coverage.py | Ruff | radon |
| Go | go test -cover | golangci-lint | gocyclo |
| Rust | cargo test + tarpaulin | clippy | - |

## 後続スキルとの連携

docs/design/の作成完了後：
- **task-planning**: design/を基にタスクを分解

task-planningスキルで逆順レビュー（タスク → 設計 → 要件）が行われます。

## リソース

### テンプレート
- 目次テンプレート: `assets/templates/design_index_template_ja.md`
- コンポーネントテンプレート: `assets/templates/component_template_ja.md`
- APIテンプレート: `assets/templates/api_template_ja.md`
- データベーステンプレート: `assets/templates/database_template_ja.md`
- 技術的決定テンプレート: `assets/templates/decision_template_ja.md`

### リファレンス
- 設計パターン: `references/design_patterns_ja.md`
- EARS記法（要件参照用）: `references/ears_notation_ja.md`

### 命名規則

| ファイル種別 | 命名規則 | 例 |
|-------------|---------|-----|
| コンポーネント | ケバブケース | `user-service.md`, `auth-handler.md` |
| API | リソース名 | `users.md`, `items.md` |
| 技術的決定 | `DEC-XXX.md` | `DEC-001.md`, `DEC-002.md` |
