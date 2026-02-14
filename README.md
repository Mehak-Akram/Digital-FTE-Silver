# Bronze Tier AI Employee

A minimal local AI assistant that manages tasks through an Obsidian vault using folder-based state management.

## Overview

Bronze Tier AI Employee is a file-based task management system that combines:
- **File System Watcher**: Automatically detects new tasks dropped in the Inbox
- **Claude Code CLI**: Manually processes tasks and generates structured plans
- **Folder-Based State**: Task lifecycle represented by folder location
- **Local-Only Operation**: No external APIs, databases, or cloud services

## Architecture

**Tier**: Bronze (Local-only, manual trigger)

**Components**:
- Python file system watcher (watchdog library)
- Obsidian vault for task storage
- Claude Code CLI for AI processing
- Markdown files with YAML frontmatter

**State Flow**:
```
Inbox → Needs_Action → Plans → Done
```

## Prerequisites

- **Python 3.11+** installed and in PATH
- **Claude Code CLI** installed and authenticated
- **Windows 10+** (current target platform)
- **Obsidian** (optional, for viewing vault)

## Installation

### 1. Clone or Navigate to Vault

```powershell
cd E:\AI_Employee_Vault
```

### 2. Verify Folder Structure

The following folders should exist:
- `Inbox/` - Drop zone for new tasks
- `Needs_Action/` - Tasks ready for processing
- `Plans/` - Generated execution plans
- `Done/` - Completed tasks
- `.watcher/` - Watcher script and logs

### 3. Install Python Dependencies

```powershell
# Virtual environment already created
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Starting the Watcher

Open PowerShell and run:

```powershell
.\scripts\start-watcher.ps1
```

You should see:
```
Starting Bronze Tier Watcher
Monitoring: E:\AI_Employee_Vault\Inbox
Press Ctrl+C to stop
--------------------------------------------------
```

**Keep this terminal open** - the watcher runs in the foreground.

### Creating a Task

1. Create a Markdown file in the `Inbox/` folder:

**Example: `Inbox/my-task.md`**

```markdown
---
id: task-002
title: Setup development environment
status: inbox
created: 2026-02-12
updated: 2026-02-12
priority: high
---

# Task Description

Setup Python development environment for Bronze Tier watcher implementation.

## Requirements

- Python 3.11+
- watchdog library
- python-frontmatter library

## Deliverables

- Working Python environment
- All dependencies installed
```

2. Within 5 seconds, the watcher will move it to `Needs_Action/`

3. Check the watcher console for confirmation:
```
[2026-02-12T14:30:00] Moved: my-task.md -> Needs_Action/
```

### Processing a Task with Claude

Open a **new terminal** (keep watcher running in first terminal):

```powershell
claude "Read the task file at E:\AI_Employee_Vault\Needs_Action\task-001.md and generate a structured plan. The plan must include: Goal (clear statement), Steps (numbered list with acceptance criteria), Acceptance Criteria (checkboxes), and Questions (if clarification needed). Save the plan to E:\AI_Employee_Vault\Plans\plan-001.md with matching ID. Reference Company_Handbook.md for context."
```

Claude will create `Plans/plan-001.md` with structured content.

### Updating Dashboard

```powershell
claude "Scan the folders in E:\AI_Employee_Vault (Inbox, Needs_Action, Plans, Done) and update Dashboard.md with: Task Counts (count of .md files in each folder), Recent Activity (last 10 file operations from watcher log if available), System Status (watcher running status, last event timestamp, vault path). Use ISO 8601 timestamps."
```

### Completing a Task

```powershell
claude "Mark task E:\AI_Employee_Vault\Needs_Action\task-001.md as complete. Update frontmatter: set status='done', set completed=2026-02-12, set updated=2026-02-12. Move the file to E:\AI_Employee_Vault\Done\. If a corresponding plan exists in Plans folder, move it to Done as well. Then update Dashboard.md."
```

## File Structure

```
E:\AI_Employee_Vault/
├── Dashboard.md              # System state overview
├── Company_Handbook.md       # AI context and guidelines
├── Inbox/                    # Drop zone (watcher monitors)
├── Needs_Action/             # Tasks ready for processing
├── Plans/                    # Generated plans
├── Done/                     # Completed tasks
├── .watcher/                 # Watcher internals
│   ├── watcher.lock          # Single instance lock
│   └── watcher.log           # Activity log
├── src/watcher/              # Python source code
│   ├── __init__.py
│   ├── config.py             # Vault paths
│   ├── file_mover.py         # File operations
│   ├── lock_manager.py       # Single instance enforcement
│   └── watcher.py            # Main watcher
├── scripts/
│   └── start-watcher.ps1     # Watcher launcher
├── requirements.txt          # Python dependencies
└── venv/                     # Virtual environment
```

## Task File Format

All tasks use Markdown with YAML frontmatter:

```markdown
---
id: task-NNN
title: Task title
status: inbox | needs_action | done
created: YYYY-MM-DD
updated: YYYY-MM-DD
completed: YYYY-MM-DD  # Only when status=done
tags: [tag1, tag2]     # Optional
priority: high | medium | low  # Optional
---

