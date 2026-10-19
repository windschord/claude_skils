# Graphify CLI リファレンス

> graphify 0.9.92 の `graphify --help` に基づく。バージョンが異なる場合は `graphify --help` で確認すること。
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
| `graphify extract <path> --code-only` | コードのみ抽出（ローカルAST、APIキー不要） | 既定で推奨。ドキュメントは対象外 |
| `graphify extract <path>` | コード＋ドキュメント等の意味的解析 | APIキー必要（gemini/kimi/claude/openai/deepseek/ollama）。外部送信あり |
| `graphify extract <path> --mode deep` | INFERRED エッジを積極的に抽出 | 誤推論が増える。検証を厳格に |
| `graphify extract <path> --out <dir>` | 出力先を `<dir>/graphify-out/` に変更 | 作業ツリーを汚したくない場合 |
| `graphify extract <path> --force` | インクリメンタル管理を無視して全再抽出 | |
| `graphify update <path>` | コード差分の再抽出（LLM不要） | 削除を伴う変更後は `--force` |
| `graphify cluster-only <path>` | 既存 graph.json のクラスタリング再実行 | `--no-label` でLLMによる命名を省略 |
| `graphify watch <path>` | 変更を監視して自動再構築 | 常駐プロセス |
| `graphify hook install` | post-commit 等のgitフックで自動更新 | **リポジトリのgitフックを書き換える。承認必須** |

出力: `graphify-out/graph.json`（完全なグラフ。`schema_version` / `graphify_version` を含む）、`GRAPH_REPORT.md`（主要概念・意外な接続・推奨質問）、`graph.html`（可視化）。

## 照会

| コマンド | 用途 | 主なオプション |
|---------|------|---------------|
| `graphify query "<質問>"` | 質問に関連する部分グラフをBFSで返す | `--dfs` / `--seed X` / `--budget N`（既定2000トークン）/ `--context C` |
| `graphify explain "X"` | ノードと隣接ノードの説明 | `--all`（全接続。既定は接続数上位20） |
| `graphify path "A" "B"` | 2ノード間の最短経路 | `--undirected`（既定は有向） |
| `graphify affected "X"` | 逆方向探索で X の変更が波及するノードを列挙 | `--depth N`（既定2）/ `--relation R` |
| `graphify god-nodes` | 最も接続数の多いノード（ハブ） | `--top N` / `--json` |
| `graphify benchmark [graph.json]` | 全ファイル読込との比較でトークン削減量を計測 | 効果の検証用 |

共通: `--graph <path>` で graph.json を指定（既定 `graphify-out/graph.json`）。

### 終了コード（query / path / explain）

| コード | 意味 | 対応 |
|-------|------|------|
| 0 | 回答あり | 結果を実コードで確認 |
| 3 | 名前が曖昧（候補が列挙される） | 候補から選び、`--seed` や完全なラベルで再実行 |
| 4 | 該当ノードなし | 表記を変えて再試行。駄目なら Grep にフォールバック |

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
