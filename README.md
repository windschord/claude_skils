# Claude Code Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/windschord/claude_skils)
[![Status](https://img.shields.io/badge/status-WIP-orange.svg)](https://github.com/windschord/claude_skils)

> **注意**: このプロジェクトは現在開発中（Work In Progress）です。機能や仕様が変更される可能性があります。

Claude Code用のスキルコレクションです。各スキルは独立したディレクトリで管理され、プロジェクトのニーズに応じて選択・使用できます。

---

## クイックスタート

```
/plugin marketplace add https://github.com/windschord/claude_skils.git
```

詳しい導入手順は[はじめに](docs/getting-started.md)を参照してください。

## 利用可能なスキル

| カテゴリ | スキル | 説明 |
|---------|--------|------|
| **SDD** | sdd-documentation | SDDオーケストレーター（6つのサブスキルを統括） |
| | requirements-defining | EARS記法による要件定義 |
| | software-designing | 技術アーキテクチャ設計 |
| | task-planning | AIエージェント向けタスク分解 |
| | task-executing | タスク実行・逆順レビュー |
| | sdd-troubleshooting | 問題分析・修正方針策定 |
| | sdd-document-management | ドキュメント管理・メンテナンス |
| **分析** | incident-rca | なぜなぜ分析によるインシデント根本原因特定 |
| **インタビュー** | depth-interviewing-career | 社員キャリアインタビュー |
| | depth-interviewing-product | 製品ユーザーインタビュー |
| **ユーティリティ** | operations-design | ITIL 4/SRE/DevOps運用設計書作成 |
| | report-summarizing | レポートのエグゼクティブサマリー変換 |
| | jules-cli | Jules CLIによるタスク委譲・管理 |

各スキルの詳細と使い方は[スキルカタログ](docs/skill-catalog.md)を参照してください。

## ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [はじめに](docs/getting-started.md) | インストールとクイックスタート |
| [スキルカタログ](docs/skill-catalog.md) | 全スキルの詳細と使い方 |
| [SDDワークフロー](docs/sdd-workflow.md) | SDDスキルの詳しいワークフロー |
| [開発ガイド](docs/development-guide.md) | 新しいスキルの追加方法 |

## ディレクトリ構造

```text
claude_skils/
├── docs/                              # ユーザー向けドキュメント（人間が読む）
│   ├── getting-started.md             # 導入ガイド
│   ├── skill-catalog.md               # 全スキル一覧と使い方
│   ├── sdd-workflow.md                # SDDワークフロー解説
│   └── development-guide.md           # スキル開発者向けガイド
│
├── .claude-plugin/
│   └── marketplace.json               # マーケットプレイス設定
├── CLAUDE.md                          # Claude Code用ガイド（スキル内部リソース）
├── README.md                          # このファイル
├── LICENSE                            # MITライセンス
│
├── sdd-documentation/                 # SDDオーケストレータースキル
│   ├── SKILL.md
│   └── references/
├── requirements-defining/             # 要件定義サブスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── software-designing/                # 設計サブスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── task-planning/                     # タスク計画サブスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── task-executing/                    # タスク実行サブスキル
│   └── references/
├── sdd-troubleshooting/               # トラブルシューティングスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── sdd-document-management/           # ドキュメント管理スキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
│
├── incident-rca/                      # インシデントRCAスキル
│   ├── SKILL.md
│   └── assets/templates/
├── operations-design/                 # 運用設計スキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── report-summarizing/                # レポート要約スキル
│   ├── SKILL.md
│   └── assets/templates/
├── jules-cli/                         # Jules CLIスキル
│   └── SKILL.md
├── depth-interviewing-career/         # キャリアインタビュースキル
│   ├── SKILL.md
│   └── assets/templates/
└── depth-interviewing-product/        # 製品インタビュースキル
    ├── SKILL.md
    └── assets/templates/
```

### ドキュメントの種別

このリポジトリでは、ドキュメントの用途を配置場所で区別しています:

| 配置場所 | 用途 | 対象読者 |
|----------|------|----------|
| `docs/` | ユーザー向けドキュメント（使い方ガイド） | 人間 |
| `SKILL.md` | スキル定義 | Claude Code |
| `references/` | スキル実行時にClaudeが参照するリファレンス | Claude Code |
| `assets/templates/` | ドキュメント生成用テンプレート | Claude Code |

---

## 開発

### 日本語文章チェック

```bash
npm install
npm run textlint
npm run textlint:fix
```

詳しくは[開発ガイド](docs/development-guide.md)を参照してください。

---

## ライセンス

MITライセンス - 詳細は[LICENSE](LICENSE)をご覧ください。

**リポジトリ**: https://github.com/windschord/claude_skils
