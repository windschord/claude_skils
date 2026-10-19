# Graphify CLI リファレンス

> graphify 0.9.92 の `graphify --help` と、本リポジトリ（Markdown 主体）での実行結果に基づく。バージョンが異なる場合は `graphify --help` で確認すること。
> 実行して確認済み: `update` / `extract --code-only` / `cluster-only --no-label` / `query` / `explain` / `path` / `affected` / `god-nodes` / `benchmark`。未実行: 意味的解析（`--code-only` なしの `extract`）、`hook`、`claude install`、`export`、`save-result`、`reflect`。
> 公式: https://github.com/Graphify-Labs/graphify （ライセンス: Apache-2.0 / MIT）

## 導入

```bash
uv tool install graphifyy      # CLI（graphify / graphify-mcp）。パッケージ名は yが2つ
graphify --version
```

必要に応じて extra（PDF・Office・動画・MCP・Neo4j・SQL 等）を追加できる。詳細は公式READMEを参照。

## グラフ生成・更新

| コマンド | 用途 | 備考 |
|---------|------|------|
| `graphify update <path>` | 初回生成と差分更新（LLM不要、APIキー不要） | `extract` なしで動く。コードに加えて Markdown の見出し構造とリンク参照も取り込む。`graph.json` / `GRAPH_REPORT.md` / `graph.html` を出力する。**既定の手段**。コード削除でノード数が減る場合は `--force` が必要 |
| `graphify extract <path> --code-only` | コードのみ抽出（ローカルAST、APIキー不要） | Markdown は対象外（本リポジトリでは 142 ファイルをスキップ）。出力は `graph.json` のみ。レポートは `cluster-only` で作る |
| `graphify extract <path>` | コード＋ドキュメント等の意味的解析 | APIキー必要（gemini/kimi/claude/openai/deepseek/ollama）。外部送信あり。**未実行** |
| `graphify extract <path> --mode deep` | INFERRED エッジを積極的に抽出 | 誤推論が増える。検証を厳格に |
| `graphify extract <path> --out <dir>` | 出力先を `<dir>/graphify-out/` に変更 | 作業ツリーを汚したくない場合 |
| `graphify extract <path> --force` | インクリメンタル管理を無視して全再抽出 | |
| `graphify cluster-only <path>` | 既存 graph.json のクラスタリング再実行と、`GRAPH_REPORT.md` / `graph.html` の生成 | `--no-label` でLLMによる命名を省略 |
| `graphify watch <path>` | 変更を監視して自動再構築 | 常駐プロセス |
| `graphify hook install` | post-commit 等のgitフックで自動更新 | **リポジトリのgitフックを書き換える。承認必須** |

出力: `graphify-out/graph.json`（完全なグラフ）、`GRAPH_REPORT.md`（コミュニティの要約など）、`graph.html`（可視化）。`update` は3つとも出力し、`extract` は `graph.json` のみ。出力先は対象パス配下の `graphify-out/` で、`--out <dir>` を指定すると `<dir>/graphify-out/` になる。

本リポジトリでの実測（グラフの規模の目安）:

| コマンド | ノード数 | 内訳 |
|---------|---------|------|
| `extract . --code-only` | 136 | コード8ファイル（Python・シェル・設定）。Markdown 142 ファイルはスキップ |
| `update .` | 約3,890 | 上に加えて Markdown の見出し約3,750 ノード。エッジの大半は `contains`（見出しの親子）。文書間の `references` は39件 |

## 照会

| コマンド | 用途 | 主なオプション |
|---------|------|---------------|
| `graphify query "<質問>"` | 質問に関連する部分グラフをBFSで返す | `--dfs` / `--seed X` / `--budget N`（既定2000トークン）/ `--context C`。ノードがすべて収まる場合はエッジを削らず、予算を超えて出力する（実測で約6900トークン） |
| `graphify explain "X"` | ノードと隣接ノードの説明（各接続に `EXTRACTED` / `INFERRED` を表示） | `--all`（全接続。既定は接続数上位20） |
| `graphify path "A" "B"` | 2ノード間の最短経路 | `--undirected`（既定は有向）。同一ファイル内の関数同士は `contains` 経由の自明な経路になりやすい |
| `graphify affected "X"` | 逆方向探索で X の呼び出し元など、変更が波及するノードを列挙 | `--depth N`（既定2）/ `--relation R` |
| `graphify god-nodes` | 最も接続数の多いノード（ハブ） | `--top N` / `--json` |
| `graphify benchmark [graph.json]` | 全ファイル読込とのトークン量の比較 | 本リポジトリでは 94.1 倍と出力。質問は Graphify が用意した汎用の例（"what is the main entry point" など）で、実際の調査での削減量を示すものではない |

共通: `--graph <path>` で graph.json を指定（既定 `graphify-out/graph.json`）。

### 終了コード（query / path / explain）

| コード | 意味 | 対応 |
|-------|------|------|
| 0 | 回答あり | 結果を実コードで確認 |
| 3 | 同じ名前が複数のファイルに存在し曖昧（例: `SKILL.md` は26ノードに一致）。候補がファイルパス付きで列挙される | 候補のファイルパスを含めて再実行する |
| 4 | 該当ノードなし（例: `No node matching 'X' found.`） | 表記を変えて再試行。駄目なら Grep にフォールバック |

注意: 曖昧でも、同一ファイル内の一致や近い一致の場合は、終了コード `0` のまま最上位の候補が選ばれる。`path` では標準エラーに `warning: source match was ambiguous` が出るため、終了コードだけでなく警告も確認する。

## エッジの種類

| タグ | 意味 | 扱い |
|------|------|------|
| `EXTRACTED` | ソースに明示された関係（import・呼び出し等） | 一次情報として扱ってよい（それでも変更前に実コードを確認） |
| `INFERRED` | Graphifyによる推論 | **仮説**。実コードで裏付けるまで根拠にしない |

## フィードバック（任意）

| コマンド | 用途 |
|---------|------|
| `graphify save-result --question Q --answer A --nodes N1 N2 --outcome useful\|dead_end\|corrected [--correction TEXT]` | 照会結果と成否を `graphify-out/memory/` に保存 |
| `graphify reflect` | 蓄積した結果から教訓ドキュメントを生成 |

## エクスポート

`graphify export html|svg|graphml|obsidian|wiki|neo4j|falkordb|callflow-html`。PR本文に貼る図が必要な場合は `callflow-html` や `svg` が使える（Mermaid で十分な場合は Mermaid を優先）。

## 組み込み・自動化（すべて承認必須）

| コマンド | 影響 |
|---------|------|
| `graphify claude install [--project]` | CLAUDE.md にセクション追加＋PreToolUseフック。検索系ツール前にグラフ利用を促す |
| `graphify claude uninstall` | 上記の取り消し |
| `graphify hook install` / `uninstall` / `status` | gitフック（post-commit / post-checkout / post-merge / post-rewrite） |
| `graphify-mcp` | MCPサーバー（`mcp` extra） |

このリポジトリのSDDスキルは、これらの組み込みを前提にしない（CLIの直接実行で完結する）。

## 注意点

- `graphify-out/` への書き込みはClaude Codeのプロンプトキャッシュを無効化し得る。`.claudeignore` に追加する
- クエリログ `~/.cache/graphify-queries.log` に質問文が残る
- ホスト版（Graphify Cloud）は対象外
