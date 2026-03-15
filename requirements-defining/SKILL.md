---
name: requirements-defining
description: EARS記法を用いた要件定義書を作成・編集する。「要件定義して」「ユーザーストーリーを作成して」「非機能要件を整理して」「受入基準を定義して」等の依頼時に使用。docs/sdd/requirements/にユーザーストーリーと非機能要件を出力する。
metadata:
  version: "1.0.0"
---

# 要件定義スキル

EARS記法（Easy Approach to Requirements Syntax）を用いて、明確でテスト可能な要件定義書を作成する。

## 成果物

```text
docs/sdd/requirements/
├── index.md                 # 目次・概要・要件サマリ
├── stories/
│   ├── US-001.md           # ユーザーストーリー詳細
│   └── ...
└── nfr/
    ├── performance.md      # 性能要件
    ├── security.md         # セキュリティ要件
    └── usability.md        # ユーザビリティ要件
```

## EARS記法

| パターン | 形式 | 使用場面 |
|---------|------|----------|
| 基本 | `システムは〜しなければならない` | 常時適用される要件 |
| イベント | `〜の時、システムは〜しなければならない` | イベント駆動要件 |
| 条件 | `もし〜ならば、システムは〜しなければならない` | 状態依存要件 |
| 継続 | `〜の間、システムは〜しなければならない` | 継続的要件 |
| 場所 | `〜において、システムは〜しなければならない` | コンテキスト固有要件 |

要件には具体的な数値を使用する（「高速に」→「2秒以内」）。1要件1「しなければならない」。詳細は [references/ears_notation_ja.md](references/ears_notation_ja.md) を参照。

## ワークフロー

### 新規作成フロー

1. **情報収集**: プロジェクトの目的、対象ユーザー、主要機能を確認
2. **情報分類**: 明示された情報と不明な情報を分けてリストアップ。不明点があればユーザーに確認
3. **ディレクトリ作成**: `docs/sdd/requirements/stories/` と `nfr/` を作成
4. **index.md作成**: 目次テンプレートを使用
5. **ユーザーストーリー作成**: 各ストーリーを `stories/US-XXX.md` として作成
6. **非機能要件作成**: カテゴリ別に `nfr/*.md` を作成
7. **index.md更新**: 作成した各ドキュメントへのリンクを追加
8. **レビュー**: チェックリストで品質確認後、ユーザーに承認を得て完了

### ストーリー追加フロー

1. `stories/US-XXX.md` を作成（ユーザーストーリーテンプレートに従う）
2. index.mdのストーリー一覧テーブルにリンクを追加
3. 関連する既存ストーリーに相互リンクを追加

### 情報分類の段階的処理

長文の要件説明を受け取った場合は段階的に処理する:
1. **Phase 1**: 必須情報のみ確認（プロジェクト名、目的、対象ユーザー）→ 不明点があれば質問
2. **Phase 2**: 機能要件の整理 → ユーザーストーリー作成
3. **Phase 3**: 非機能要件の整理 → NFRドキュメント作成

## ユーザーとの対話

ユーザーの指示を受け取ったら、「明示された情報」と「不明な情報」を分類する。不明な情報が1つでもあれば実装前に確認する。推測で進めない。

```text
【明示された情報】
- [ユーザーから明確に指定された内容]

【不明/要確認の情報】
1. [項目1]: [選択肢A] / [選択肢B] / その他
2. [項目2]: [具体的な質問]
```

## 検証チェックリスト

- [ ] すべての要件がEARS記法に従っている
- [ ] 要件IDが一意である（REQ-XXX、NFR-XXX）
- [ ] 各要件がテスト可能である（具体的な数値・条件あり）
- [ ] 曖昧な表現が排除されている
- [ ] 非機能要件が含まれている

## 後続スキルとの連携

作成完了後、software-designingが設計を行い、task-planningでタスクに分解される。

## リソース

### テンプレート
- 目次: [assets/templates/requirements_index_template_ja.md](assets/templates/requirements_index_template_ja.md)
- ユーザーストーリー: [assets/templates/user_story_template_ja.md](assets/templates/user_story_template_ja.md)
- 非機能要件: [assets/templates/nfr_template_ja.md](assets/templates/nfr_template_ja.md)

### リファレンス
- EARS記法詳細: [references/ears_notation_ja.md](references/ears_notation_ja.md)

### 命名規則

| ファイル種別 | 命名規則 | 例 |
|-------------|---------|-----|
| ユーザーストーリー | `US-XXX.md` | `US-001.md` |
| 非機能要件 | カテゴリ名 | `performance.md`, `security.md` |

### リンク形式

index.mdでは `[詳細](stories/US-001.md) @stories/US-001.md` のようにマークダウン形式と@形式を併記する。
