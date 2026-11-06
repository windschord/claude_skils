---
name: requirement-management
description: 要求・ユーザーストーリー・理由・用語・要求間の関係をYAMLレジストリで管理し、追加・変更・廃止のたびに要求間の整合性と矛盾を機械的に検証する。要求の追加/変更/削除、矛盾チェック、トレーサビリティ確認、ユーザーストーリーと受入条件の管理が必要な場合に使用する。設計は実装時にPR本文・GitHubコメントに書くだけで永続化しない運用を前提とする。requirements-defining / software-designing / sdd-document-management の移行先。Do NOT use for 設計書の作成・永続化（設計はPRに書く）。
metadata:
  version: "1.0.0"
---

# 要求管理スキル

要求（Requirement）とその理由（Rationale）を軸に、ユーザーストーリー・用語・要求間の関係までを永続化し、要求どうしの整合性・無矛盾性を機械検証で常に保ちます。設計ドキュメントは作りません。

## このスキルの前提

| 項目 | 方針 |
|------|------|
| 永続化するもの | 要求・ユーザーストーリー・理由・用語・要求間の関係のみ |
| 永続化しないもの | 設計書、アーキテクチャ図、API仕様、タスク詳細 |
| 設計の扱い | 実装時に必ず行うが、記録先はPR本文とGitHubコメントのみ（レジストリにはPRのURLだけ残す） |
| テストの合格条件 | すべての有効要求に検証手段があり、全ユーザーストーリーが要求で覆われていること |
| 削除の扱い | 物理削除は禁止。`deprecated` / `superseded` として理由付きで残す（墓標） |

このスキルは `requirements-defining` / `software-designing` / `sdd-document-management` の移行先です。これらは非推奨であり、併用は想定していません。既存の `docs/sdd/` からの移行手順は `references/migration_from_sdd_ja.md` を参照してください。

## ディレクトリ構成

```text
docs/requirements/
├── glossary.yaml            # 用語集＋ポリシー（曖昧語・多値キー・鮮度しきい値）
├── <ドメイン>.yaml           # 要求とストーリー（ファイル分割は自由）
└── generated/               # 自動生成（手で編集しない・レビュー対象）
    ├── index.md             # 全要求一覧＋墓標
    ├── traceability.md      # ストーリー→要求→検証 マトリクス
    └── graph.md             # Mermaid関係グラフ
```

## 中核ルール（破ってはならない不変条件）

1. **理由なき要求を作らない**: すべての要求に `rationale.why` が必須。
2. **リンクは片方向のみ**: ストーリーと要求の紐付けは要求側の `stories` にだけ書く。ストーリー側に `acceptance` を書くと二重管理となりエラー。
3. **検証不能な要求を残さない**: `status: active` の要求には `verification` が必須。
4. **削除せず廃止する**: 削除時は `status` を `deprecated` / `superseded` にし、`rationale.retired_why` を書く。
5. **矛盾は宣言するか解消する**: 数値・事実の衝突は、要求を直すか、双方に `conflicts_with` と `rationale.tradeoff` を書いて許容を明示する。
6. **生成物は手で書かない**: `generated/` は必ず `reqctl.py generate` で再生成する。生成結果は入力が同じなら常に同一になるため、CIで再生成して差分がないことを確認できる。

## コマンド

すべて `reqctl.py`（Python 3.9+ / PyYAML のみ）で実行します。

実行パスは導入方法によって変わります。初期化時にプロジェクトへコピーした場合は `scripts/reqctl.py`、スキルから直接実行する場合は `<スキルのパス>/sdd/requirement-management/scripts/reqctl.py` を指定します。以下はコピーした場合の例です（CI設定例も同じ前提）。

```bash
python3 scripts/reqctl.py validate                     # 検査（エラーがあれば exit 1）
python3 scripts/reqctl.py validate --strict            # 警告もエラー扱い（exit 2）
python3 scripts/reqctl.py validate --check-tests       # 検証手段のテストファイル存在も確認
python3 scripts/reqctl.py validate --json              # 機械処理用の出力
python3 scripts/reqctl.py generate                     # generated/ を再生成
python3 scripts/reqctl.py impact REQ-0002              # 変更前の影響範囲確認
python3 scripts/reqctl.py next-id req                  # 次の採番
python3 scripts/reqctl.py stats                        # 件数サマリ
```

`--dir` でレジストリの場所を変更できます（既定 `docs/requirements`）。

## ワークフロー

> **読み込みの原則**: テンプレートとリファレンスは、使用する直前に必要なものを1つだけ読み込む。手順の冒頭で一括して読み込まない。

### 0. 初期化（レジストリが存在しない場合）

1. `docs/requirements/` を作成する。
2. `assets/templates/glossary_template_ja.yaml` を読み込み、`glossary.yaml` としてコピーして用語を埋める。
3. `assets/templates/requirements_registry_template_ja.yaml` を読み込み、`<ドメイン>.yaml` としてコピーする。
4. `scripts/reqctl.py` をプロジェクトの `scripts/` にコピーするか、スキルのパスを直接実行する。
5. `validate` → `generate` を実行して初期状態を確定する。
6. `assets/templates/ci_req_lint_template.yml` を読み込み、CI設定を導入する。

