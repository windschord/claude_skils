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
| **コード品質** | ai-code-review | セキュリティ・可読性等6観点からのPRレビュー |
| | self-review | サブエージェント並列によるローカル変更の6観点セルフレビュー |
| | pr-comment-fixer | PRレビューコメントの自動検出・修正 |
| **運用・監視** | health-check | インフラメトリクスの定期調査・健全性評価 |
| | incident-rca | なぜなぜ分析によるインシデント根本原因特定 |
| | operations-design | ITIL 4/SRE/DevOps運用設計書作成 |
| **インタビュー** | depth-interviewing-career | 社員キャリアインタビュー |
| | depth-interviewing-product | 製品ユーザーインタビュー |
| **ナレッジ管理** | knowledge-base | ローカルMarkdownによるナレッジベース管理 |
| | report-summarizing | レポートのエグゼクティブサマリー変換 |
| **SaaS仕様** | saas-spec-document | SaaSサービス仕様書作成（経済産業省ガイドライン準拠） |
| **オーケストレーション** | orchestrating-agents | 3階層エージェント構造による自律的タスク完遂基盤 |
| **ユーティリティ** | jules-api | Jules REST APIによる対話的タスク管理（ベースブランチ指定、プラン承認、Claude協調） |
| | jules-cli | Jules CLIによるタスク委譲・管理 |
| | things-url | Things 3とのタスク双方向共有 |

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
├── agents/                            # エージェント定義
│   ├── orchestrator.md               # オーケストレーター（親セッション）
│   ├── manager.md                    # マネージャー（子セッション）
│   └── task-executing.md              # タスク実行エージェント（孫としても動作）
├── scripts/                           # ユーティリティスクリプト
│   ├── generate-toc.sh                # 目次生成
│   ├── github-slug.mjs                # GitHubスラグ生成
│   └── lint-skills.sh                 # スキル定義リント
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
├── ai-code-review/                    # AIコードレビュースキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── self-review/                       # セルフレビュースキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── pr-comment-fixer/                  # PRコメント自動修正スキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── health-check/                      # サービスヘルスチェックスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── incident-rca/                      # インシデントRCAスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── sessions/
├── operations-design/                 # 運用設計スキル
│   ├── SKILL.md
│   ├── assets/templates/
│   ├── hearing_items/
│   └── references/
├── knowledge-base/                    # ナレッジベース管理スキル（SKILL.mdのみで動作）
│   └── SKILL.md
├── saas-spec-document/                # SaaSサービス仕様書スキル
│   ├── SKILL.md
│   └── assets/templates/
├── report-summarizing/                # レポート要約スキル
│   ├── SKILL.md
│   └── assets/templates/
├── orchestrating-agents/              # エージェントオーケストレーションスキル
│   ├── SKILL.md
│   ├── assets/templates/
│   └── references/
├── jules-api/                         # Jules API統合スキル
│   ├── SKILL.md
│   └── references/
├── jules-cli/                         # Jules CLIスキル
│   └── SKILL.md
├── things-url/                        # Things URLタスク共有スキル
│   ├── SKILL.md
│   └── references/
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
