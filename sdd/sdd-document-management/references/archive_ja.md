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
3. CLAUDE.mdへの反映対象を抽出（★ 新規ステップ ★）
4. ★ ユーザーに提示し承認を得る ★
5. 承認されたファイルをdocs/sdd/archive/に移動
6. 移動元のindex.mdを更新
7. アーカイブのindex.mdを更新
8. CLAUDE.mdの各仕様セクション（API Endpoints, DB Schema, Services等）を更新（★ 必須 ★）
```

## アーカイブ時の処理

1. **ファイル移動**: 元のディレクトリ構造を維持
2. **インデックス更新**: 移動元・移動先のindex.mdを更新
3. **参照の保持**: 他ドキュメントからの参照がある場合は警告、リンクを更新
4. **CLAUDE.md同期（必須）**: 完了プロジェクトの実装結果をCLAUDE.mdに反映

### CLAUDE.md同期の詳細

アーカイブ対象のSDD（requirements, design, tasks）から以下の情報を抽出し、CLAUDE.mdの対応セクションに追記する:

| 抽出対象 | CLAUDE.mdの反映先セクション |
|---------|---------------------------|
| APIエンドポイント定義 | API Endpoints |
| テーブル/カラム定義 | DB Schema |
| サービスクラス | Services |
| 画面/ページ定義 | Pages |
| WebSocketメッセージ定義 | WebSocket Message Types |
| 状態遷移定義 | State Machines |
| ビジネスルール | Business Rules |
| 環境変数 | Environment Variables |

```text
反映手順:
1. アーカイブ対象のSDD（requirements/*.md, design/*.md, tasks/*.md）からAPI、DB、サービス等の定義を抽出
2. CLAUDE.mdの該当セクションを検索
3. 未記載の項目を追記（既存の項目は更新不要）
4. セクション自体が存在しない場合は新規作成
```

**重要**: この同期ステップを省略すると、実装した仕様がどこにも「現在形」で残らなくなる。SDD完了 = archive移動 + CLAUDE.md更新 はセットで行うこと。

## ユーザー承認フロー

```text
アーカイブ対象を検出しました。

【アーカイブ対象】
- 完了済みタスク: X件
- 古い決定事項: X件

【参照への影響】
- リンク更新が必要: X件

【CLAUDE.md更新対象】
- 新規API: X件
- 新規テーブル/列: X件
- 新規サービス: X件
- その他: X件

対応を選択してください：

A) すべてアーカイブ + CLAUDE.md更新（リンクも自動更新）
B) タスクのみアーカイブ + CLAUDE.md更新
C) 決定事項のみアーカイブ + CLAUDE.md更新
D) 個別に選択（※ CLAUDE.md更新は選択に関わらず必須）
E) 今回はアーカイブしない
```

## レポートテンプレート

`../assets/templates/archive_report_template_ja.md` を参照。
