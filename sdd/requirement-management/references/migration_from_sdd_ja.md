# SDDドキュメントからの移行手順

`requirements-defining` / `software-designing` / `sdd-document-management` は `requirement-management` へ統合され非推奨となった。既存の `docs/sdd/` を持つプロジェクトを移行する手順を示す。

## 目次

- [移行の全体像](#移行の全体像)
- [移行するもの・しないもの](#移行するものしないもの)
- [手順1: 準備](#手順1-準備)
- [手順2: ユーザーストーリーの移行](#手順2-ユーザーストーリーの移行)
- [手順3: 機能要件の移行](#手順3-機能要件の移行)
- [手順4: 非機能要件の移行](#手順4-非機能要件の移行)
- [手順5: 設計書の扱い](#手順5-設計書の扱い)
- [手順6: 検証と生成](#手順6-検証と生成)
- [手順7: 旧ドキュメントの停止](#手順7-旧ドキュメントの停止)
- [移行時によくある詰まり](#移行時によくある詰まり)

## 移行の全体像

```text
docs/sdd/requirements/index.md      → docs/requirements/generated/index.md（自動生成）
docs/sdd/requirements/stories/*.md  → docs/requirements/<ドメイン>.yaml の stories
docs/sdd/requirements/nfr/*.md      → docs/requirements/<ドメイン>.yaml の requirements（type: quality/constraint）
docs/sdd/design/                    → 移行しない（今後の設計はPR本文へ）
docs/sdd/tasks/                     → 移行しない（GitHub Issue運用のまま）
```

**一括変換はしない。** 要求1件ずつ、理由と検証手段を確認しながら移す。旧ドキュメントには `rationale.why`（なぜその要求が必要か）と `verification`（どう検証するか）が欠けていることが多く、そこを埋める作業が移行の本体である。

## 移行するもの・しないもの

| 旧 | 移行 | 理由 |
|----|------|------|
| ユーザーストーリー | する | `stories` として1対1で移せる |
| 機能要件（REQ-XXX） | する | `type: functional` の要求になる |
| 非機能要件（NFR） | する | `type: quality` / `constraint` になる。数値は `measures` に構造化する |
| 要件間の相互リンク | する | `depends_on` / `refines` に置き換える |
| 設計書 | **しない** | 設計は永続化しない運用に変わる。過去の設計書はアーカイブとして残すか削除する |
| タスク | **しない** | GitHub Issue運用は変更しない |
| 完了済み・廃止済みの要件 | する | `status: deprecated` の墓標として `retired_why` 付きで残す |

## 手順1: 準備

```bash
cd <プロジェクトルート>
mkdir -p docs/requirements
cp <スキルのパス>/assets/templates/glossary_template_ja.yaml docs/requirements/glossary.yaml
cp <スキルのパス>/assets/templates/requirements_registry_template_ja.yaml docs/requirements/<ドメイン>.yaml
cp <スキルのパス>/scripts/reqctl.py scripts/reqctl.py
```

移行対象の一覧を作る。

```bash
ls docs/sdd/requirements/stories/
ls docs/sdd/requirements/nfr/
```

## 手順2: ユーザーストーリーの移行

`docs/sdd/requirements/stories/US-XXX.md` の冒頭は、そのまま `stories` に対応する。

```markdown
<!-- 旧: US-001.md -->
**私は** 登録ユーザーとして
**〜したい** メールアドレスとパスワードでログインしたい
**なぜなら** 自分のデータにアクセスできる
```

```yaml
# 新
stories:
  - id: US-001
    as_a: 登録ユーザー
    i_want: メールアドレスとパスワードでログインしたい
    so_that: 自分のデータにアクセスできる
    status: active
```

IDは旧番号をそのまま引き継ぐ。`acceptance` は書かない（要求側の `stories` から自動導出される）。

## 手順3: 機能要件の移行

旧ストーリー内の「受入基準（EARS記法）」の各行が、1件の要求になる。

```markdown
<!-- 旧: US-001.md の受入基準 -->
- **REQ-001-001**: 利用者がログインボタンを押した時、システムはメールアドレスとパスワードの組を検証しなければならない
```

```yaml
# 新
requirements:
  - id: REQ-0001
    title: パスワード認証
    statement: 利用者がログインボタンを押した時、システムはメールアドレスとパスワードの組を検証しなければならない
    type: functional
    status: active
    priority: must
    stories: [US-001]
    rationale:
      why: ★ここを埋める（なぜこの要求が必要か。旧ドキュメントには通常書かれていない）
      source: ★誰の要望か / どの決定に由来するか
      decided_at: ★決定日（不明なら関係者に確認する。推測で埋めない）
    verification:
      - kind: test
        ref: ★対応する既存テスト（なければ実装して紐付ける）
```

- **IDは振り直す**: 旧 `REQ-001-001` のような階層IDは `REQ-0001` の連番に置き換える。対応表を移行PRの本文に残す
- **`rationale.why` が書けない要求は移さない**: 理由を言えない要求は、その時点で棚卸しの対象。関係者に確認するか、廃止候補として `status: deprecated` で移す
- **`verification` がない要求は `status: draft` で入れる**: `active` にすると `E-NOVERIFY` になる。テストを紐付けてから `active` にする

## 手順4: 非機能要件の移行

`nfr/performance.md` などの数値要件は、`measures` に構造化して初めて機械検証の対象になる。ここが移行の最大の価値。

```markdown
<!-- 旧: nfr/performance.md -->
- **NFR-PERF-001**: システムはログイン処理を2秒以内に完了しなければならない
```

```yaml
# 新
  - id: REQ-0002
    title: ログイン応答時間
    statement: 利用者がログインボタンを押した時、システムは2秒以内に認証結果を返さなければならない
    type: quality
    status: active
    priority: should
    stories: [US-001]
    rationale:
      why: ★その数値でなければならない理由（計測結果・規約・監査指摘など）
      source: ★出所
      decided_at: ★決定日
    measures:
      - subject: auth.login.latency   # 同じ測定対象は必ず同じ文字列にする
        op: "<="
        value: 2
        unit: s
    verification:
      - kind: metric
        ref: p95(auth.login.latency) <= 2s
```

`subject` の命名を揃えることが重要。同じ指標に別名を付けると矛盾検出が働かない。ドメイン全体で `<ドメイン>.<対象>.<指標>` に統一する。

「適切に」「十分な」といった曖昧語を含む要件は、移行時に測定可能な条件へ書き換える。書き換えられないものは、要件として成立していない可能性が高い。

## 手順5: 設計書の扱い

`docs/sdd/design/` は移行しない。次のいずれかを選ぶ。

| 方針 | 手順 |
|------|------|
| アーカイブとして残す | `docs/sdd/design/` をそのまま置き、README に「過去の設計記録。現行の設計はPRを参照」と明記する |
| 削除する | Git履歴に残るため、必要時は履歴から参照する |

いずれの場合も、**今後の設計はPR本文に書く**。`assets/templates/pr_design_note_template_ja.md` を使う。設計内容をレジストリのYAMLに書き写してはならない（`rationale` に実現方式を書かない）。

## 手順6: 検証と生成

```bash
python3 scripts/reqctl.py validate --strict
python3 scripts/reqctl.py generate
```

移行直後は大量のエラー・警告が出る。次の順に潰す。

1. `E-RATIONALE`（理由なし）: 理由を確認して埋める。埋められないものは廃止候補
2. `E-NOVERIFY`（検証手段なし）: テストを紐付ける。まだないなら `status: draft` に落とす
3. `E-CONFLICT-*`（矛盾）: **移行の成果**。旧ドキュメントに埋もれていた矛盾が表面化したもの。どちらが正しいかを関係者に確認して解消する
4. `W-AMBIGUOUS` / `W-EARS`（曖昧・記法）: 要求文を書き直す
5. `W-ORPHAN-REQ`（ストーリー未紐付け）: ストーリーに紐付けるか `type: constraint` に見直す

矛盾が見つかった場合は、勝手に片方を選ばない。`references/change_workflow_ja.md` の変更フロー（承認ゲート付き）に乗せる。

## 手順7: 旧ドキュメントの停止

移行を終えて `validate --strict` が通ったら、旧ドキュメントの更新を止める。

1. `docs/sdd/requirements/index.md` の冒頭に移行済みの注記を入れる（または削除する）
2. CI に `reqctl.py validate` を追加する（`assets/templates/ci_req_lint_template.yml`）
3. プロジェクトの CLAUDE.md に「要求は `docs/requirements/` で管理する」と明記する

旧ドキュメントと新レジストリを**併存させたまま両方更新してはならない**。二重管理は必ずずれる。

## 移行時によくある詰まり

| 症状 | 原因と対処 |
|------|-----------|
| 理由が誰も分からない要件がある | 移行の価値が最も出る場面。関係者に確認し、答えが出なければ `status: deprecated` に落として `retired_why: 理由を追跡できず、必要性を確認できなかったため` と記録する |
| 数値要件が矛盾していると検出された | 旧ドキュメントでは別ファイルにあって気づけなかっただけ。承認フローに乗せて解消する |
| 1つの要件に複数の関心事が混ざっている | 分割する。旧IDを `superseded` にし、新しい複数の要求へ `supersedes: [旧ID]` を書く |
| 要件数が多くて一度に移せない | ドメイン単位で分割して移す。移行済みドメインだけCIの検査対象にし、段階的に広げる |
| ストーリーに紐付かない要件が大量にある | 多くは `type: constraint`（システム全体の制約）に該当する。`type` を見直せば `W-ORPHAN-REQ` は消える |
