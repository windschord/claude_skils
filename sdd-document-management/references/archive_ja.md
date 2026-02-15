# アーカイブ詳細ガイド

## アーカイブ対象

| 対象 | 条件 | 移動先 |
|-----|------|--------|
| 完了タスク | ステータスがDONE | docs/sdd/archive/tasks/phase-N/ |
| 古い決定事項 | 明示的に指定 or 一定期間経過 | docs/sdd/archive/decisions/ |
| 古いトラブルシューティング | 修正完了から一定期間経過 | docs/sdd/archive/troubleshooting/ |

## ディレクトリ構造

```text
docs/sdd/archive/
├── tasks/
│   ├── phase-1/
│   └── phase-2/
├── decisions/
└── troubleshooting/
```

## 実行手順

```text
1. docs/sdd/tasks/からステータスDONEのタスクを検出
2. アーカイブ対象リストを作成
3. ★ ユーザーに提示し承認を得る ★
4. 承認されたファイルをdocs/sdd/archive/に移動
5. 移動元のindex.mdを更新
6. アーカイブのindex.mdを更新
```

## アーカイブ時の処理

1. **ファイル移動**: 元のディレクトリ構造を維持
2. **インデックス更新**: 移動元・移動先のindex.mdを更新
3. **参照の保持**: 他ドキュメントからの参照がある場合は警告、リンクを更新

## ユーザー承認フロー

```text
アーカイブ対象を検出しました。

【アーカイブ対象】
- 完了済みタスク: X件
- 古い決定事項: X件

【参照への影響】
- リンク更新が必要: X件

対応を選択してください：

A) すべてアーカイブ（リンクも自動更新）
B) 個別に選択
C) 今回はアーカイブしない
```

## レポートテンプレート

`../assets/templates/archive_report_template_ja.md` を参照。
