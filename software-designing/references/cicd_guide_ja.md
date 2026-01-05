# CI/CD・品質基準ガイド

設計段階で定義すべきCI/CD設定と品質基準の詳細ガイドです。

## 必須品質基準

設計段階で以下の品質基準を定義し、GitHub Actionsで自動検証します：

| 項目 | 基準値 | ツール例 |
|------|--------|---------|
| テストカバレッジ | 80%以上 | Jest, pytest, go test |
| Linter | エラー0件 | ESLint, Ruff, golangci-lint |
| コード複雑性 | 低（循環的複雑度10以下） | SonarQube, lizard, gocyclo |

## GitHub Actions CI設定

design/index.mdには以下のCI設定を含めます：

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

## 設計書への記載項目

design/index.mdの「技術的決定事項」セクションに以下を含めます：

```markdown
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

## 言語別推奨ツール

| 言語 | テスト/カバレッジ | Linter | 複雑性 |
|------|------------------|--------|--------|
| TypeScript/JS | Jest + Istanbul | ESLint | lizard |
| Python | pytest + coverage.py | Ruff | radon |
| Go | go test -cover | golangci-lint | gocyclo |
| Rust | cargo test + tarpaulin | clippy | - |

## デプロイメント設計

### 環境構成

| 環境 | 用途 | トリガー |
|------|------|----------|
| development | 開発・テスト | develop ブランチへのpush |
| staging | ステージング検証 | release/* ブランチへのpush |
| production | 本番 | main ブランチへのpush（手動承認後） |

### デプロイメントパイプライン

```yaml
# .github/workflows/deploy.yml の設計
name: Deploy

on:
  push:
    branches:
      - develop
      - 'release/*'
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || (startsWith(github.ref, 'refs/heads/release') && 'staging' || 'development') }}
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          # 環境に応じたデプロイ処理
```

## セキュリティスキャン

### 推奨ツール

| カテゴリ | ツール | 用途 |
|----------|--------|------|
| 依存関係 | Dependabot, Snyk | 脆弱性のある依存関係の検出 |
| コード | CodeQL, Semgrep | セキュリティ脆弱性の静的解析 |
| シークレット | GitGuardian, TruffleHog | 認証情報の漏洩検出 |

### GitHub Actions統合

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * 1'  # 毎週月曜日

jobs:
  codeql:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v2
      - uses: github/codeql-action/analyze@v2
```
