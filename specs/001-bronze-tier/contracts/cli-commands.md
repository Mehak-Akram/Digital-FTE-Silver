# CLI Commands Contract: Bronze Tier AI Employee

**Phase**: 1 - Design & Contracts
**Date**: 2026-02-12
**Purpose**: Define Claude CLI command specifications for Bronze Tier operations

## Overview

Bronze Tier uses manual Claude Code CLI invocation for all AI-powered operations. This document specifies the command patterns, expected inputs, and outputs for each workflow.

---

## Command: Process Task

**Purpose**: Read a task from Needs_Action, generate a structured plan, and save to Plans folder

**Invocation Pattern**:
```bash
claude "Read the task file at E:\AI_Employee_Vault\Needs_Action\[TASK_FILE] and generate a structured plan. The plan must include: Goal (clear statement), Steps (numbered list with acceptance criteria), Acceptance Criteria (checkboxes), and Questions (if clarification needed). Save the plan to E:\AI_Employee_Vault\Plans\[PLAN_FILE] with matching ID. Reference Company_Handbook.md for context."
```

**Input**:
- Task file in `/Needs_Action` with YAML frontmatter and task description
- Company_Handbook.md for context

**Output**:
- Plan file in `/Plans` with structured sections (Goal, Steps, Acceptance Criteria, Questions)
- Plan frontmatter includes `task_id` reference

**Success Criteria**:
- Plan file created with valid YAML frontmatter
- All required sections present (Goal, Steps, Acceptance Criteria)
- Plan ID matches task ID (task-001 → plan-001)
- Plan is actionable and testable

**Example**:
```bash
claude "Read the task file at E:\AI_Employee_Vault\Needs_Action\task-001.md and generate a structured plan. The plan must include: Goal (clear statement), Steps (numbered list with acceptance criteria), Acceptance Criteria (checkboxes), and Questions (if clarification needed). Save the plan to E:\AI_Employee_Vault\Plans\plan-001.md with matching ID. Reference Company_Handbook.md for context."
```

**Error Handling**:
- If task file not found: Report error, do not create plan
- If task has malformed YAML: Process content, create minimal frontmatter
- If plan file already exists: Update existing plan with timestamp

---

## Command: Update Dashboard

**Purpose**: Scan vault folders and regenerate Dashboard.md with current state

**Invocation Pattern**:
```bash
claude "Scan the folders in E:\AI_Employee_Vault (Inbox, Needs_Action, Plans, Done) and update Dashboard.md with: Task Counts (count of .md files in each folder), Recent Activity (last 10 file operations from watcher log if available), System Status (watcher running status, last event timestamp, vault path). Use ISO 8601 timestamps."
```

**Input**:
- Folder contents (Inbox, Needs_Action, Plans, Done)
- Optional: Watcher log for recent activity

**Output**:
- Updated Dashboard.md with current counts and activity

**Success Criteria**:
- Counts match actual folder contents
- Timestamps in ISO 8601 format
- Dashboard is human-readable

**Example**:
```bash
claude "Scan the folders in E:\AI_Employee_Vault (Inbox, Needs_Action, Plans, Done) and update Dashboard.md with: Task Counts (count of .md files in each folder), Recent Activity (last 10 file operations from watcher log if available), System Status (watcher running status, last event timestamp, vault path). Use ISO 8601 timestamps."
```

**Error Handling**:
- If Dashboard.md missing: Create new Dashboard
- If folders missing: Report error, create folders
- If watcher log unavailable: Skip Recent Activity section

---

## Command: Complete Task

**Purpose**: Mark a task as complete, move to Done folder, update frontmatter

**Invocation Pattern**:
```bash
claude "Mark task E:\AI_Employee_Vault\Needs_Action\[TASK_FILE] as complete. Update frontmatter: set status='done', set completed=[TODAY], set updated=[TODAY]. Move the file to E:\AI_Employee_Vault\Done\. If a corresponding plan exists in Plans folder, move it to Done as well. Then update Dashboard.md."
```

**Input**:
- Task file in `/Needs_Action` or `/Plans`
- Optional: Corresponding plan file

**Output**:
- Task file moved to `/Done` with updated frontmatter
- Optional: Plan file moved to `/Done`
- Updated Dashboard.md

**Success Criteria**:
- Task file in `/Done` with `status='done'` and `completed` date
- Original file removed from source folder
- Dashboard reflects new counts

**Example**:
```bash
claude "Mark task E:\AI_Employee_Vault\Needs_Action\task-001.md as complete. Update frontmatter: set status='done', set completed=2026-02-12, set updated=2026-02-12. Move the file to E:\AI_Employee_Vault\Done\. If a corresponding plan exists in Plans folder, move it to Done as well. Then update Dashboard.md."
```