### 1. 要求の追加

```text
ステップ 1/6: 情報分類（明示された情報／不明な情報を分ける）
ステップ 2/6: 不明点をユーザーに質問（推測で埋めない）
ステップ 3/6: 既存要求との衝突を先に調べる（同じ subject/key を持つ要求を impact で確認）
ステップ 4/6: next-id で採番し、要求とストーリーをYAMLに追記
ステップ 5/6: validate を実行し、エラーゼロになるまで修正
ステップ 6/6: generate で generated/ を更新し、差分をユーザーに提示して承認を得る
```

理由（`rationale.why`）が書けない要求は**追加しない**でユーザーに確認します。

### 2. 要求の変更

```text
ステップ 1/6: impact <ID> で影響範囲（被依存要求・ストーリー・テスト・同一subject）を取得
ステップ 2/6: change_proposal_template_ja.md を読み込み、変更提案レポートを作成
ステップ 3/6: ★ ユーザー承認 ★（必須ゲート）
ステップ 4/6: YAMLを変更し、rationale.why を更新（理由が変わったなら理由も書き換える）
ステップ 5/6: validate --strict を実行し、波及した矛盾をすべて解消
ステップ 6/6: generate → 差分提示
```

**要求の意味が変わる変更は、変更ではなく置換（supersede）です。** 影響が大きい場合は新IDを作り、旧要求を `superseded` にします。判断基準は `references/change_workflow_ja.md` を参照。

### 3. 要求の廃止・削除

行を消してはいけません。

```text
ステップ 1/5: impact <ID> で、その要求に依存している要求とストーリーを特定
ステップ 2/5: 依存元の扱いを決める（同時廃止／付け替え／置換）
ステップ 3/5: ★ ユーザー承認 ★
ステップ 4/5: status を deprecated（単純廃止）または superseded（置換）にし、rationale.retired_why を記入。
              置換の場合は新要求に supersedes: [旧ID] を書く
ステップ 5/5: validate → generate
```

### 4. 実装時（設計はここで行いPRに書く）

1. 実装対象の要求IDを確定する（`generated/traceability.md` から選ぶ）。
2. 設計を検討する。**設計内容はレジストリに書かない。**
3. `assets/templates/pr_design_note_template_ja.md` を読み込み、PR本文に設計ノートを書く。
4. 実装とテストを書き、テスト名を要求の `verification` に登録する。
5. `validate --check-tests` でテストの存在を確認する。
6. PRのURLを `design_refs` に追加する（URLのみ。設計内容は書かない）。設計判断が要求の理由そのものを変えた場合は、あわせて `rationale` を更新する。

詳細は `references/design_in_pr_ja.md` を参照。

### 5. 定期点検

リリース前や週次で `validate --strict` を実行し、警告（曖昧表現・用語ゆれ・重複疑い・理由の陳腐化）を棚卸しします。

## 検査項目の概要

| 分類 | 代表コード | 内容 |
|------|-----------|------|
| 構造 | E-SCHEMA / E-IDFMT / E-REF | 必須項目・ID書式・参照先の実在 |
| 理由 | E-RATIONALE / W-STALE | 理由の有無と鮮度 |
| ライフサイクル | E-SUPERSEDE / E-RETIRE / E-DEAD-REF | 廃止の整合、廃止済みへの参照禁止 |
| 矛盾 | E-CONFLICT-NUM / E-CONFLICT-FACT | 数値制約・事実主張の充足不能 |
| 循環 | E-CYCLE | 依存関係の循環 |
| カバレッジ | E-NOVERIFY / E-ORPHAN-US / W-ORPHAN-REQ | 検証手段とストーリー被覆 |
| 品質 | W-AMBIGUOUS / W-EARS / W-TERM-ALIAS / W-DUP | 曖昧表現・記法・用語ゆれ・重複疑い |

全コードと対処法は `references/consistency_rules_ja.md` を参照。

## ユーザー承認が必須の操作

- 要求の変更・廃止・置換
- 既存要求との衝突を `conflicts_with` で許容する判断
- 要求の優先度（`priority`）の変更
- レジストリの分割・移動などの構成変更

追加のみ・警告解消のみの場合は、差分提示で足ります。

## リソース

### スクリプト
- `scripts/reqctl.py`: 検証・生成・影響分析ツール

### テンプレート
- `assets/templates/requirements_registry_template_ja.yaml`: 要求レジストリ雛形
- `assets/templates/glossary_template_ja.yaml`: 用語集・ポリシー雛形
- `assets/templates/change_proposal_template_ja.md`: 変更提案レポート
- `assets/templates/pr_design_note_template_ja.md`: PR設計ノート
- `assets/templates/ci_req_lint_template.yml`: CI設定例

### リファレンス
- `references/data_model_ja.md`: YAMLスキーマ全仕様
- `references/consistency_rules_ja.md`: 検査コード一覧と対処法
- `references/change_workflow_ja.md`: 追加・変更・廃止の判断基準
- `references/design_in_pr_ja.md`: 設計をPRに閉じる運用
- `references/management_options_ja.md`: 管理方式の比較検討と採用理由
- `references/migration_from_sdd_ja.md`: 既存 docs/sdd/ からの移行手順