# Task Description

[Task details in markdown]
```

## Plan File Format

Plans generated by Claude follow this structure:

```markdown
---
id: plan-NNN
task_id: task-NNN
title: Plan title
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | approved | completed
---

## Goal

[Clear statement of what this plan achieves]

## Steps

1. [First step with acceptance criteria]
2. [Second step with acceptance criteria]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Questions

[Optional: Clarifications needed]

## Notes

[Optional: Additional context]
```

## Troubleshooting

### Watcher Won't Start

**Error**: "Watcher already running (lock file exists)"

**Solution**:
```powershell
rm .watcher\watcher.lock
.\scripts\start-watcher.ps1
```

### File Not Moving from Inbox

**Check**:
1. Is watcher running? (Check terminal)
2. Is file in Inbox? (Check folder)
3. Check watcher console for errors

### Claude Command Not Working

**Check**:
1. Is Claude Code CLI installed? Run `claude --version`
2. Are paths absolute? (Use full paths like `E:\AI_Employee_Vault\...`)
3. Are quotes correct? (Use double quotes for command string)

## Bronze Tier Constraints

**What's Allowed**:
- ✅ File system operations within vault
- ✅ Manual Claude CLI invocation
- ✅ Folder-based state transitions
- ✅ Console logging
- ✅ Markdown files with YAML frontmatter

**What's Prohibited**:
- ❌ External API calls
- ❌ MCP servers
- ❌ Cloud services
- ❌ Autonomous background loops
- ❌ Database systems
- ❌ Network operations

## Development

### Running Tests

```powershell
venv\Scripts\activate
pytest tests/
```

### Project Structure

- `src/watcher/` - Core watcher implementation
- `tests/watcher/` - Unit tests
- `scripts/` - Utility scripts
- `specs/001-bronze-tier/` - Design documents

## References

- **Constitution**: `.specify/memory/constitution.md`
- **Specification**: `specs/001-bronze-tier/spec.md`
- **Implementation Plan**: `specs/001-bronze-tier/plan.md`
- **Data Model**: `specs/001-bronze-tier/data-model.md`
- **CLI Commands**: `specs/001-bronze-tier/contracts/cli-commands.md`
- **Quickstart Guide**: `specs/001-bronze-tier/quickstart.md`

## What's Next?

After mastering Bronze Tier:
- **Silver Tier**: Adds MCP servers, automated dashboard updates, task dependencies
- **Gold Tier**: Adds external integrations (email, calendar, APIs)

## License

Internal project - Bronze Tier AI Employee

## Version

**Bronze Tier**: 1.0.0
**Date**: 2026-02-12
