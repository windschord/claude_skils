---
name: knowledge-base
description: ローカルMarkdownファイルによる個人ナレッジベースを管理する。メモ・記録・ノートの保存、検索・参照、会議メモの構造化、既存ファイルの取り込みに使用する。Do NOT use for プロジェクトのソースコードやSDDドキュメントの管理。
metadata:
  version: "1.0.0"
---

# Knowledge Base スキル

## トリガー条件（descriptionの補足詳細）

> descriptionはスキル発火判定用の簡潔な概要。以下はスキル実行時に参照する詳細なトリガーパターン。

以下のような場面で必ず使用すること：
- 「メモして」「記録して」「ノートに追加して」「保存して」などの保存・追記リクエスト
- 「〜について調べて（自分のナレッジから）」「〜に関する過去の情報は？」などの検索・参照リクエスト
- 「会議メモ」「議事録」「MTGまとめ」などを渡されたとき（構造化して保存）
- 「〜を整理して」「〜を要約してまとめて」などの整理リクエスト
- 「既存のファイルを取り込んで」「〜をナレッジベースに入れて」などの取り込みリクエスト
- ワークスペース（案件・カテゴリ）の作成・一覧・切り替えリクエスト
情報が混在しないよう、必ずワークスペースを明示または確認してから操作すること。

ローカルMarkdownファイルによるナレッジベースを管理する。Git（ローカルのみ）で履歴管理し、VS Codeで閲覧可能な構成を維持する。

---

## KB_ROOTの決定方法

**KB_ROOT = Claude Codeが実行されているカレントディレクトリ（`pwd`）**

設定ファイルは不要。操作前に必ず以下で確認する：

```bash
pwd
```

**初回判定**: Gitリポジトリとして初期化済みかを確認し、さらにKB必須ファイルの存在を検証する。

```bash
git rev-parse --is-inside-work-tree 2>/dev/null && echo "git: initialized" || echo "git: not initialized"
test -f _index/MASTER.md && test -f _index/tags.md && echo "kb: ready" || echo "kb: not ready"
```

- `git: not initialized` → 初回セットアップを提案
- `git: initialized` かつ `kb: not ready` → KB必須ファイルのみ作成を提案（既存リポジトリへの追加）
- 両方OK → 通常操作可能

**既存リポジトリの安全確認**: リモートが設定されている場合、KB操作で意図しないpushが発生しないよう警告する。

```bash
git remote -v
```

リモートが存在する場合は、ユーザーに以下を確認する：
- このリポジトリにKBファイルをコミットしてよいか
- KB専用ディレクトリでの運用を推奨する旨を案内

---

## ディレクトリ構造

```text
{KB_ROOT}/  ← Claude Codeのカレントディレクトリ（pwd）
├── .git/                        # ローカルGit（remoteなし）
├── _index/
│   ├── MASTER.md                # 全ワークスペース横断インデックス
│   └── tags.md                  # 全タグ一覧と件数
├── {workspace-name}/
│   ├── INDEX.md                 # ワークスペース別インデックス（自動更新）
│   └── {note-slug}.md           # 個別ノート
└── ...
```

### ワークスペース命名規則

- 英小文字・ハイフン区切り（例: `project-alpha`, `internal`, `general`）
- 予約済みディレクトリ: `_index`（インデックス専用、ノート不可）

---

## ノートのフォーマット

すべてのノートはYAMLフロントマターを持つ：

```markdown
---
title: ノートのタイトル
workspace: project-alpha
tags: [tag1, tag2, tag3]
created: 2026-03-13
updated: 2026-03-13
---

# ノートのタイトル

本文...
```

### ファイル名規則

- `{YYYY-MM-DD}-{slug}.md`（例: `2026-03-13-api-design-notes.md`）
- 会議メモ: `{YYYY-MM-DD}-meeting-{topic}.md`
- 参照情報（日付に依存しないもの）: `{slug}.md`（例: `aws-s3-tips.md`）

---

## 操作フロー

### 1. ノートの保存・追記

```text
ユーザーの入力 → ワークスペース確認 → ノート作成/追記 → INDEX更新 → MASTER更新 → git commit
```

**手順:**

1. `pwd` でKB_ROOTを確認し、`git rev-parse --is-inside-work-tree` で初期化済みか確認する
2. ワークスペースが未指定なら確認する
3. 既存の関連ノートを検索（`grep -r`）し、追記か新規作成かを判断
4. ノートを書き込む（新規ならフロントマターを付与）
5. `updated` フィールドを今日の日付に更新
6. ワークスペースの `INDEX.md` を更新
7. `_index/MASTER.md` を更新
8. `_index/tags.md` を更新
9. `git add "{workspace}/" "_index/" && git commit -m "{type}: {概要}"`

### 2. 検索・参照

**ワークスペース内検索:**

