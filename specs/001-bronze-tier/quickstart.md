# Quickstart Guide: Bronze Tier AI Employee

**Version**: 1.0.0
**Date**: 2026-02-12
**Audience**: End users setting up and using Bronze Tier

## Overview

Bronze Tier AI Employee is a minimal local AI assistant that manages tasks through an Obsidian vault using folder-based state management. This guide will help you set up and start using the system.

---

## Prerequisites

Before you begin, ensure you have:

- **Windows 10+** (current Bronze Tier target platform)
- **Python 3.11+** installed and in PATH
- **Claude Code CLI** installed and authenticated
- **Obsidian vault** at `E:\AI_Employee_Vault` (or adjust paths accordingly)
- **Git** (optional, recommended for version control)

---

## Setup

### Step 1: Create Vault Structure

Create the required folders in your Obsidian vault:

```powershell
# Navigate to vault
cd E:\AI_Employee_Vault

# Create folders
mkdir Inbox, Needs_Action, Plans, Done, .watcher
```

### Step 2: Create Initial Files

Create `Dashboard.md` in vault root:

```markdown
# Dashboard

**Last Updated**: 2026-02-12T00:00:00

## Task Counts

- **Inbox**: 0 tasks
- **Needs Action**: 0 tasks
- **Plans**: 0 plans
- **Done**: 0 completed

## Recent Activity

No activity yet.

## System Status

- **Watcher**: not started
- **Vault Path**: E:\AI_Employee_Vault
```

Create `Company_Handbook.md` in vault root:

```markdown
# Company Handbook

## Project Context

Bronze Tier AI Employee - a minimal local AI assistant for task management.

## Task Guidelines

When processing tasks:
- Read task description carefully
- Generate structured plans with clear steps
- Include acceptance criteria for verification
- Ask clarifying questions if requirements are ambiguous

## Quality Standards

All plans must include:
- Clear goal statement
- Numbered steps with acceptance criteria
- Testable outcomes

## Communication Style

- Be concise and actionable
- Use bullet points for clarity
- Avoid jargon unless necessary
```

### Step 3: Install Python Dependencies

```powershell
# Create virtual environment (recommended)
cd E:\AI_Employee_Vault\.watcher
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install watchdog python-frontmatter pyyaml
```

### Step 4: Create Watcher Script

Create `E:\AI_Employee_Vault\.watcher\watcher.py`:

```python
import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT_PATH = Path("E:/AI_Employee_Vault")
INBOX = VAULT_PATH / "Inbox"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
LOCK_FILE = VAULT_PATH / ".watcher" / "watcher.lock"

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)
        dest = NEEDS_ACTION / source.name

        # Handle collision
        if dest.exists():
            timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
            dest = NEEDS_ACTION / f"{source.stem}-{timestamp}{source.suffix}"

        # Move file
        shutil.move(str(source), str(dest))
        print(f"[{datetime.now().isoformat()}] Moved: {source.name} -> Needs_Action/")

def acquire_lock():
    if LOCK_FILE.exists():
        print("ERROR: Watcher already running (lock file exists)")
        return False
    LOCK_FILE.write_text(str(os.getpid()))
    return True

def release_lock():
    LOCK_FILE.unlink(missing_ok=True)

if __name__ == "__main__":
    import os

    if not acquire_lock():
        exit(1)

    try:
        print(f"Starting watcher on {INBOX}")
        print("Press Ctrl+C to stop")

        event_handler = InboxHandler()
        observer = Observer()
        observer.schedule(event_handler, str(INBOX), recursive=False)
        observer.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping watcher...")
    finally:
        observer.join()
        release_lock()
        print("Watcher stopped")
```

### Step 5: Create Start Script

Create `E:\AI_Employee_Vault\.watcher\start-watcher.ps1`:

```powershell
# Start Bronze Tier Watcher
$venvPath = "E:\AI_Employee_Vault\.watcher\venv\Scripts\python.exe"
$scriptPath = "E:\AI_Employee_Vault\.watcher\watcher.py"

Write-Host "Starting Bronze Tier Watcher..." -ForegroundColor Green
& $venvPath $scriptPath
```

---

## Usage

### Starting the Watcher

Open PowerShell and run:

```powershell
cd E:\AI_Employee_Vault\.watcher
.\start-watcher.ps1
```

You should see:
```
Starting watcher on E:\AI_Employee_Vault\Inbox
Press Ctrl+C to stop
```

Leave this terminal open. The watcher will run in the foreground.

### Creating a Task

1. Create a new Markdown file in `Inbox/` folder:

**Example: `Inbox/task-001.md`**

```markdown
---
id: task-001
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
- Watcher script tested
```

2. Within 5 seconds, the watcher will move it to `Needs_Action/`

3. Check the watcher console for confirmation:
```
[2026-02-12T14:30:00] Moved: task-001.md -> Needs_Action/
```

### Processing a Task

1. Open a new terminal (keep watcher running in first terminal)

2. Run Claude CLI to generate a plan:

