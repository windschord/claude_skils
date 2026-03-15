# CLAUDE.md同期 詳細ガイド

## 目的

CLAUDE.mdは「今動いているもの」の仕様書であり、常にコンテキストに入る最重要ドキュメントです。
このガイドでは、CLAUDE.mdと実装コードの乖離を検出し、CLAUDE.mdを最新状態に保つ手順を説明します。

## チェック対象

### CLAUDE.md vs 実装の比較

| チェック項目 | CLAUDE.md側 | 実装側（例） |
|-------------|------------|-------------|
| API一覧 | API Endpointsセクション | `src/app/api/`, `src/routes/` |
| サービス一覧 | Servicesセクション | `src/services/` |
| DBスキーマ | DB Schemaセクション | `src/db/schema.ts`, `prisma/schema.prisma` |
| ページ一覧 | Pagesセクション | `src/app/`, `src/pages/` |
| WebSocket | WebSocket Message Typesセクション | WebSocket関連実装ファイル |
| 状態遷移 | State Machinesセクション | 状態管理コード |

### 不足セクション検出

CLAUDE.mdに以下のセクションが存在するか確認し、不足があれば報告します:

| セクション | 必須/推奨 | 説明 |
|-----------|----------|------|
| API Endpoints | 必須 | 全APIエンドポイントの一覧 |
| DB Schema | 必須 | テーブル定義と重要カラム |
| Services | 必須 | サービス一覧と責務 |
| Pages | 推奨 | 画面一覧と主要機能 |
| WebSocket Message Types | 推奨 | メッセージ種別と方向（該当する場合） |
| State Machines | 推奨 | 状態遷移（該当する場合） |
| Business Rules | 推奨 | 重要なビジネスルール |
| Environment Variables | 必須 | 環境変数の一覧 |

## 実行手順

```text
1. CLAUDE.mdの各仕様セクションを解析
   - 記載されているAPI、サービス、テーブル等をリストアップ

2. 対応する実装コードをスキャン
   - ルーティングファイルからAPIエンドポイントを抽出
   - サービスディレクトリからサービス一覧を抽出
   - スキーマ定義ファイルからテーブル/カラムを抽出
   - ページディレクトリからページ一覧を抽出

3. 乖離を検出
   - CLAUDE.mdに記載があるが実装にない（過剰記載）
   - 実装にあるがCLAUDE.mdに記載がない（未記載）
   - 記載と実装の内容が異なる（不一致）

4. 不足セクションを検出
   - 上記テーブルのセクションがCLAUDE.mdに存在するか確認

5. レポートを作成
   - docs/sdd/reports/claude-md-sync/[YYYY-MM-DD].md

6. ★ ユーザー承認 ★

7. CLAUDE.mdを更新
```

## ユーザー承認フロー

```text
CLAUDE.md同期チェックが完了しました。

【検出された乖離】
- 未記載API: X件
- 未記載サービス: X件
- DBスキーマ不一致: X件
- 過剰記載（実装に存在しない）: X件
- 不足セクション: X件

詳細レポートを確認し、以下の対応を選択してください：

A) すべての乖離をCLAUDE.mdに反映
B) 項目ごとに個別に対応を選択
C) 今回は修正せずレポートのみ保存
```

## 乖離の優先度判定

| 優先度 | 条件 | 対応 |
|--------|------|------|
| High | 必須セクションの欠落（API Endpoints, DB Schema, Services, Environment Variables） | セクション新規作成 |
| High | 未記載API（3件以上） | 即座に追記 |
| Medium | 推奨セクションの欠落（Pages, WebSocket Message Types, State Machines, Business Rules） | 計画的にセクション作成 |
| Medium | 未記載サービス | 計画的に追記 |
| Medium | DBスキーマ不一致 | 実装を確認して更新 |
| Low | 過剰記載（削除済み機能） | 確認後に削除 |

## アーカイブ時のCLAUDE.md同期との違い

| 観点 | CLAUDE.md同期（機能5） | アーカイブ時CLAUDE.md同期（機能3） |
|------|----------------------|----------------------------------|
| トリガー | ユーザーが定期チェックとして実行 | アーカイブ実行時に自動で付随 |
| 比較対象 | CLAUDE.md vs 実装コード | SDD設計書 → CLAUDE.mdへの転記 |
| 目的 | 既存記載の正確性を検証 | 完了プロジェクトの仕様を転記 |
| 頻度 | 大規模実装後、リリース前 | プロジェクト完了時 |

## レポートテンプレート

実装同期チェックレポート（`../assets/templates/sync_report_template_ja.md`）の「CLAUDE.md乖離詳細」セクションを使用します。
