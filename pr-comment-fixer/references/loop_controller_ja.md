# ループ制御ロジック

修正→push→bot再レビュー→再スキャンのループを制御するロジック。

## ループフロー概要

```text
┌─────────────────────────────────────────────────────────┐
│                   Fix Loop Controller                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Comment Collectorで全未対応コメント取得               │
│     → known_review_ids を記録                            │
│                                                         │
│  2. 各コメントを分類                                     │
│     - auto-fixable / manual-required / already-addressed│
│                                                         │
│  3. auto-fixableコメントを修正                           │
│                                                         │
│  4. 修正をcommit & push                                 │
│                                                         │
│  5. bot再レビュー待機                                    │
│     - CIステータスポーリング                              │
│     - 新規レビューID監視                                 │
│                                                         │
│  6. 新規レビュー検出 → Step 1 に戻る                     │
│                                                         │
│  7. 完了判定 → レポート出力                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## ループパラメータ

| パラメータ | デフォルト値 | 説明 |
|-----------|------------|------|
| `maxLoops` | 5 | 最大ループ回数 |
| `maxWaitSeconds` | 120 | bot再レビュー待機の最大秒数 |
| `pollIntervalSeconds` | 15 | ポーリング間隔秒数 |

## レビューID追跡

### known_review_idsの管理

ループ開始時に全レビューIDを記録し、push後に新規IDの出現を監視する。

```text
ループ開始時:
  known_review_ids = {pulls/reviews から取得した全レビューID}

push後の再スキャン:
  current_review_ids = {pulls/reviews から再取得した全レビューID}
  new_review_ids = current_review_ids - known_review_ids

  if new_review_ids が空でない:
    → 新規レビューが検出された → 次のループへ
  else:
    → 新規レビューなし
```

### 実行コマンド

```bash
# レビューID一覧を取得
gh api repos/{owner}/{repo}/pulls/{PR番号}/reviews --paginate \
  --jq '.[].id'
```

## bot再レビュー待機

### 待機フロー

push後、botが再レビューを生成するまで待機する。

```text
push完了
  │
  ├── 待機開始（経過時間 = 0）
  │
  ├── ポーリング（15秒間隔）
  │     │
  │     ├── gh pr checks でCIステータス確認
  │     │     → 全チェックが completed になったか?
  │     │
  │     ├── pulls/reviews で新規レビューID確認
  │     │     → known_review_ids に無いIDが出現したか?
  │     │
  │     ├── 両方の条件を満たす → 待機完了
  │     │
  │     └── 経過時間 > maxWaitSeconds → タイムアウト
  │           → 新規レビューID有無を判定:
  │              ├── 検出済み → 次ループへ進む
  │              └── 未検出 → 完了判定へ進む
  │
  └── 待機完了 → 次のステップへ
```

### CIステータス確認

```bash
# PRのチェック状態を確認
gh pr checks {PR番号} --json name,state,conclusion \
  --jq '.[] | {name, state, conclusion}'
```

チェック状態の判定:
- `state: "completed"` かつ `conclusion: "success"` → pass
- `state: "completed"` かつ `conclusion: "failure"` → fail
- `state: "pending"` or `state: "queued"` → 未完了（待機継続）

### 待機のタイムアウト

`maxWaitSeconds`（デフォルト120秒）を超えた場合:
1. CIが未完了でも待機を終了
2. 新規レビューがなければ完了判定へ進む
3. CIが失敗していればユーザーに報告

## 完了判定

### 判定条件

以下のすべてを満たす場合にループを完了とする:

```text
完了条件:
  1. GraphQL reviewThreads で isResolved: false のスレッド = 0
  2. Review body内の未対応コメント = 0
     （対応済み判定でalready-addressedになったものを除く）
  3. CIチェックが全て pass
  4. 新規レビューが検出されていない
```

### 判定フローチャート

```text
ループ N 完了後:
  │
  ├── auto-fixableコメントが 0 件だったか?
  │     │
  │     ├── YES → push不要 → 完了判定へ
  │     │
  │     └── NO → push実行 → bot再レビュー待機
  │                              │
  │                              ├── 新規レビュー検出?
  │                              │     │
  │                              │     ├── YES → ループ N+1 へ
  │                              │     │
  │                              │     └── NO → 完了判定へ
  │                              │
  │                              └── タイムアウト → 完了判定へ
  │
  ├── 完了判定:
  │     │
  │     ├── 未解決スレッド = 0?
  │     │     ├── NO → ループ N+1 へ（maxLoops未到達なら）
  │     │     └── YES → 次の条件へ
  │     │
  │     ├── CI全チェック pass?
  │     │     ├── NO → CI失敗をレポートに記載 → 終了
  │     │     └── YES → 次の条件へ
  │     │
  │     └── 全条件クリア → 完了
  │
  └── ループ回数 >= maxLoops → 強制終了 → レポート出力
```

## CI失敗時の挙動

### CI失敗の種類と対応

| CI失敗の原因 | 対応 |
|-------------|------|
| 修正が原因のテスト失敗 | 修正を見直して再適用（ループ継続） |
| 修正前から存在するテスト失敗 | 無視してループ継続 |
| lint/format エラー | 自動修正を試行（ループ継続） |
| ビルドエラー | ユーザーに報告（ループ中断） |

### CI失敗の判定

```bash
# 失敗したチェックの詳細を取得
gh pr checks {PR番号} --json name,state,conclusion \
  --jq '.[] | select(.conclusion == "failure") | {name, conclusion}'
```

## ループ上限到達時

`maxLoops`に到達した場合:
1. ループを強制終了
2. 残存する未対応コメントをすべてレポートに記載
3. ユーザーに手動対応を促すメッセージを出力

## 進捗報告

各ループの開始時と終了時にユーザーに進捗を報告する。

```text
[pr-comment-fixer] ループ 1/5: コメント収集中...
[pr-comment-fixer] ループ 1/5: 未対応コメント 8件検出（auto-fixable: 6, manual: 2）
[pr-comment-fixer] ループ 1/5: 6件の修正を適用中...
[pr-comment-fixer] ループ 1/5: 修正完了、push中...
[pr-comment-fixer] ループ 1/5: bot再レビュー待機中（最大120秒）...
[pr-comment-fixer] ループ 1/5: 新規レビュー2件検出 → ループ 2へ

[pr-comment-fixer] ループ 2/5: コメント収集中...
[pr-comment-fixer] ループ 2/5: 未対応コメント 1件検出（auto-fixable: 1, manual: 0）
[pr-comment-fixer] ループ 2/5: 1件の修正を適用中...
[pr-comment-fixer] ループ 2/5: 修正完了、push中...
[pr-comment-fixer] ループ 2/5: 新規レビューなし、CI全チェックpass
[pr-comment-fixer] 完了: 全コメント対応済み（2ループ、7件修正、2件手動対応要）
```