```powershell
claude "Read the task file at E:\AI_Employee_Vault\Needs_Action\task-001.md and generate a structured plan. The plan must include: Goal (clear statement), Steps (numbered list with acceptance criteria), Acceptance Criteria (checkboxes), and Questions (if clarification needed). Save the plan to E:\AI_Employee_Vault\Plans\plan-001.md with matching ID. Reference Company_Handbook.md for context."
```

3. Claude will create `Plans/plan-001.md` with structured content

4. Review the plan in Obsidian or any text editor

### Completing a Task

After you've completed the work described in the task:

```powershell
claude "Mark task E:\AI_Employee_Vault\Needs_Action\task-001.md as complete. Update frontmatter: set status='done', set completed=2026-02-12, set updated=2026-02-12. Move the file to E:\AI_Employee_Vault\Done\. If a corresponding plan exists in Plans folder, move it to Done as well. Then update Dashboard.md."
```

The task (and plan) will move to `Done/` folder.

### Checking System Status

View the Dashboard:

```powershell
claude "Scan the folders in E:\AI_Employee_Vault (Inbox, Needs_Action, Plans, Done) and update Dashboard.md with: Task Counts (count of .md files in each folder), Recent Activity (last 10 file operations from watcher log if available), System Status (watcher running status, last event timestamp, vault path). Use ISO 8601 timestamps."
```

Then open `Dashboard.md` in Obsidian to see current state.

---

## Common Workflows

### Workflow 1: Simple Task (No Plan Needed)

1. Drop task in Inbox → Watcher moves to Needs_Action
2. Do the work manually
3. Run completion command → Task moves to Done

### Workflow 2: Complex Task (Plan Required)

1. Drop task in Inbox → Watcher moves to Needs_Action
2. Run "Process Task" command → Plan created in Plans
3. Review plan, do the work
4. Run completion command → Task and plan move to Done

### Workflow 3: Batch Processing

1. Drop multiple tasks in Inbox
2. Watcher moves all to Needs_Action
3. Run "List Tasks" to see what's pending
4. Process tasks one by one with Claude CLI

---

## Troubleshooting

### Watcher Won't Start

**Error**: "Watcher already running (lock file exists)"

**Solution**:
```powershell
# Remove stale lock file
rm E:\AI_Employee_Vault\.watcher\watcher.lock

# Restart watcher
.\start-watcher.ps1
```

### File Not Moving from Inbox

**Check**:
1. Is watcher running? (Check terminal)
2. Is file a valid format? (Any file type works, but .md recommended)
3. Check watcher console for errors

### Claude Command Not Working

**Check**:
1. Is Claude Code CLI installed? Run `claude --version`
2. Are paths absolute? (Use full paths like `E:\AI_Employee_Vault\...`)
3. Are quotes correct? (Use double quotes for command string)

### Dashboard Out of Sync

**Solution**: Regenerate Dashboard with update command (see "Checking System Status" above)

### Task Frontmatter Malformed

**Solution**: Claude will handle gracefully, but you can manually fix:
```yaml
---
id: task-001
title: My Task
status: needs_action
created: 2026-02-12
updated: 2026-02-12
---
```

---

## Tips & Best Practices

1. **Keep watcher running**: Start it in the morning, stop at end of day
2. **Use descriptive task titles**: Makes Dashboard more useful
3. **Add priority tags**: Helps with triage
4. **Review plans before executing**: Claude's plans are suggestions
5. **Update Dashboard regularly**: Run update command after major changes
6. **Backup vault with git**: `git init` in vault root, commit regularly
7. **Use Obsidian for viewing**: Better markdown rendering than text editors

---

## What's Next?

After mastering Bronze Tier:

- **Silver Tier**: Adds MCP servers, automated dashboard updates, task dependencies
- **Gold Tier**: Adds external integrations (email, calendar, APIs)

But for now, focus on the Bronze Tier fundamentals: file drops, manual processing, folder-based state.

---

## Quick Reference

### Folder States

- `Inbox/` - New tasks (watcher monitors)
- `Needs_Action/` - Ready for processing
- `Plans/` - Generated plans
- `Done/` - Completed tasks

### Key Commands

```powershell
# Process task
claude "Read task at [PATH] and generate plan..."

# Complete task
claude "Mark task [PATH] as complete..."

# Update dashboard
claude "Scan folders and update Dashboard.md..."

# List tasks
claude "List all tasks in [FOLDER]..."
```

### File Structure

```
task-NNN.md (frontmatter + description)
plan-NNN.md (frontmatter + Goal/Steps/Criteria)
Dashboard.md (counts + activity)
Company_Handbook.md (context for AI)
```

---

## Support

For issues or questions:
- Check constitution: `.specify/memory/constitution.md`
- Check spec: `specs/001-bronze-tier/spec.md`
- Check plan: `specs/001-bronze-tier/plan.md`

---

**Version History**:
- 1.0.0 (2026-02-12): Initial Bronze Tier quickstart
