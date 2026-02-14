# Research: Bronze Tier AI Employee

**Phase**: 0 - Outline & Research
**Date**: 2026-02-12
**Purpose**: Resolve technical unknowns and document architectural decisions

## Research Questions

### Q1: File System Watcher Implementation

**Question**: What is the best approach for implementing a reliable file system watcher on Windows that monitors a single directory and moves files?

**Research Findings**:

**Decision**: Use Python `watchdog` library with `FileSystemEventHandler`

**Rationale**:
- Cross-platform support (works on Windows, macOS, Linux)
- Mature library with active maintenance (10+ years, 6k+ stars)
- Event-driven architecture matches Bronze Tier requirements
- Simple API for monitoring specific directories
- Built-in debouncing prevents duplicate events
- No external dependencies beyond Python standard library

**Alternatives Considered**:
- **Windows-specific `ReadDirectoryChangesW`**: Rejected - not cross-platform, requires C bindings
- **Polling with `os.listdir()`**: Rejected - inefficient, high CPU usage, delayed detection
- **PowerShell `FileSystemWatcher`**: Rejected - requires PowerShell runtime, harder to test

**Implementation Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Move file from Inbox to Needs_Action
            pass
```

---

### Q2: YAML Frontmatter Handling

**Question**: How should we parse and update YAML frontmatter in Markdown files reliably?

**Research Findings**:

**Decision**: Use `python-frontmatter` library for parsing, manual string manipulation for updates

**Rationale**:
- `python-frontmatter` is the de facto standard for Python (1k+ stars)
- Preserves content structure and formatting
- Handles edge cases (missing frontmatter, malformed YAML)
- Simple API: `frontmatter.load(file)` returns metadata dict + content
- For updates, use string replacement to avoid reformatting entire file

**Alternatives Considered**:
- **PyYAML + manual parsing**: Rejected - error-prone, must handle delimiters manually
- **markdown-it-py**: Rejected - overkill for simple frontmatter needs
- **regex-only approach**: Rejected - fragile, fails on nested YAML structures

**Implementation Pattern**:
```python
import frontmatter

# Read
post = frontmatter.load('task.md')
metadata = post.metadata  # dict
content = post.content    # string

# Update
post['status'] = 'completed'
post['updated'] = '2026-02-12'
with open('task.md', 'w') as f:
    f.write(frontmatter.dumps(post))
```

---

### Q3: File Collision Handling

**Question**: How should we handle filename collisions when moving files between folders?

**Research Findings**:

**Decision**: Append ISO 8601 timestamp to filename on collision

**Rationale**:
- Preserves all files (no data loss)
- Timestamp provides chronological ordering
- Human-readable format
- Deterministic (no random suffixes)
- Matches spec requirement (FR-014)

**Alternatives Considered**:
- **Overwrite existing**: Rejected - data loss risk
- **Numeric suffix (file-1.md, file-2.md)**: Rejected - requires scanning directory, race conditions
- **UUID suffix**: Rejected - not human-readable, harder to debug

**Implementation Pattern**:
```python
from pathlib import Path
from datetime import datetime

def safe_move(source: Path, dest_dir: Path) -> Path:
    dest = dest_dir / source.name
    if dest.exists():
        timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
        stem = source.stem
        suffix = source.suffix
        dest = dest_dir / f"{stem}-{timestamp}{suffix}"
    source.rename(dest)
    return dest
```

---

### Q4: Dashboard Update Strategy

**Question**: How should Dashboard.md be updated when task state changes?

**Research Findings**:

**Decision**: Scan folders on-demand, regenerate Dashboard sections atomically

**Rationale**:
- Folder scan is single source of truth (matches Principle IV)
- No separate state tracking needed
- Atomic file write prevents corruption
- Simple implementation (no event queue or state machine)
- Performance acceptable for Bronze Tier scale (~100 tasks)

**Alternatives Considered**:
- **Event-driven updates**: Rejected - adds complexity, requires state tracking
- **Incremental updates**: Rejected - risk of drift between Dashboard and actual folder state
- **Watcher updates Dashboard**: Rejected - violates separation of concerns (watcher only moves files)

**Implementation Pattern**:
```python
def update_dashboard(vault_path: Path):
    inbox_count = len(list((vault_path / 'Inbox').glob('*.md')))
    needs_action_count = len(list((vault_path / 'Needs_Action').glob('*.md')))
    plans_count = len(list((vault_path / 'Plans').glob('*.md')))
    done_count = len(list((vault_path / 'Done').glob('*.md')))

    dashboard_content = f"""# Dashboard

## Task Counts
- Inbox: {inbox_count}
- Needs Action: {needs_action_count}
- Plans: {plans_count}
- Done: {done_count}

## Recent Activity
[Last 10 state changes from watcher log]
"""

    # Atomic write
    temp = vault_path / 'Dashboard.md.tmp'
    temp.write_text(dashboard_content)
    temp.replace(vault_path / 'Dashboard.md')
