# 要求レジストリ データモデル仕様

## 目次

- [ファイル構成](#ファイル構成)
- [トップレベルキー](#トップレベルキー)
- [requirements（要求）](#requirements要求)
- [stories（ユーザーストーリー）](#storiesユーザーストーリー)
- [terms（用語）](#terms用語)
- [policy（ポリシー）](#policyポリシー)
- [矛盾検出のための構造化フィールド](#矛盾検出のための構造化フィールド)
- [記述例](#記述例)

## ファイル構成

`docs/requirements/` 配下の `*.yaml` / `*.yml` をすべて読み込んでマージする。`generated/` 配下は読み込まない。

ファイル分割は自由。ドメイン単位（`auth.yaml`、`billing.yaml`）を推奨する。IDはファイルをまたいで一意でなければならない。

## トップレベルキー

| キー | 型 | 説明 |
|------|-----|------|
| `requirements` | list | 要求の配列 |
| `stories` | list | ユーザーストーリーの配列 |
| `terms` | list | 用語定義の配列（`glossary.yaml` に置くことを推奨） |
| `policy` | map | 検査ポリシー（複数ファイルにあると後勝ちでマージ） |

## requirements（要求）

| フィールド | 必須 | 型 | 説明 |
|-----------|------|-----|------|
| `id` | 必須 | str | `REQ-0001` 形式。数字は3桁以上 |
| `title` | 必須 | str | 短い名前（一覧表示用） |
| `statement` | 必須 | str | EARS記法の要求文。「システムは〜しなければならない」を含める |
| `type` | 必須 | enum | `functional` / `quality` / `constraint` |
| `status` | 必須 | enum | `draft` / `active` / `deprecated` / `superseded` |
| `priority` | 必須 | enum | `must` / `should` / `could` / `wont` |
| `rationale` | 必須 | map | 理由（下記） |
| `stories` | 任意 | list[str] | 紐付くユーザーストーリーID。**ストーリーと要求を結ぶ唯一の場所** |
| `verification` | active時必須 | list[map] | 検証手段（下記） |
| `depends_on` | 任意 | list[str] | この要求が成立するために前提となる要求 |
| `refines` | 任意 | list[str] | 上位要求を具体化した要求である場合の親 |
| `supersedes` | 任意 | list[str] | この要求が置き換えた旧要求 |
| `conflicts_with` | 任意 | list[str] | 許容済みの衝突相手（双方に書く必要がある） |
| `measures` | 任意 | list[map] | 数値制約（矛盾検出用） |
| `asserts` | 任意 | list[map] | 「こうであること」の主張（矛盾検出用） |
| `forbids` | 任意 | list[map] | 「こうでないこと」の主張（矛盾検出用） |
| `terms` | 任意 | list[str] | 使用している用語集の語 |
| `tags` | 任意 | list[str] | 任意の分類 |
| `design_refs` | 任意 | list[str] | 設計を議論したPR・コメントのURL。**設計内容は書かない** |

### rationale（理由）

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `why` | 必須 | なぜこの要求が必要か。10文字以上。「〜のため」で終わる形が望ましい |
| `source` | 推奨 | 誰の要望か、どの決定・調査・監査指摘に由来するか |
| `decided_at` | 推奨 | `YYYY-MM-DD`。`policy.stale_days` を超えると鮮度警告が出る |
| `tradeoff` | 衝突宣言時に必須 | `conflicts_with` を宣言した場合の、衝突を許容する理由 |
| `retired_why` | 廃止時に必須 | `deprecated` / `superseded` にした理由 |
| `alternatives_rejected` | 任意 | 却下した代替案（list[str]） |

理由に**設計方針を書かない**。書くのは「なぜその要求が要るのか」であって「どう実現するか」ではない。

### verification（検証手段）

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `kind` | 必須 | `test` / `manual` / `metric` / `review` |
| `ref` | 必須 | `test` の場合は `tests/test_auth.py::test_login` 形式。それ以外は手順名や監視クエリ |

`kind: test` の `ref` は `validate --check-tests` で `::` より前のパスの実在を確認する。

## stories（ユーザーストーリー）

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `id` | 必須 | `US-001` 形式 |
| `as_a` | 必須 | ユーザーの種類 |
| `i_want` | 必須 | 目標・要望 |
| `so_that` | 必須 | 得られる価値 |
| `status` | 推奨 | `draft` / `active` / `done` / `dropped` |
| `rationale` | 任意 | ストーリーレベルの理由 |

`acceptance` は**書いてはならない**（`E-DUPLINK`）。受入要求は要求側の `stories` から導出され、`generated/traceability.md` に出力される。

## terms（用語）

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | 必須 | 正規の用語 |
| `definition` | 推奨 | 定義 |
| `aliases` | 任意 | 使ってはいけない言い換え。要求文に出現すると `W-TERM-ALIAS` |

## policy（ポリシー）

| キー | 既定値 | 説明 |
|------|--------|------|
| `ambiguous_words` | 「適切に」「適宜」ほか | 要求文に含めてはならない曖昧語のリスト |
| `multi_value_keys` | `[]` | 複数値を取ってよい `asserts` のキー。ここに入れた key は値の食い違いを矛盾としない |
| `stale_days` | `365` | `decided_at` からこの日数を超えると鮮度警告 |

## 矛盾検出のための構造化フィールド

要求文（自然言語）だけでは矛盾を機械判定できないため、**数値と事実だけを構造化して併記**する。要求文の意味を機械可読に落とした「影」であり、要求文と一致していなければならない。

### measures（数値制約）

```yaml
measures:
  - subject: auth.login.latency   # 測定対象の識別子。同じ対象は必ず同じ文字列にする
    op: "<="                      # < <= > >= == != のいずれか
    value: 2
    unit: s                       # 同一 subject で単位が混在すると判定をスキップして警告
```

同一 `subject` に対する制約の区間が空になると `E-CONFLICT-NUM`。

`subject` の命名は `<ドメイン>.<対象>.<指標>` を推奨（例: `auth.session.ttl`、`billing.invoice.retention`）。

### asserts / forbids（事実の主張）

```yaml
asserts:
  - key: auth.method              # 決定事項の識別子
    value: password
forbids:
  - key: storage.region
    value: us-east-1
```

- 同じ `key` に異なる `value` を主張する有効要求が2つあると `E-CONFLICT-FACT`
- ある `key=value` を `asserts` する要求と `forbids` する要求が同居すると `E-CONFLICT-FACT`
- 複数値が正当な場合（例: 対応する認証要素の列挙）は `policy.multi_value_keys` に登録する

## 記述例

```yaml
requirements:
  - id: REQ-0002
    title: ログイン応答時間
    statement: 利用者がログインボタンを押した時、システムは2秒以内に認証結果を返さなければならない
    type: quality
    status: active
    priority: should
    stories: [US-001]
    depends_on: [REQ-0001]
    conflicts_with: [REQ-0005]
    rationale:
      why: 3秒を超えると離脱率が倍増する自社計測結果があるため
      source: 2026-07 UX計測レポート
      decided_at: 2026-07-15
      tradeoff: 多要素認証の入力待ち時間は測定対象外とし、認証結果返却までで評価する
    measures:
      - subject: auth.login.latency
        op: "<="
        value: 2
        unit: s
    verification:
      - kind: metric
        ref: p95(auth.login.latency) <= 2s
    design_refs:
      - https://github.com/example/repo/pull/42#issuecomment-1234567890
```
