# SDD-Docs - ソフトウェア設計ドキュメント管理スキル

Claude Codeのためのソフトウェア設計ドキュメント（SDD）作成・管理スキルです。EARS記法を用いた要件定義、技術設計、タスク管理の3つのドキュメントを構造化されたプロセスで作成します。

## 概要

SDD-Docsは、ソフトウェアプロジェクトにおける以下の課題を解決します：

- 曖昧で測定不可能な要件定義
- 技術的決定事項の記録不足
- タスク分解と進捗管理の困難さ

このスキルは、明確で、テスト可能で、追跡可能なドキュメントの作成を支援します。

## 主な機能

### 3つの必須ドキュメント

1. **requirements.md** - 要件定義書
   - EARS記法を用いたユーザーストーリー
   - 測定可能な受入基準
   - 機能要件と非機能要件の明確な定義

2. **design.md** - 設計書
   - システムアーキテクチャ
   - コンポーネント設計
   - 技術的決定事項と根拠

3. **tasks.md** - タスク管理書
   - 実装可能な粒度へのタスク分解
   - 依存関係の明確化
   - 進捗追跡とステータス管理

### EARS記法（Easy Approach to Requirements Syntax）

要件を明確で曖昧さのないものにする5つの基本パターン：

| パターン | 形式 | 例 |
|---------|------|------|
| 基本 | システムは〜しなければならない | システムはパスワードを暗号化しなければならない |
| イベント | 〜の時、システムは〜しなければならない | ユーザーがログインした時、システムはトークンを生成しなければならない |
| 条件 | もし〜ならば、システムは〜しなければならない | もし認証が失敗した場合、システムはエラーを表示しなければならない |
| 継続 | 〜の間、システムは〜しなければならない | アップロード中、システムは進捗を表示しなければならない |
| 場所 | 〜において、システムは〜しなければならない | EU地域において、システムはGDPR同意を取得しなければならない |

## ディレクトリ構造

```
claude_skils/
├── README.md                              # このファイル
├── CLAUDE.md                              # Claude Code用のガイド
├── LICENSE
└── sdd-docs/                              # スキルのメインディレクトリ
    ├── SKILL.md                           # スキル定義ファイル
    ├── assets/
    │   └── templates/                     # ドキュメントテンプレート
    │       ├── requirements_template_ja.md
    │       ├── design_template_ja.md
    │       └── tasks_template_ja.md
    └── references/                        # リファレンス資料
        ├── ears_notation_ja.md            # EARS記法の詳細ガイド
        └── examples_ja.md                 # 実装例集
```

## 使い方

### Claude Codeでの使用

このスキルは、Claude Codeのスキルシステムを通じて利用します。

1. プロジェクトで「docsディレクトリを初期化してください」と依頼
2. 要件、設計、タスクのテンプレートが自動生成される
3. プロジェクトに応じてカスタマイズされたドキュメントが作成される

### 手動での使用

テンプレートファイルを直接コピーして使用することも可能です：

```bash
# プロジェクトのdocsディレクトリを作成
mkdir -p docs

# テンプレートをコピー
cp sdd-docs/assets/templates/requirements_template_ja.md docs/requirements.md
cp sdd-docs/assets/templates/design_template_ja.md docs/design.md
cp sdd-docs/assets/templates/tasks_template_ja.md docs/tasks.md
```

## ワークフロー

```
1. 要件定義（requirements.md）
   ↓ 何を作るかを定義
2. 設計（design.md）
   ↓ どのように作るかを文書化
3. タスク計画（tasks.md）
   ↓ どのように実装するかを計画
4. 実装とレビュー
   ↓ タスクを実行し、ドキュメントを更新
5. 反復
```

## ベストプラクティス

1. **具体的な値を使用** - 「高速」ではなく「2秒以内」
2. **1要件1文** - 複数の「しなければならない」を避ける
3. **測定可能に** - すべての要件をテスト可能にする
4. **依存関係を明記** - タスク間の関係を明確にする
5. **図表を活用** - Mermaidでアーキテクチャを視覚化
6. **継続的に更新** - プロジェクトの進展に合わせて同期

## リファレンス

- **EARS記法の詳細**: [sdd-docs/references/ears_notation_ja.md](sdd-docs/references/ears_notation_ja.md)
- **実装例**: [sdd-docs/references/examples_ja.md](sdd-docs/references/examples_ja.md)
  - ECショッピングカート（requirements.md）
  - タスク管理API（design.md）
  - ユーザー認証機能（tasks.md）

## 検証チェックリスト

### 要件定義書
- ✅ すべての要件がEARS記法に従っている
- ✅ 要件IDが一意である（REQ-XXX、NFR-XXX）
- ✅ 各要件がテスト可能である
- ✅ 非機能要件が含まれている

### 設計書
- ✅ アーキテクチャ概要がある
- ✅ 主要コンポーネントが定義されている
- ✅ 技術的決定事項と根拠が記載されている
- ✅ 図表が含まれている

### タスク管理書
- ✅ タスクが適切な粒度に分解されている
- ✅ 各タスクに受入基準がある
- ✅ 依存関係が明確である
- ✅ 見積もり時間が記載されている

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 貢献

イシューやプルリクエストを歓迎します。改善提案がある場合は、お気軽にご連絡ください。

## 参考文献

- EARS - The Easy Approach to Requirements Syntax (Alistair Mavin et al.)
- IEEE 830-1998 Standard for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2018 Requirements Engineering