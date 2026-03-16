# セルフレビューレポート

## 概要

| 項目 | 内容 |
|------|------|
| レビュー日時 | {YYYY-MM-DD HH:MM:SS} |
| 対象ブランチ | {branch_name} |
| ベースブランチ | {base_branch} |
| 差分取得方法 | {diff_method}（例: ブランチ間差分、ステージ済みのみ） |
| 変更ファイル数 | {file_count} |
| 変更行数 | +{additions} / -{deletions} |

## レビュー結果マトリクス

| 観点 | critical | warning | suggestion | nitpick |
|------|----------|---------|------------|---------|
| セキュリティ | {count} | {count} | {count} | {count} |
| ドキュメント乖離 | {count} | {count} | {count} | {count} |
| 可読性・複雑度 | {count} | {count} | {count} | {count} |
| ライブラリ選定 | {count} | {count} | {count} | {count} |
| 変更説明 | {count} | {count} | {count} | {count} |
| 既知脆弱性 | {count} | {count} | {count} | {count} |
| **合計** | **{total}** | **{total}** | **{total}** | **{total}** |

## 総合判定

- [ ] 問題なし（指摘なし）
- [ ] 軽微な指摘のみ（suggestion/nitpickのみ）
- [ ] 修正推奨（warningあり）
- [ ] 修正必須（criticalあり）

## 指摘一覧

### Critical

<!-- critical指摘がない場合は「なし」と記載 -->

#### F-{NNN}: {指摘タイトル}

- **ファイル**: `{file_path}:{line}`
- **カテゴリ**: {category}
- **問題**: {問題の説明}
- **推奨修正**: {修正方針の説明}

<details>
<summary>AI向け修正情報</summary>

```json
{
  "id": "F-{NNN}",
  "file": "{file_path}",
  "line": "{line}",
  "severity": "critical",
  "category": "{category}",
  "title": "{指摘タイトル}",
  "fix": {
    "old_text": "{置換対象のコードテキスト}",
    "new_text": "{置換後のコードテキスト}",
    "description": "{補足説明}"
  },
  "fix_strategy": {
    "approach": "{推奨する修正アプローチ}",
    "alternatives": ["{代替案}"],
    "impact": "{影響範囲}",
    "effort": "small | medium | large"
  },
  "context": "{該当行の前後3行程度のコード断片}",
  "rule": "{関連ルール}",
  "verification_hint": "{修正後の確認ポイント}"
}
```

</details>

### Warning

<!-- warning指摘がない場合は「なし」と記載 -->

#### F-{NNN}: {指摘タイトル}

（criticalと同一形式）

### Suggestion

<!-- suggestion指摘がない場合は「なし」と記載 -->

#### F-{NNN}: {指摘タイトル}

（criticalと同一形式）

### Nitpick

<!-- nitpick指摘がない場合は「なし」と記載 -->

#### F-{NNN}: {指摘タイトル}

（criticalと同一形式）

## 修正対応状況

<!-- 修正を適用した場合に記入 -->

| ID | 指摘 | 重大度 | 対応状況 | コメント |
|----|------|--------|---------|---------|
| F-{NNN} | {指摘タイトル} | {severity} | {resolved/unresolved/wont-fix} | {コメント} |

## 変更ファイル一覧

| ファイル | 変更行数 | カテゴリ | 優先度 |
|---------|---------|---------|--------|
| `{file_path}` | +{add}/-{del} | {category} | {高/中/低} |

---

<!-- 再レビュー時に使用するセクション -->

## 再レビュー（前回レポートとの比較）

<!-- 再レビュー時のみ記入。初回レビュー時はこのセクション全体を削除する -->

### 前回レビュー情報

| 項目 | 内容 |
|------|------|
| 前回レビュー日時 | {previous_review_date} |
| 前回レポートファイル | {previous_report_file} |

### 前回指摘の修正状況

| ID | 指摘 | 重大度 | 状態 | コメント |
|----|------|--------|------|---------|
| F-{NNN} | {指摘タイトル} | {severity} | {resolved/partially-resolved/unresolved/wont-fix/regressed} | {コメント} |

### 修正状況サマリー

- resolved: {count}件
- partially-resolved: {count}件
- unresolved: {count}件
- wont-fix: {count}件
- regressed: {count}件

### 新規指摘

（上記「指摘一覧」セクションと同一形式で記載）
