# 報告フォーマットテンプレート

## 子→親 報告フォーマット

---

## Task Report
task_id: {{TASK-XXX}}
status: {{completed | failed | escalation_required}}
duration: {{所要時間}}

## Results
{{成果物概要}}

### 作成/変更ファイル
{{ファイルリスト}}

### コミット
{{コミットハッシュとメッセージ}}

## Quality Check
- 受入基準: {{すべて達成 | 一部未達成（詳細）}}
- テスト: {{パス | 失敗（詳細）}}
- lint: {{パス | 警告あり（詳細）}}

## Escalations (if any)
- type: {{approval_needed | risk_warning | blocker}}
  description: {{内容}}
  options: {{選択肢（該当する場合）}}

## Next Steps
{{推奨される次のアクション}}

---

## 孫→子 報告フォーマット

---

## Work Report
subtask_id: {{TASK-XXXa}}
status: {{completed | failed | needs_retry}}

## Changes
{{変更ファイルリスト}}

## Acceptance Criteria Status
- [ ] {{基準1}}: {{達成/未達成}}
- [ ] {{基準2}}: {{達成/未達成}}

## Issues (if any)
{{問題の詳細}}
