---
skill_name: planner_skill
description: Generates structured execution plans from task descriptions and routes them based on action types (file-only vs external actions requiring approval)
version: 1.0.0
required_permissions:
  - file_read
  - file_write
  - file_move
external_dependencies: []
requires_approval: false
error_handling:
  retry_strategy: none
  max_retries: 0
  fallback_action: Log error and move task back to Needs_Action with error details in frontmatter
rollback_procedure: Delete generated plan file and restore task to original state in Needs_Action folder
---

# Planner Skill

**Purpose**: Analyze tasks and generate structured execution plans with routing logic.

## Execution Logic

1. **Read task file** from Needs_Action folder
   - Parse YAML frontmatter for metadata (id, title, priority, status)
   - Extract markdown content body for task requirements

2. **Analyze task requirements**
   - Identify required actions from task description
   - Classify actions as file operations or external actions
   - Determine if human approval is needed

3. **Generate plan structure**
   - Create unique plan ID (same as task ID)
   - Write clear objective statement
   - Break down into ordered execution steps
   - Identify potential risks and failure modes
   - Document rollback procedure

4. **Set approval flag**
   - `requires_approval = true` if any step involves:
     - send_email action
     - post_facebook action
   - `requires_approval = false` if only file operations:
     - file_read, file_write, file_move, file_delete

5. **Route plan to appropriate folder**
   - If `requires_approval = true` → move to Pending_Approval/
   - If `requires_approval = false` → move to Plans/

6. **Log plan generation**
   - Record timestamp, task ID, plan ID, routing decision
   - Log to mcp_server/logs/reasoning-loop.log

7. **Update task status**
   - Set task status to "planned"
   - Add plan_id reference to task frontmatter

## Input Format

**Task File** (Markdown with YAML frontmatter):

```yaml
---
id: "20260215-143000-send-weekly-report"
title: "Send weekly report to team"
status: "triaged"
created_at: "2026-02-15T14:30:00Z"
updated_at: "2026-02-15T14:30:00Z"
priority: "P2"
source: "manual"
---

# Task: Send weekly report to team

Send the weekly project status report to the team via email.

**Recipients**: team@example.com
**Subject**: Weekly Project Status - Week of Feb 15
**Content**: Include completed tasks, blockers, and next week's priorities.
```

## Output Format

**Plan File** (Markdown with YAML frontmatter):

```yaml
---
id: "20260215-143000-send-weekly-report"
task_id: "20260215-143000-send-weekly-report"
objective: "Send weekly project status report to team@example.com"
requires_approval: true
created_at: "2026-02-15T14:35:00Z"
execution_status: "pending"
---

# Execution Plan: Send weekly report to team

## Steps

1. **Read completed tasks from Done folder** (action_type: file_read)
   - Parameters: folder="/Done", date_range="2026-02-08 to 2026-02-15"
   - Expected outcome: List of completed tasks with titles and dates

2. **Compose email content** (action_type: file_write)
   - Parameters: template="weekly_report", data=completed_tasks
   - Expected outcome: Formatted email body with task summary

3. **Send email via MCP** (action_type: send_email)
   - Parameters: to="team@example.com", subject="Weekly Project Status - Week of Feb 15", body=<composed_content>
   - Expected outcome: Email delivered successfully

## Risks

- Email delivery failure due to SMTP server issues
- Recipient email address may be invalid
- Email content may be incomplete if Done folder is empty

## Rollback Procedure

If email sending fails:
1. Log error details in plan frontmatter
2. Move plan back to Pending_Approval with error message
3. Notify human via pending_approval_watcher
4. Human can modify recipient or retry

## Action Preview

**Email Preview**:
- To: team@example.com
- Subject: Weekly Project Status - Week of Feb 15
- Body: (first 500 chars)
  "Hi team, here's our weekly project status update..."
```

## Examples

### Example 1: File-only task

**Input**: Task requesting file organization
```
Move all completed tasks from last week to archive folder
```

**Output**: Plan routed to /Plans with file_move actions, requires_approval=false

### Example 2: Email task

**Input**: Task requesting email notification
```
Send project update email to stakeholders@example.com
```

**Output**: Plan routed to /Pending_Approval with send_email action, requires_approval=true

### Example 3: Facebook post task

**Input**: Task requesting social media post
```
Post announcement about new product launch to Facebook Page
```

**Output**: Plan routed to /Pending_Approval with post_facebook action, requires_approval=true

## Edge Cases

- **Empty task content**: Log error, move task back to Inbox with error message
- **Malformed YAML frontmatter**: Attempt to parse, or flag for human review
- **Ambiguous action type**: Default to requires_approval=true for safety
- **Multiple external actions**: Set requires_approval=true, include all action previews
- **Task already has plan**: Check if plan exists, avoid duplicate generation
- **Missing required fields**: Add defaults (priority=P3, source=manual)
