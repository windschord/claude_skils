# 修正適用ロジック

検出した未対応コメントをコード修正に変換し、適用するロジック。

## コメント分類

### 分類判定フロー

```text
UnresolvedComment
      │
      ├── type が "praise" or "summary" → スキップ（対応不要）
      │
      ├── type が "question" → manual-required（設計判断が必要）
      │
      ├── path が null → manual-required（対象ファイル不明）
      │
      ├── status が "already-addressed" → スキップ（対応済み）
      │
      ├── 対象ファイルが存在しない → manual-required（ファイル不明）
      │
      ├── severity が "critical" かつ
      │   セキュリティ/アーキテクチャ関連 → manual-required（設計判断が必要）
      │
      └── それ以外 → auto-fixable
```

### auto-fixable判定の詳細基準

以下のすべてを満たすコメントをauto-fixableとする:

1. `path`が特定されている（null でない）
2. 対象ファイルがワークツリーに存在する
3. コメントの内容がコード修正で対応可能（設計判断不要）
4. 修正の影響範囲がコメント対象のファイル内に限定される

### manual-requiredとなるケース

- アーキテクチャの変更を要する指摘
- 複数ファイルにまたがるリファクタリング提案
- トレードオフの判断を要する指摘（パフォーマンス vs 可読性等）
- 仕様の解釈に曖昧性がある指摘
- 対象ファイルパスが特定できない指摘

## 修正適用フロー

### 1件ずつの修正

```text
auto-fixableコメント1件ごとに:
  1. 対象ファイルをReadツールで読み込み
  2. コメントの指摘内容を分析
  3. 該当箇所を特定（line番号 + コンテキスト）
  4. Editツールで修正を適用
  5. 修正内容をメモリに記録
```

### 修正時の注意事項

- **Editツール使用**: old_string/new_stringの指定で正確に修正
- **コンテキスト確認**: line番号だけでなく、diff_hunkとファイル内容で該当箇所を確認
- **最小限の修正**: コメントの指摘に直接対応する変更のみ。周辺コードのリファクタリングは行わない
- **インデント保持**: 既存のインデントスタイルを維持
- **suggestion形式への対応**: Copilotのsuggestionコードブロックは提案コードでそのまま置換

### 行番号のズレへの対処

同一ファイルへ複数の修正を適用すると、先の修正により行番号がズレる可能性がある。

対処方法:
1. 同一ファイルの修正はファイル末尾側から適用（行番号のズレを回避）
2. またはEditツールのold_string指定で正確に該当箇所を特定（行番号に依存しない）

## コミット戦略

### コミット単位

修正はまとめて1つのコミットとする（コメント1件ごとのコミットは不要）。

### コミットメッセージフォーマット

```text
fix: address PR review comments

Addressed the following review comments:
- [{reviewer}] {path}:{line} - {summary}
- [{reviewer}] {path}:{line} - {summary}
...

Skipped (manual review required):
- [{reviewer}] {path}:{line} - {reason}
```

### コミット手順

```bash
# 変更されたファイルをステージング
git add {修正したファイルパス1} {修正したファイルパス2} ...

# コミット
git commit -m "fix: address PR review comments" \
  -m "Addressed the following review comments:" \
  -m "- [coderabbitai[bot]] src/app/api/route.ts:341 - Fix filter condition" \
  -m "- [coderabbitai[bot]] docs/sdd/tasks/index.md - Add missing entry" \
  -m "" \
  -m "Skipped (manual review required):" \
  -m "- [coderabbitai[bot]] architecture decision - Requires design review"
```

### push

```bash
# 現在のブランチにpush
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH"
```

## テスト実行

### 修正後のテスト

修正をコミットする前に、プロジェクトのテストスイートを実行して修正がビルド/テストを壊していないことを確認する。

### テスト実行の判断

1. `package.json`に`test`スクリプトがある場合 → `npm test`を実行
2. `Makefile`に`test`ターゲットがある場合 → `make test`を実行
3. テストスイートが存在しない場合 → テストスキップ（ビルド確認のみ）

### テスト失敗時

テストが失敗した場合:
1. 失敗したテストのエラー内容を分析
2. 修正が原因の場合 → 修正を見直して再適用
3. 既存のテスト失敗（修正前から失敗）の場合 → そのまま続行し、レポートに記載

## 修正結果の記録

各コメントの修正結果を以下の形式で記録する:

```text
FixResult {
  commentId: string        // 元コメントのID
  status: string           // "fixed" | "skipped" | "failed"
  action: string           // 実施した修正の概要
  reason: string | null    // skipped/failedの場合の理由
  filesModified: string[]  // 修正したファイルパス
}
```

この記録は最終レポートの生成と、ループ制御での進捗追跡に使用される。