**Error Handling**:
- If task already in Done: Report "already completed", no action
- If task not found: Report error
- If plan move fails: Complete task anyway, log warning

---

## Command: List Tasks

**Purpose**: Display all tasks in a specific folder with summary information

**Invocation Pattern**:
```bash
claude "List all tasks in E:\AI_Employee_Vault\[FOLDER]\ showing: filename, title (from frontmatter), status, created date, priority (if present). Format as a table."
```

**Input**:
- Folder path (Inbox, Needs_Action, Plans, Done)

**Output**:
- Markdown table with task summaries

**Success Criteria**:
- All .md files in folder included
- Table is properly formatted
- Frontmatter parsed correctly

**Example**:
```bash
claude "List all tasks in E:\AI_Employee_Vault\Needs_Action\ showing: filename, title (from frontmatter), status, created date, priority (if present). Format as a table."
```

**Expected Output**:
```markdown
| Filename | Title | Status | Created | Priority |
|----------|-------|--------|---------|----------|
| task-001.md | Research Bronze Tier | needs_action | 2026-02-12 | high |
| task-002.md | Setup watcher | needs_action | 2026-02-12 | medium |
```

**Error Handling**:
- If folder empty: Report "No tasks found"
- If malformed frontmatter: Show filename, mark other fields as "N/A"

---

## Command: Create Task

**Purpose**: Create a new task file with proper frontmatter structure

**Invocation Pattern**:
```bash
claude "Create a new task file in E:\AI_Employee_Vault\Inbox\ with title '[TITLE]' and description '[DESCRIPTION]'. Generate frontmatter with: id (next available task-NNN), title, status='inbox', created=[TODAY], updated=[TODAY]. Use proper YAML frontmatter format."
```

**Input**:
- Task title
- Task description

**Output**:
- New task file in `/Inbox` with valid frontmatter

**Success Criteria**:
- Unique task ID assigned
- Valid YAML frontmatter
- File created in Inbox

**Example**:
```bash
claude "Create a new task file in E:\AI_Employee_Vault\Inbox\ with title 'Setup Python environment' and description 'Install Python 3.11, pip, and virtualenv for Bronze Tier development'. Generate frontmatter with: id (next available task-NNN), title, status='inbox', created=2026-02-12, updated=2026-02-12. Use proper YAML frontmatter format."
```

**Error Handling**:
- If ID collision: Append timestamp to filename
- If Inbox folder missing: Create folder first

---

## Command: Review Plan

**Purpose**: Read a plan file and provide feedback or suggestions

**Invocation Pattern**:
```bash
claude "Review the plan at E:\AI_Employee_Vault\Plans\[PLAN_FILE]. Check for: clear goal statement, actionable steps, testable acceptance criteria, missing details. Provide feedback and suggestions for improvement."
```

**Input**:
- Plan file in `/Plans`

**Output**:
- Feedback text with suggestions

**Success Criteria**:
- Feedback is constructive and specific
- Identifies gaps or ambiguities
- Suggests concrete improvements

**Example**:
```bash
claude "Review the plan at E:\AI_Employee_Vault\Plans\plan-001.md. Check for: clear goal statement, actionable steps, testable acceptance criteria, missing details. Provide feedback and suggestions for improvement."
```

**Error Handling**:
- If plan not found: Report error
- If plan malformed: Provide feedback on structure issues

---

## Command Patterns Summary

| Command | Primary Action | Input Folder | Output Folder | Updates Dashboard |
|---------|---------------|--------------|---------------|-------------------|
| Process Task | Generate plan | Needs_Action | Plans | No |
| Update Dashboard | Scan folders | All | N/A | Yes |
| Complete Task | Archive task | Needs_Action | Done | Yes |
| List Tasks | Display summary | Any | N/A | No |
| Create Task | New task file | N/A | Inbox | No |
| Review Plan | Provide feedback | Plans | N/A | No |

---

## Common Parameters

**Vault Path**: `E:\AI_Employee_Vault` (hardcoded for Bronze Tier)

**Date Format**: ISO 8601 (YYYY-MM-DD)

**Timestamp Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SS)

**File Extension**: `.md` (Markdown)

**Frontmatter Delimiter**: `---` (YAML)

---

## Validation Rules

All commands must:
- Operate only within vault boundary (`E:\AI_Employee_Vault`)
- Use absolute paths (no relative paths)
- Preserve file content integrity
- Update timestamps on modifications
- Handle missing files gracefully
- Log errors to console (no silent failures)

---

## Future Enhancements (Silver Tier)

- Batch operations (process all tasks in Needs_Action)
- Task dependencies (block/unblock based on other tasks)
- Automated dashboard updates (triggered by file events)
- Task templates (predefined task structures)
- Search and filter (find tasks by criteria)

These are explicitly out of scope for Bronze Tier.