```bash
grep -r "キーワード" {KB_ROOT}/{workspace}/ --include="*.md" -l
```

**横断検索（全ワークスペース）:**

```bash
grep -r "キーワード" {KB_ROOT}/ --include="*.md" \
  --exclude-dir=".git" -l
```

**タグ検索:**

```bash
grep -r "tags:.*{tag}" {KB_ROOT}/ --include="*.md" -l
```

**検索後**: ヒットしたファイルを読み込み、関連情報を整理して回答する。

### 3. 会議メモの構造化

ユーザーから生のメモ・テキストを受け取ったら、以下の構造に整形してから保存する：

```markdown
---
title: MTG: {トピック}
workspace: {workspace}
tags: [meeting, {関連タグ}]
created: {date}
updated: {date}
---

# MTG: {トピック}

**日時**: {date}
**参加者**: {もしあれば}

## 議題

{箇条書き}

## 決定事項

{箇条書き}

## アクションアイテム

- [ ] {担当者}: {タスク}（{期限}）

## メモ・背景

{その他情報}
```

### 4. 整理・要約

特定のワークスペースまたはテーマについて情報を整理する場合：

1. 関連ノートをすべて収集（grep or INDEXを参照）
2. 重複・古い情報を特定
3. 統合案をユーザーに提示してから実行
4. 整理後はgit commit

### 5. 既存ファイルの取り込み

ユーザーが既存のMarkdownやテキストを渡した場合：

1. フロントマターが未付与なら付与する
2. ワークスペースを確認・設定
3. ファイル名をルール通りにリネーム
4. `{KB_ROOT}/{workspace}/` に配置
5. INDEX・MASTER・tagsを更新
6. git commit

---

## インデックスファイルの仕様

### `_index/MASTER.md`

```markdown
# Knowledge Base マスターインデックス

最終更新: {date}

## ワークスペース一覧

| ワークスペース | ノート数 | 最終更新 | 説明 |
|---|---|---|---|
| [project-alpha](../project-alpha/INDEX.md) | 12 | 2026-03-13 | クライアントAのプロジェクト |
| [internal](../internal/INDEX.md) | 5 | 2026-03-10 | 社内情報 |

## 最近更新されたノート（全体）

- 2026-03-13 [タイトル](../workspace/note.md) `workspace` #tag1 #tag2
```

### `{workspace}/INDEX.md`

```markdown
# {Workspace} インデックス

最終更新: {date}

## ノート一覧

| ファイル | タイトル | 更新日 | タグ |
|---|---|---|---|
| [note.md](./note.md) | タイトル | 2026-03-13 | #tag1 #tag2 |
```

### `_index/tags.md`

```markdown
# タグ一覧

| タグ | 件数 | 関連ノート |
|---|---|---|
| meeting | 8 | [リスト] |
| aws | 3 | [リスト] |
```

---

## Git運用ルール

- **commit message形式**: `{type}: {概要}`
  - `feat:` 新規ノート作成
  - `update:` ノート追記・編集
  - `refactor:` 整理・統合
  - `index:` インデックスのみ更新
  - `import:` 既存ファイル取り込み
- **remoteはなし**: `git remote` は設定しない。既存リポジトリにリモートがある場合は、KB操作後に意図しない `git push` が行われないよう注意すること
- **毎操作後にcommit**: ユーザーが明示的に「まとめてcommitして」と言わない限り、操作ごとにcommitする
- **ステージング範囲の限定**: `git add -A` は使用せず、`git add "{workspace}/" "_index/"` のようにKB関連ディレクトリのみをステージングする

---

## 初回セットアップ手順

Gitリポジトリが未初期化の場合（`git rev-parse --is-inside-work-tree` が失敗）:

1. ユーザーに「現在のディレクトリ（`{pwd}`）をナレッジベースとして初期化しますか？」と確認する
2. 確認が取れたら以下を実行:

```bash
mkdir -p _index
git init
git commit --allow-empty -m "init: knowledge base"
```

3. `_index/MASTER.md` と `_index/tags.md` の初期ファイルを作成
4. 完了をユーザーに報告し、最初のワークスペース名を確認する

既存Gitリポジトリ内で使用する場合（`git: initialized` かつ `kb: not ready`）:

1. リモートの有無を確認し、リモートがある場合はKBファイルをコミットしてよいかユーザーに確認する
2. `_index/MASTER.md` と `_index/tags.md` を作成
3. KB関連ファイルのみをステージングしてcommit

---

## 注意事項

- **情報の混在防止**: ワークスペースが未指定の操作は必ず確認してから実行する
- **破壊的操作の確認**: ノートの削除・大幅な書き換えは事前にユーザーに確認する
- **ファイルサイズ**: 1ノートが500行を超えたら分割を提案する
- **機密情報**: ローカルのみで完結しているが、スクリーンショット等での漏洩リスクをユーザーが認識していることを前提とする
