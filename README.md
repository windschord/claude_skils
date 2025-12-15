# Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/windschord/claude_skils)
[![Status](https://img.shields.io/badge/status-WIP-orange.svg)](https://github.com/windschord/claude_skils)

> **注意**: このプロジェクトは現在開発中（Work In Progress）です。機能や仕様が変更される可能性があります。

Claude Code用のスキルコレクションです。各スキルは独立したディレクトリで管理され、プロジェクトのニーズに応じて選択・使用できます。

---

## インストール

### Claude Codeでマーケットプレイスを追加

Claude Codeで以下のコマンドを実行します：

```
/plugin marketplace add https://github.com/windschord/claude_skils.git
```

これにより、このリポジトリがマーケットプレイスとして追加され、すべてのスキルが利用可能になります。

### 追加を確認

マーケットプレイスが正しく追加されたか確認します：

```
/plugin marketplace list
```

`sdd-documentation-skills`がリストに表示されていれば成功です。

### ローカル開発の場合

ローカルで開発やカスタマイズを行う場合は、リポジトリをクローンしてローカルパスを指定します：

```bash
# リポジトリをクローン
git clone https://github.com/windschord/claude_skils.git

# Claude Codeでローカルマーケットプレイスを追加
/plugin marketplace add /path/to/claude_skils
```

---

## 利用可能なスキル

### SDD-Docs

ソフトウェア設計ドキュメント（SDD）を作成・管理するスキルです。

**主な機能:**
- EARS記法による要件定義（requirements.md）
- 技術設計の文書化（design.md）
- タスク管理と進捗追跡（tasks.md）

**詳細:** [sdd-docs/README.md](sdd-docs/README.md)

**使用開始:**
```
docsディレクトリを初期化してください
```

### Task Executor

docs/tasks.mdに記載されたタスクを自動的に実行するスキルです。

**主な機能:**
- サブエージェントを使用した自動実装
- 並列実行可能なタスクの並列処理
- タスクごとの自動コミット作成
- タスク完了時のtasks.md自動更新

**詳細:** [task-executor/README.md](task-executor/README.md)

**使用開始:**
```
次のタスクを実行してください
```

### Incident RCA

インシデント調査で根本原因を特定するためのなぜなぜ分析ファシリテーションツールです。

**主な機能:**
- なぜなぜ分析による体系的な根本原因の特定
- ユーザーの発言を漏らさず記録
- リアルタイムマインドツリーの作成と可視化
- ファシリテーターとしての中立的なサポート
- 複合要因の分割と個別分析
- 最低1つの根本原因の特定保証

**詳細:** [incident-rca/README.md](incident-rca/README.md)

**使用開始:**
```
インシデントの根本原因を分析したい
```

### Jules CLI

docs/tasks.mdに記載されたタスクをJules CLIを使って依頼・管理するスキルです。

**主な機能:**
- タスクを日本語でフォーマットしてJulesに依頼
- Julesの進捗状況を追跡・管理
- 完了したタスクをtasks.mdで自動更新
- 複数タスクの並行依頼サポート
- 詳細な文脈提供による高品質な実装

**詳細:** [jules-cli/README.md](jules-cli/README.md)

**使用開始:**
```
次のタスクをJulesに依頼してください
```

### Operations Design

運用設計コンサルタントとして、ITIL 4・SRE・DevOpsに基づいた運用設計書を作成するスキルです。

**主な機能:**
- 対象業界の最新トレンド調査
- サービス仕様の体系的ヒアリング
- インフラパターン別テンプレート（クラウドネイティブ/IaaS/オンプレミス）
- 包括的な運用設計書の作成（20セクション）
- 設計内容の一貫性チェックと客観的レビュー
- 会話ログによるコンテキスト保持

**詳細:** [operations-design/README.md](operations-design/README.md)

**使用開始:**
```
運用設計書を作成したい
```

### Executive Summary

調査結果や分析レポートをエグゼクティブサマリー + 本編の2部構成で整理するスキルです。

**主な機能:**
- エグゼクティブサマリー + 本編の2部構成への変換
- Mermaidダイアグラム（マインドマップ、フローチャート等）による全体像の可視化
- 結論・推奨事項・重要ポイントを冒頭1〜2ページに要約
- 詳細セクションへの内部リンクによるナビゲーション
- GitHub/VSCodeで直接レンダリング可能なMarkdown形式

**詳細:** [executive-summary/README.md](executive-summary/README.md)

**使用開始:**
```
このドキュメントをエグゼクティブサマリー形式に変換してください
```

---

## ディレクトリ構造

```
claude_skils/
├── .claude-plugin/
│   └── marketplace.json           # マーケットプレイス設定
├── .gitignore                      # Git除外設定
├── README.md                       # このファイル
├── CLAUDE.md                       # Claude Code用ガイド
├── LICENSE                         # MITライセンス
├── sdd-docs/                       # SDD-Docsスキル
│   ├── SKILL.md                    # スキル定義
│   ├── README.md                   # スキル詳細ドキュメント
│   ├── assets/
│   │   └── templates/              # ドキュメントテンプレート
│   └── references/                 # リファレンス資料
├── task-executor/                  # Task Executorスキル
│   ├── SKILL.md                    # スキル定義
│   └── README.md                   # スキル詳細ドキュメント
├── incident-rca/                   # Incident RCAスキル
│   ├── SKILL.md                    # スキル定義
│   ├── README.md                   # スキル詳細ドキュメント
│   └── templates/                  # 分析テンプレート
│       ├── result_template.md      # 結果テンプレート
│       └── log_template.md         # ログテンプレート
├── jules-cli/                      # Jules CLIスキル
│   ├── SKILL.md                    # スキル定義
│   └── README.md                   # スキル詳細ドキュメント
├── operations-design/              # Operations Designスキル
│   ├── SKILL.md                    # スキル定義
│   ├── README.md                   # スキル詳細ドキュメント
│   ├── assets/
│   │   └── templates/              # 運用設計書テンプレート
│   ├── guides/                     # ガイドドキュメント
│   ├── hearing_items/              # ヒアリング項目
│   └── references/                 # リファレンス資料
└── executive-summary/              # Executive Summaryスキル
    ├── SKILL.md                    # スキル定義
    ├── README.md                   # スキル詳細ドキュメント
    └── assets/
        └── templates/              # エグゼクティブサマリーテンプレート
```

---

## スキルの追加方法（開発者向け）

このリポジトリに新しいスキルを追加する場合：

1. **スキルディレクトリを作成**
   ```bash
   mkdir my-new-skill
   cd my-new-skill
   ```

2. **SKILL.mdを作成**
   ```markdown
   ---
   name: my-new-skill
   description: スキルの説明
   ---

   # My New Skill

   スキルの詳細な説明...
   ```

3. **README.mdを作成**

   スキルの使い方、機能、例などを記載します。

4. **marketplace.jsonに追加**

   `.claude-plugin/marketplace.json`の`plugins`配列に新しいスキルを追加します：
   ```json
   {
     "name": "スキル名",
     "description": "スキルの説明",
     "source": "./",
     "strict": false,
     "skills": [
       "./sdd-docs",
       "./my-new-skill"
     ]
   }
   ```

---

## 開発

### 日本語文章チェック

このプロジェクトでは、textlintを使用して日本語ドキュメントの品質を維持しています。

**ローカルでチェック:**
```bash
# 依存関係のインストール
npm install

# textlintを実行
npm run textlint

# 自動修正を試みる
npm run textlint:fix
```

**GitHub Actions:**
プルリクエスト作成時に、自動的にtextlintが実行されます。エラーが検出された場合は、PRにコメントが追加されます。

**設定:**
- `.textlintrc.json`: textlintのルール設定
- `.textlintignore`: チェック対象外ファイルの設定（テンプレート、リファレンスファイルを除外）
- 有効なルール:
  - `preset-ja-technical-writing`: 技術文書向け日本語ルール（一部のルールは緩和設定）

---

## 貢献

貢献を歓迎します！以下の方法で参加できます：

### イシューの報告

バグや改善提案がある場合は、GitHubのIssuesで報告してください。

### プルリクエスト

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 新しいスキルの提案

新しいスキルのアイデアがある場合は、Issueで提案してください。以下の情報を含めると検討がスムーズです：

- スキルの目的
- 解決する課題
- 主な機能
- 使用例

---

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

---

## サポート

質問や問題がある場合は、GitHubのIssuesでお知らせください。

**リポジトリ**: https://github.com/windschord/claude_skils
