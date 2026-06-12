# CI/CD・品質基準ガイド

設計段階で定義すべきCI/CD設定と品質基準のガイドです。

## 必須品質基準

| 項目 | 基準値 | ツール例 |
|------|--------|---------|
| テストカバレッジ | 80%以上 | Jest, pytest, go test |
| ミューテーションスコア | 85%以上 | Stryker, PIT, mutmut, go-mutesting, cargo-mutants |
| Linter | エラー0件 | ESLint, Ruff, golangci-lint |
| コード複雑性 | 低（循環的複雑度10以下） | SonarQube, lizard, gocyclo |

## 言語別推奨ツール

| 言語 | テスト/カバレッジ | ミューテーションテスト | Linter | 複雑性 |
|------|------------------|----------------------|--------|--------|
| TypeScript/JS | Jest + Istanbul | Stryker | ESLint | lizard |
| Python | pytest + coverage.py | mutmut | Ruff | radon |
| Go | go test -cover | go-mutesting | golangci-lint | gocyclo |
| Rust | cargo test + tarpaulin | cargo-mutants | clippy | - |

## 設計書への記載項目

design/index.mdの「技術的決定事項」セクションに以下を含める：

```markdown
## CI/CD設計

### 品質ゲート
- テストカバレッジ: 80%以上
- ミューテーションスコア: 85%以上
- Linter: [選択したツール]でエラー0件
- コード複雑性: 循環的複雑度10以下

### CI/CDパイプライン
- トリガー: push/PRでmain/developブランチ
- 必須チェック: test, mutation, lint, complexity
- 成功条件: すべてのチェックがパス

### 採用ツール
- テスト: [Jest/pytest/etc.]
- カバレッジ: [Istanbul/coverage.py/etc.]
- ミューテーションテスト: [Stryker/PIT/mutmut/cargo-mutants/etc.]
- Linter: [ESLint/Ruff/etc.]
- 複雑性: [lizard/SonarQube/etc.]
```

## デプロイメント環境構成

| 環境 | 用途 | トリガー |
|------|------|----------|
| development | 開発・テスト | develop ブランチへのpush |
| staging | ステージング検証 | release/* ブランチへのpush |
| production | 本番 | main ブランチへのpush（手動承認後） |

## セキュリティスキャン推奨ツール

| カテゴリ | ツール | 用途 |
|----------|--------|------|
| 依存関係 | Dependabot, Snyk | 脆弱性のある依存関係の検出 |
| コード | CodeQL, Semgrep | セキュリティ脆弱性の静的解析 |
| シークレット | GitGuardian, TruffleHog | 認証情報の漏洩検出 |
