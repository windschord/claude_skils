# 開発ガイド

このリポジトリに新しいスキルを追加する方法と、開発に関するガイドラインです。

## スキルの追加方法

### 1. スキルディレクトリを作成

```bash
mkdir -p my-new-skill/references
mkdir -p my-new-skill/assets/templates
```

### 2. SKILL.mdを作成

スキルのルートにSKILL.mdを作成します。これはClaude Codeが読み込むスキル定義ファイルです。

```markdown
---
name: my-new-skill
description: スキルの説明
---

# My New Skill

スキルの詳細な説明...
```

### 3. テンプレート・リファレンスを配置

```text
my-new-skill/
├── SKILL.md               # スキル定義（必須）
├── references/             # リファレンス（Claude実行時参照）
│   └── guide_ja.md
└── assets/templates/       # テンプレート（ドキュメント生成用）
    └── template_ja.md
```

**命名規則:**

| ディレクトリ | 用途 | 命名規則 |
|-------------|------|----------|
| `references/` | スキル実行時にClaudeが参照するガイド | `{内容}_ja.md` |
| `assets/templates/` | ドキュメント生成用テンプレート | `{内容}_template_ja.md` |

### 4. marketplace.jsonに追加

`.claude-plugin/marketplace.json`の`plugins`配列に追加します:

```json
{
  "name": "my-new-skill",
  "description": "スキルの説明",
  "source": "./",
  "strict": false,
  "skills": [
    "./my-new-skill"
  ]
}
```

## ディレクトリ構造の規約

### ドキュメントの種類と配置場所

| 種類 | 配置場所 | 説明 |
|------|----------|------|
| ユーザー向けドキュメント | `docs/` | 人間が読む使い方ガイド |
| スキル定義 | `{スキル}/SKILL.md` | Claude Codeフレームワークが読み込む |
| リファレンス | `{スキル}/references/` | スキル実行時にClaudeが参照する内部リソース |
| テンプレート | `{スキル}/assets/templates/` | ドキュメント生成時に使用するテンプレート |

### 禁止事項

- スキルディレクトリ内にREADME.mdを置かない（ユーザー向け情報は`docs/`に集約）
- `guides/`や`templates/`（assets/なし）など非標準のディレクトリ名を使わない
- テンプレートとリファレンスを同じディレクトリに混在させない

## 日本語文章チェック

textlintを使用して日本語ドキュメントの品質を維持しています。

```bash
# 依存関係のインストール
npm install

# textlintを実行
npm run textlint

# 自動修正を試みる
npm run textlint:fix
```

**設定ファイル:**

- `.textlintrc.json` - ルール設定
- `.textlintignore` - チェック対象外（テンプレート、リファレンスを除外）

## 貢献

### イシューの報告

バグや改善提案は[GitHubのIssues](https://github.com/windschord/claude_skils/issues)で報告してください。

### プルリクエスト

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成
