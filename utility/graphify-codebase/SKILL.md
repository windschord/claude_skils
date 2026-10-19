---
name: graphify-codebase
description: Graphify（コードベースをナレッジグラフ化するCLI）を導入・更新・照会し、SDDの設計・レビュー・実装・トラブルシューティングで影響範囲や依存関係の調査に使う。既存コードの構造把握、変更の波及範囲の特定、2要素間の経路追跡が必要な場合に使用する。Graphifyは任意の補助ツールであり、未導入でも既存の調査手順にフォールバックする。Do NOT use for 要求の整合性検証（requirement-managementのreqctl.pyを使用すること）。
metadata:
  version: "1.0.0"
---

# Graphify コードベース調査スキル

[Graphify](https://github.com/Graphify-Labs/graphify) でコードベースをナレッジグラフ化し、SDDの各フェーズ（設計・レビュー・実装・トラブルシューティング）で「どこを読むべきか」「何に波及するか」を、ファイルを総当たりで読まずに特定するためのスキルです。

## 重要な原則

1. **Graphifyは任意の補助ツール**: 未導入・生成失敗・グラフが古い場合は、従来どおり Grep/Glob/Read で調査する。Graphifyが無いことで作業を止めない
2. **グラフは仮説、コードが正**: `INFERRED`（推論）エッジは裏付けではなく調査の手がかり。設計判断・指摘・修正の根拠にする前に、必ず該当コードを読んで確認する
3. **導入はユーザー承認のうえで行う**: `graphify claude install` は CLAUDE.md の書き換えとフック（PreToolUse）を追加する。承認なしに実行しない
4. **生成物はコミットしない**: `graphify-out/` は派生物。`.gitignore` と `.claudeignore` に追加する（書き込みでプロンプトキャッシュが無効化されるのを防ぐ）
5. **外部送信の範囲を意識する**: コード（AST解析）はローカルで処理されるが、ドキュメント・画像等の意味的解析は設定したモデル／APIキー経由で外部に送られる。機密リポジトリでは `--code-only` を既定にする

## このスキルを使用する場面

| SDDフェーズ | 使いどころ | 主なコマンド |
|------------|-----------|-------------|
| 設計（PR本文の設計ノート） | 既存構造の把握、変更の影響範囲の洗い出し | `query` / `explain` / `god-nodes` / `affected` |
| 逆順レビュー・コードレビュー | 変更シンボルの呼び出し元・依存先の確認、見落とし検出 | `affected` / `path` / `explain` |
| 実装（task-executing） | 触るべきファイルの絞り込み、実装後のグラフ更新 | `query` / `explain` / `update` |
| トラブルシューティング | エラー箇所とエントリポイントの経路特定、波及範囲の確認 | `path` / `affected` / `explain` |
| タスク計画 | Issue本文の「変更対象ファイル候補」の根拠 | `query` / `affected` |

フェーズごとの具体的な手順は `references/sdd_integration_ja.md` を参照。

## ワークフロー

### ステップ1: 利用可否の判定

```bash
command -v graphify          # 導入済みか
ls graphify-out/graph.json   # グラフが生成済みか
```

| 状態 | 対応 |
|------|------|
| 導入済み・グラフあり | ステップ3（鮮度確認）へ |
| 導入済み・グラフなし | ステップ2（生成）へ |
| 未導入 | ユーザーに導入可否を確認。拒否・不可なら**従来の調査にフォールバック**して終了 |

### ステップ2: 導入とグラフ生成（初回のみ）

```bash
# 前提: Python 3.10+ と uv（または pipx）。パッケージ名は graphifyy（yが2つ）
uv tool install graphifyy

# APIキー不要・コードのみ（tree-sitter、ローカル完結）
graphify extract . --code-only
```

- ドキュメント（Markdown・PDF等）も対象にするには `--code-only` を外す。意味的解析のため APIキー（`ANTHROPIC_API_KEY` 等）が必要
- 生成物は `graphify-out/`（`graph.json` / `GRAPH_REPORT.md` / `graph.html`）
- 生成後、`.gitignore` と `.claudeignore` に `graphify-out/` を追記する（既に無いか確認してから）
- 大規模リポジトリで時間がかかる場合は対象ディレクトリを絞る（`graphify extract <サブディレクトリ>`）

### ステップ3: グラフの鮮度確認と更新

調査の前に、グラフが現在のコードと乖離していないか確認する。

```bash
git log -1 --format=%cI -- graphify-out/graph.json 2>/dev/null   # 追跡している場合
stat -c %y graphify-out/graph.json                                 # ファイルの更新時刻
git diff --stat HEAD                                               # 未反映の変更の有無
```

乖離がある場合は、LLM不要の差分更新を行う。

```bash
graphify update .
```

リファクタリングでコードを削除した後は、ノード数が減るため `--force` が必要になる場合がある（`graphify update . --force`）。

### ステップ4: 照会

```bash
graphify query "認証トークンの検証はどこで行われるか"   # 質問に関連する部分グラフ（既定2000トークン上限）
graphify explain "TokenValidator"                      # ノードと隣接ノードの説明
graphify path "LoginController" "UserRepository"       # 2ノード間の最短経路
graphify affected "UserRepository" --depth 2           # 逆方向探索: 変更の波及先
graphify god-nodes --top 10                            # 最も接続数の多いハブ
```

終了コード: `0`=回答あり / `3`=名前が曖昧（候補が列挙される。候補から選んで再実行）/ `4`=該当ノードなし（Grep にフォールバック）。

全コマンドの詳細は `references/cli_reference_ja.md` を参照。

### ステップ5: 結果の検証と記録

1. 照会結果で挙がったファイル・シンボルを **Read で実コードと突き合わせる**（特に `INFERRED` エッジ）
2. 検証できた内容だけを、設計ノート／レビュー指摘／Issue本文に転記する（`assets/templates/impact_analysis_note_template_ja.md`）
3. 結果と実態が食い違った場合は記録する（任意）

```bash
graphify save-result --question "..." --answer "..." --nodes A B --outcome corrected --correction "実際は..."
```

## 禁止事項

- グラフの結果だけを根拠にした設計判断・レビュー指摘・修正（必ず実コードで確認する）
- `INFERRED` エッジを `EXTRACTED`（ソースに明示された関係）と同等に扱うこと
- 承認なしの `graphify claude install` / `graphify hook install`（CLAUDE.md・フック・gitフックを書き換える）
- 機密リポジトリで、意味的解析（`--code-only` なし）を承認なしに実行すること
- `graphify-out/` のコミット、およびグラフが古いまま結果を鵜呑みにすること

## プライバシーに関する注意

- クエリログが `~/.cache/graphify-queries.log` に記録される。質問文に機密情報を含めない。無効化の方法は Graphify の公式ドキュメントで確認する
- 有料のホスト版（Graphify Cloud）はこのスキルの対象外。ローカルCLIのみを前提とする

## フォールバック

Graphifyを使えない場合、同じ目的を次の手段で代替する。

| Graphifyの用途 | 代替手段 |
|---------------|---------|
| `query` / `explain` | Grep（シンボル・キーワード検索）→ Read |
| `affected` | シンボル名のGrep（呼び出し元の洗い出し）＋テストファイルの確認 |
| `path` | エントリポイントから呼び出しを手で追跡 |
| `god-nodes` | import／参照数の多いファイルをGrepで集計 |

## 進捗の可視化

```text
[graphify-codebase] ステップ 1/5: 利用可否を判定中...
[graphify-codebase] ステップ 3/5: グラフの鮮度を確認中（最終更新: ...）...
[graphify-codebase] ステップ 4/5: query を実行中...
[graphify-codebase] 完了: 候補ファイル N 件を特定（実コードで確認済み M 件）
```

## リソース

- `references/cli_reference_ja.md` - コマンドリファレンス（用途・終了コード・注意点）
- `references/sdd_integration_ja.md` - SDDフェーズ別の使い方
- `assets/templates/impact_analysis_note_template_ja.md` - 影響範囲調査ノート（PR設計ノート／Issue本文に貼る）
