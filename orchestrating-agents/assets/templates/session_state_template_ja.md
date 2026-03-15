# セッション状態
更新日時: {{YYYY-MM-DDTHH:MM:SS}}

## 親セッション
status: {{active | paused | completed}}
current_task: {{現在処理中のタスクまたはキュー管理}}
mission_path: .orchestrating-agents/mission.md

## 子セッション
- name: {{child-name}}
  agent_id: {{agent_id}}
  status: {{active | completed | failed | paused}}
  task: [{{TASK-XXX}}]
  worktree_branch: {{worktree/child-name or N/A}}
  workorder_path: .orchestrating-agents/workorders/{{TASK-XXX}}.md

## 孫セッション
- parent: {{child-name}}
  agent_id: {{agent_id}}
  status: {{active | completed | failed}}
  work: {{TASK-XXX-subtask-id}}
  worktree_branch: {{worktree/worker-XXX or N/A}}