```

---

### Q5: Single Watcher Instance Enforcement

**Question**: How do we prevent multiple watcher instances from running concurrently?

**Research Findings**:

**Decision**: Use PID file (lock file) with process validation

**Rationale**:
- Standard Unix/Windows pattern for single-instance processes
- Simple to implement with `pathlib` and `os.getpid()`
- Handles crashes gracefully (stale PID detection)
- No external dependencies
- Matches Principle V (Single Watcher Architecture)

**Alternatives Considered**:
- **Named mutex (Windows)**: Rejected - platform-specific, requires ctypes
- **Socket binding**: Rejected - overkill, requires network stack
- **No enforcement**: Rejected - violates constitution

**Implementation Pattern**:
```python
import os
from pathlib import Path

def acquire_lock(lock_file: Path) -> bool:
    if lock_file.exists():
        pid = int(lock_file.read_text())
        # Check if process still running
        try:
            os.kill(pid, 0)  # Signal 0 checks existence
            return False  # Lock held by running process
        except OSError:
            pass  # Stale lock, proceed

    lock_file.write_text(str(os.getpid()))
    return True

def release_lock(lock_file: Path):
    lock_file.unlink(missing_ok=True)
```

---

### Q6: Claude CLI Command Structure

**Question**: What command structure should Claude CLI workflows use for task processing?

**Research Findings**:

**Decision**: Custom Claude Code prompts invoked via `claude` CLI with explicit file paths

**Rationale**:
- Claude Code CLI supports custom prompts and file context
- Explicit file paths ensure vault boundary enforcement
- User maintains full control (manual invocation)
- No custom CLI tool needed (uses existing Claude Code)
- Matches Principle III (Manual Trigger Model)

**Command Examples**:
```bash
# Process task from Needs_Action
claude "Read the task file at E:\AI_Employee_Vault\Needs_Action\task-001.md and generate a structured plan with Goal, Steps, and Acceptance Criteria. Save the plan to E:\AI_Employee_Vault\Plans\plan-001.md"

# Update Dashboard
claude "Scan the folders in E:\AI_Employee_Vault (Inbox, Needs_Action, Plans, Done) and update Dashboard.md with current task counts and recent activity"

# Complete task
claude "Move E:\AI_Employee_Vault\Plans\task-001.md to E:\AI_Employee_Vault\Done\ and add completion timestamp to frontmatter"
```

**Alternatives Considered**:
- **Custom Python CLI**: Rejected - adds complexity, requires maintenance
- **Shell scripts**: Rejected - less flexible than Claude's natural language understanding
- **Obsidian plugins**: Rejected - requires JavaScript, violates file-system-only principle

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Watcher | Python watchdog | 3.0+ | Cross-platform, event-driven, mature |
| Frontmatter | python-frontmatter | 1.0+ | Standard library, preserves formatting |
| File Operations | pathlib | stdlib | Type-safe, cross-platform paths |
| AI Processing | Claude Code CLI | current | Manual trigger, vault-scoped |
| Testing | pytest | 7.0+ | Industry standard, simple fixtures |
| Process Management | PID file | custom | Single instance enforcement |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Watcher crashes | Medium | Low | User restarts manually; no data loss (state in files) |
| File collision | Low | Low | Timestamp suffix prevents overwrite |
| Malformed YAML | Medium | Low | python-frontmatter handles gracefully; log warning |
| Multiple watchers | Low | Medium | PID file enforcement prevents |
| Vault boundary violation | Low | High | Explicit path validation in all operations |
| Dashboard drift | Low | Low | Regenerate from folder scan (single source of truth) |

---

## Open Questions

None. All technical unknowns resolved.

---

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md (Task File, Plan File, Dashboard structure)
- Create contracts/cli-commands.md (Claude CLI command specifications)
- Create quickstart.md (Setup and usage guide)
