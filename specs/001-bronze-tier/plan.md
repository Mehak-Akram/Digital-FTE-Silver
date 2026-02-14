# Implementation Plan: Bronze Tier AI Employee

**Branch**: `001-bronze-tier` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-bronze-tier/spec.md`

## Summary

Build a minimal local AI Employee system that detects file drops in an Obsidian vault, enables manual AI-powered task planning via Claude Code CLI, and manages task lifecycle through folder-based state transitions. The system operates entirely locally with no external APIs, databases, or autonomous loops, adhering strictly to Bronze Tier constitutional constraints.

**Core Capabilities:**
- File system watcher monitors `/Inbox` and moves files to `/Needs_Action`
- Manual Claude CLI invocation processes tasks and generates structured plans
- Folder location represents task state (Inbox → Needs_Action → Plans → Done)
- Dashboard provides visibility into system state
- All data stored as Markdown files with YAML frontmatter

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: watchdog (file system monitoring), PyYAML (frontmatter parsing), pathlib (file operations)
**Storage**: File system only - Markdown files with YAML frontmatter in Obsidian vault
**Testing**: pytest (watcher unit tests), manual integration testing (Claude CLI workflows)
**Target Platform**: Windows 10+ (vault at E:\AI_Employee_Vault)
**Project Type**: Single project (Python watcher + vault structure + Claude CLI workflows)
**Performance Goals**: File detection <5 seconds, plan generation <30 seconds for typical tasks
**Constraints**: No external APIs, no databases, no network operations, single watcher instance, manual AI trigger only
**Scale/Scope**: Single user, local vault, ~100 tasks through full lifecycle without data loss

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I: File System Only Operations** ✅
- Watcher uses Python watchdog for file system events only
- Claude Code operates via file read/write within vault
- No external API calls, network requests, or system calls beyond file I/O

**Principle II: Vault Boundary Enforcement** ✅
- All operations confined to `E:\AI_Employee_Vault`
- Watcher monitors only vault subdirectories
- Claude CLI workflows explicitly scoped to vault paths

**Principle III: Manual Trigger Model** ✅
- Watcher only detects and moves files (no AI reasoning)
- Claude invoked manually via CLI commands
- No autonomous loops, scheduled tasks, or self-triggering

**Principle IV: Folder-Based State Management** ✅
- State transitions: Inbox → Needs_Action → Plans → Done
- Folder location is single source of truth
- No external state databases or registries

**Principle V: Single Watcher Architecture** ✅
- One Python watchdog process maximum
- Process management prevents multiple instances
- Simple console logging for user visibility

**Principle VI: No Cloud or External Services** ✅
- Local-only operation
- No cloud storage, email, messaging, or web services
- No browser automation or network-dependent features

**GATE STATUS**: ✅ PASSED - All constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-bronze-tier/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── cli-commands.md  # Claude CLI command specifications
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Vault Structure (E:\AI_Employee_Vault)

```text
E:\AI_Employee_Vault/
├── Dashboard.md              # System state overview and recent activity
├── Company_Handbook.md       # Project context and guidelines for AI
├── Inbox/                    # Drop zone for new tasks
├── Needs_Action/             # Tasks ready for AI processing
├── Plans/                    # Generated execution plans
├── Done/                     # Completed tasks archive
└── .watcher/                 # Watcher script and logs
    ├── watcher.py            # Python watchdog script
    ├── requirements.txt      # Python dependencies
    └── watcher.log           # Watcher activity log
```

### Source Code (repository root)

```text
src/
└── watcher/
    ├── __init__.py
    ├── watcher.py           # Main watchdog event handler
    ├── file_mover.py        # File operation utilities
    └── config.py            # Vault paths and settings

tests/
└── watcher/
    ├── test_watcher.py      # Watcher event handling tests
    └── test_file_mover.py   # File operation tests

scripts/
└── start-watcher.ps1        # PowerShell script to launch watcher
```

**Structure Decision**: Single project structure chosen because Bronze Tier has minimal components (watcher script + vault). No web frontend, no API server, no mobile app. The watcher is a simple Python script that runs as a foreground process. Claude Code operates directly on vault files via CLI, requiring no additional source structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles satisfied.
