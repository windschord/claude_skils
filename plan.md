# ai-code-review SKILL.md GitHub投稿処理の改善プラン

## 変更対象

- `ai-code-review/SKILL.md`

## 修正箇所と内容

### 修正1: ステップ5の末尾に「投稿時の注意事項」ブロックを追加（256行目の後）

ステップ5の承認確認セクションの末尾（現在の「重要: この承認確認は省略できない」ブロックの後）に、投稿時の注意事項ブロックを追記する。

追加内容:
```text
+---------------------------------------------------------------+
| 投稿時の注意事項                                                 |
+---------------------------------------------------------------+
| - 自身のPRには APPROVE / REQUEST_CHANGES を付与できない           |
|   → 自身のPRの場合は event を "COMMENT" にフォールバックする      |
| - commit_id は gh pr view --json headRefOid で取得する          |
| - body やコメントに JSON コードブロック・特殊文字を含む場合、      |
|   -f フラグではエスケープ問題が発生しやすいため                   |
|   --input による JSON ファイル入力を使用する                      |
+---------------------------------------------------------------+
```

### 修正2: ステップ6のインラインコメント投稿方法を差し替え（270-281行目）

現在の `-f` フラグによる投稿方法を、`--input` によるJSON入力方式に全面置換する。

**削除する部分（272-281行目）:**
```bash
# PRレビューをインラインコメント付きで投稿
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews \
  --method POST \
  -f body="レビューサマリー" \
  -f event="COMMENT" \
  -f 'comments[0][path]=ファイルパス' \
  -f 'comments[0][line]=行番号' \
  -f 'comments[0][body]=コメント本文'
```

**置換後:**
```bash
# 1. commit SHA を取得
COMMIT_SHA=$(gh pr view {PR番号} --json headRefOid --jq '.headRefOid')

# 2. JSONファイルにレビュー内容を書き出す（Write ツール推奨）
# /tmp/review_body.json に以下の構造で書き出す:
# {
#   "commit_id": "<COMMIT_SHA>",
#   "event": "COMMENT",
#   "body": "サマリーコメント本文",
#   "comments": [
#     {
#       "path": "ファイルパス",
#       "line": 行番号(int),
#       "body": "インラインコメント本文"
#     }
#   ]
# }

# 3. 投稿
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews \
  --method POST --input /tmp/review_body.json
```

この方式により:
- `comments` が正しいJSON配列として送信される（問題1を解決）
- `commit_id` がリクエストに含まれる（問題3を解決）
- 特殊文字のエスケープ問題が発生しない

## 修正しない箇所

- ステップ1〜4: 変更なし
- レビュー観点、指摘フォーマット、再レビュー手順: 変更なし
- サマリーコメントの投稿方法（264行目のテンプレート参照）: 変更なし

## 影響範囲

SKILL.mdのみの変更。他のファイル（templates、references）への変更は不要。
