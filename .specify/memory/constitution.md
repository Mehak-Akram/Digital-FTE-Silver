# Personal AI Employee Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: [TEMPLATE] → 1.0.0
Rationale: Initial constitution establishment for Bronze Tier architecture

Modified Principles:
- Created 6 new principles from template placeholders
- Established Bronze Tier architectural constraints
- Defined operational boundaries and governance model

Added Sections:
- Core Principles (6 principles)
- Bronze Tier Architecture Constraints
- Operational Model
- Governance

Templates Requiring Updates:
- ✅ constitution.md (this file)
- ⚠ .specify/templates/plan-template.md (pending validation)
- ⚠ .specify/templates/spec-template.md (pending validation)
- ⚠ .specify/templates/tasks-template.md (pending validation)

Follow-up TODOs: None
-->

## Core Principles

### I. File System Only Operations

The AI MUST interact with the system exclusively through file system operations within the designated Obsidian vault. No external API calls, network requests, or system calls beyond file I/O are permitted in Bronze Tier.

**Rationale**: This constraint ensures predictable, auditable behavior and eliminates security risks associated with external integrations. All actions leave a traceable file system footprint.

### II. Vault Boundary Enforcement

All file operations MUST occur within the Obsidian vault directory (`E:\AI_Employee_Vault`). The AI MUST NOT read, write, modify, or delete files outside this boundary.

**Rationale**: Strict boundary enforcement prevents accidental data corruption, maintains system integrity, and provides a clear security perimeter for AI operations.

### III. Manual Trigger Model

Task processing MUST be initiated manually via Claude CLI commands. No autonomous background loops, scheduled tasks, or self-triggering mechanisms are permitted in Bronze Tier.

**Rationale**: Manual triggering ensures human oversight for every AI action, preventing runaway processes and maintaining user control over system behavior.

### IV. Folder-Based State Management

System state MUST be represented through folder location and structure. State transitions follow the canonical flow:
- `/Inbox` → New items requiring triage
- `/Needs_Action` → Triaged items awaiting execution
- `/Plans` → Items with execution plans ready for implementation
- `/Done` → Completed items

File movement between folders represents state changes. No external state databases or registries are permitted.

**Rationale**: Folder-based state is human-readable, version-controllable, and requires no additional infrastructure. Users can understand system state at a glance through file explorer.

### V. Single Watcher Architecture

Only ONE file system watcher process may run concurrently. The watcher's sole responsibility is detecting new files in `/Inbox` and notifying the user.

**Rationale**: A single watcher minimizes resource usage and complexity. Multiple watchers create race conditions and state synchronization issues.

### VI. No Cloud or External Services

Bronze Tier MUST operate entirely locally. Prohibited:
- Cloud storage synchronization during AI operations
- External API calls (email, messaging, web services)
- Browser automation
- Network-dependent features

**Rationale**: Local-only operation ensures privacy, eliminates network dependencies, and provides a stable foundation before introducing external integrations in higher tiers.

## Bronze Tier Architecture Constraints

**AI Logic**: Claude Code (Sonnet 4.5) via CLI interface

**Memory Layer**: Local Obsidian vault using Markdown files with YAML frontmatter for metadata

**Perception Layer**: Single file system watcher monitoring `/Inbox` for new `.md` files

**Action Layer**: File system operations only:
- Read files
- Write files
- Move files between folders
- Create/delete files within vault
- Modify file content and frontmatter

**Task Processing**: Manual invocation via `claude` CLI commands

**State Management**: Folder location represents state; no external databases

**Prohibited in Bronze Tier**:
- MCP servers
- External API integrations
- Autonomous loops ("Ralph Wiggum" mode)
- Background daemons beyond the single watcher
- Network operations
- System calls outside file I/O

## Operational Model

### Workflow

1. User creates task file in `/Inbox`
2. File watcher detects new file and notifies user
3. User manually invokes Claude CLI to process inbox
4. Claude reads task, generates plan, moves to appropriate folder
5. User reviews and approves actions
6. Claude executes approved actions, updates state via folder movement
7. Completed tasks move to `/Done`

### File Format Standards

All task and state files MUST use:
- Markdown format (`.md` extension)
- YAML frontmatter for structured metadata
- Human-readable content body
- ISO 8601 dates (YYYY-MM-DD)

### Error Handling

When operations fail:
- Claude MUST log error details in file frontmatter
- File MUST remain in current folder (no state transition)
- User MUST be notified with actionable error message
- No silent failures permitted

## Governance

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Version number MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles or sections added
   - **PATCH**: Clarifications, wording improvements, non-semantic changes
3. Amendment date MUST be recorded in `Last Amended` field
4. Sync Impact Report MUST be generated and prepended as HTML comment
5. Dependent templates MUST be reviewed and updated for consistency

### Compliance

- All features and implementations MUST comply with these principles
- Violations MUST be documented and justified in Architecture Decision Records (ADRs)
- Constitution supersedes all other guidance documents
- When principles conflict with implementation convenience, principles win

### Version Control

This constitution is version-controlled in Git. All amendments create a new commit with:
- Clear commit message describing the change
- Updated version number
- Sync Impact Report in file

### Review Cadence

Constitution MUST be reviewed:
- Before each tier upgrade (Bronze → Silver → Gold)
- When architectural constraints change
- When new capabilities are added
- Annually at minimum

**Version**: 1.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-12
