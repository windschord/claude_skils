# はじめに

Claude Code用スキルコレクションの導入ガイドです。

## インストール

### マーケットプレイスから追加

Claude Codeで以下のコマンドを実行します:

```
/plugin marketplace add https://github.com/windschord/claude_skils.git
```

### 追加を確認

```
/plugin marketplace list
```

`claude-development-skills`がリストに表示されていれば成功です。

### ローカル開発の場合

```bash
# リポジトリをクローン
git clone https://github.com/windschord/claude_skils.git

# ローカルマーケットプレイスを追加
/plugin marketplace add /path/to/claude_skils
```

## クイックスタート

### SDDワークフローで開発を始める

SDDスキルを使って要件定義から実装まで一貫して進めるには:

```text
docsディレクトリを初期化してください
```

これにより`sdd-documentation`オーケストレータースキルが起動し、以下の順序でドキュメントを作成します:

1. **要件定義** (`docs/sdd/requirements/`) - EARS記法で何を作るかを定義
2. **設計** (`docs/sdd/design/`) - どのように作るかを文書化
3. **タスク計画** (`docs/sdd/tasks/`) - 実装タスクを分解
4. **実装** - タスクに沿ってコードを実装

### 個別スキルを使う

各スキルは独立して使用できます:

```text
# なぜなぜ分析を始めたい
# 運用設計書を作成したい
# このドキュメントをエグゼクティブサマリー形式に変換してください
# 社員インタビューを開始してください
```

利用可能なスキルの詳細は[スキルカタログ](skill-catalog.md)を参照してください。

## ドキュメントの種類

このリポジトリには2種類のドキュメントがあります:

| 種類 | 場所 | 対象読者 | 説明 |
|------|------|----------|------|
| **ユーザー向けドキュメント** | `docs/` | 人間 | 使い方ガイド、スキル一覧、開発ガイド |
| **スキル内部リソース** | 各スキルディレクトリ | Claude Code | SKILL.md、references/、assets/templates/ |

### スキル内部リソースの構造

各スキルディレクトリ内のファイルはClaude Codeがスキル実行時に参照する内部リソースです:

```text
{スキル名}/
├── SKILL.md               # スキル定義（Claude Codeが読み込む）
├── references/             # リファレンス（スキル実行時にClaudeが参照）
└── assets/templates/       # テンプレート（ドキュメント生成時に使用）
```

## 次のステップ

- [スキルカタログ](skill-catalog.md) - 全スキルの詳細と使い方
- [SDDワークフロー](sdd-workflow.md) - SDDスキルの詳しいワークフロー
- [開発ガイド](development-guide.md) - 新しいスキルの追加方法
