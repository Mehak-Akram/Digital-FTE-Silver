# Feature Specification: Bronze Tier AI Employee

**Feature Branch**: `001-bronze-tier`
**Created**: 2026-02-12
**Status**: Draft
**Input**: "Create the Bronze Tier specification for the Personal AI Employee project. Build a minimal local AI Employee that can detect file drops, generate task plans, and mark tasks as completed using a local Obsidian vault."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Intake and Triage (Priority: P1) 🎯 MVP

A user drops a new task file into the Inbox folder. The system detects the file, moves it to Needs_Action, and notifies the user that a new task is ready for processing.

**Why this priority**: This is the entry point for all work. Without reliable task intake, no other functionality can operate. This establishes the perception layer and basic state management.

**Independent Test**: Drop a markdown file into `/Inbox`. Verify the file appears in `/Needs_Action` within seconds and the original is removed from `/Inbox`.

**Acceptance Scenarios**:

1. **Given** `/Inbox` is empty, **When** user creates `task-001.md` in `/Inbox`, **Then** file appears in `/Needs_Action` within 5 seconds and is removed from `/Inbox`
2. **Given** multiple files are dropped simultaneously, **When** 5 files are created in `/Inbox`, **Then** all 5 files appear in `/Needs_Action` in order of creation
3. **Given** a non-markdown file is dropped, **When** user creates `document.pdf` in `/Inbox`, **Then** file is moved to `/Needs_Action` (system accepts all file types)

---

### User Story 2 - Task Planning (Priority: P2)

A user manually invokes Claude Code to process tasks in Needs_Action. Claude reads the task content, interprets the requirements, generates a structured plan, and saves it to the Plans folder.

**Why this priority**: This is the core AI reasoning capability. It transforms unstructured task descriptions into actionable plans. Required for the system to provide value beyond simple file movement.

**Independent Test**: Place a task file in `/Needs_Action` with content "Research Bronze Tier architecture options". Run Claude CLI command. Verify a corresponding plan file appears in `/Plans` with structured sections (Goal, Steps, Acceptance Criteria).

**Acceptance Scenarios**:

1. **Given** `task-001.md` exists in `/Needs_Action` with task description, **When** user runs `claude process-task task-001.md`, **Then** `plan-001.md` is created in `/Plans` with Goal, Steps, and Acceptance Criteria sections
2. **Given** task contains ambiguous requirements, **When** Claude processes the task, **Then** plan includes clarifying questions in a "Questions" section
3. **Given** task is already processed, **When** user runs process command again, **Then** system updates existing plan with timestamp rather than creating duplicate

---

### User Story 3 - Dashboard Updates (Priority: P3)

When tasks move through the workflow (Inbox → Needs_Action → Plans → Done), the Dashboard.md file automatically updates to reflect current system state, showing counts and recent activity.

**Why this priority**: Provides visibility into system state without requiring users to manually check folders. Enhances usability but system functions without it.

**Independent Test**: Move a task from `/Needs_Action` to `/Done`. Open `Dashboard.md`. Verify the "Completed Tasks" count incremented and the task appears in "Recent Activity".

**Acceptance Scenarios**:

1. **Given** Dashboard shows 3 tasks in Needs_Action, **When** a new task arrives in `/Needs_Action`, **Then** Dashboard updates to show 4 tasks within 10 seconds
2. **Given** a task moves to `/Done`, **When** user checks Dashboard, **Then** "Recent Activity" section shows the completed task with timestamp
3. **Given** Dashboard.md is deleted, **When** next state change occurs, **Then** Dashboard.md is recreated with current system state

---

### User Story 4 - Task Completion (Priority: P4)

After a user completes work on a task, they manually invoke Claude to mark it complete. Claude moves the task file from its current location to the Done folder and updates all tracking documents.

**Why this priority**: Completes the task lifecycle. Provides closure and historical record. Lower priority because tasks can be manually moved to Done if needed.

**Independent Test**: Place a task in `/Plans`. Run completion command. Verify task moves to `/Done`, Dashboard updates, and task metadata includes completion timestamp.

**Acceptance Scenarios**:

1. **Given** `task-001.md` exists in `/Plans`, **When** user runs `claude complete-task task-001.md`, **Then** file moves to `/Done` with completion timestamp in frontmatter
2. **Given** task has associated plan file, **When** task is completed, **Then** both task and plan files move to `/Done` together
3. **Given** task is already in `/Done`, **When** completion command runs, **Then** system reports "already completed" without error

---

### Edge Cases

- What happens when `/Inbox` receives a file with the same name as an existing file in `/Needs_Action`? System appends timestamp to filename to prevent overwrite.
- How does system handle corrupted or empty markdown files? System moves file to `/Needs_Action` but logs warning in Dashboard about unreadable content.
- What if user manually moves files between folders while watcher is running? System respects manual moves and updates Dashboard accordingly on next scan.
- What if Dashboard.md or Company_Handbook.md are accidentally deleted? System recreates Dashboard.md on next state change; Company_Handbook.md must be manually restored (system logs warning).
- What happens when watcher process crashes? User must manually restart watcher; no data loss occurs as all state is in file system.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor `/Inbox` folder for new file creation events
- **FR-002**: System MUST move newly detected files from `/Inbox` to `/Needs_Action` within 5 seconds of detection
- **FR-003**: System MUST preserve original file content and metadata during folder transitions
- **FR-004**: System MUST support manual invocation of Claude Code via CLI commands
- **FR-005**: System MUST read task files from `/Needs_Action` and extract task requirements
- **FR-006**: System MUST generate structured plan files with Goal, Steps, and Acceptance Criteria sections
- **FR-007**: System MUST save generated plans to `/Plans` folder with corresponding task identifier
- **FR-008**: System MUST update `Dashboard.md` to reflect current task counts across all folders
- **FR-009**: System MUST record recent activity (last 10 state changes) in Dashboard
- **FR-010**: System MUST move completed tasks to `/Done` folder on completion command
- **FR-011**: System MUST add completion timestamp to task frontmatter when marking complete
- **FR-012**: System MUST maintain `Company_Handbook.md` as reference context for task interpretation
- **FR-013**: System MUST use YAML frontmatter in all task and plan files for structured metadata
- **FR-014**: System MUST handle filename collisions by appending ISO timestamp
- **FR-015**: System MUST operate entirely within vault boundary (no external file access)
- **FR-016**: System MUST NOT make external API calls or network requests
- **FR-017**: System MUST NOT use database systems (all state in file system)
- **FR-018**: System MUST NOT run autonomous background reasoning loops
- **FR-019**: Watcher process MUST be single-instance (no concurrent watchers)
- **FR-020**: System MUST log errors to Dashboard when file operations fail

### Key Entities

- **Task File**: Markdown file representing a work item with YAML frontmatter (id, title, status, created, updated) and body content describing requirements
- **Plan File**: Markdown file containing structured execution plan with Goal, Steps, Acceptance Criteria, and Questions sections
- **Dashboard**: Central status file showing task counts per folder, recent activity log, and system health indicators
- **Company Handbook**: Reference document containing project context, principles, and guidelines for task interpretation
- **Folder State**: Physical folder location representing task lifecycle stage (Inbox, Needs_Action, Plans, Done)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can drop a task file and see it in Needs_Action within 5 seconds without manual intervention
- **SC-002**: User can invoke Claude to generate a task plan and receive structured output in under 30 seconds for typical tasks (under 500 words)
- **SC-003**: Dashboard accurately reflects system state with zero discrepancies after any state change
- **SC-004**: System processes 100 tasks through full lifecycle (Inbox → Done) without data loss or corruption
- **SC-005**: User can understand current system state by reading Dashboard alone without checking individual folders
- **SC-006**: System operates continuously for 7 days with watcher running without requiring restart or intervention
- **SC-007**: All task files retain complete original content through all folder transitions (verified by checksum)
- **SC-008**: User can complete common workflows (drop task, generate plan, mark complete) using only 3 CLI commands

## Assumptions

- Users are comfortable with command-line interfaces for manual task processing
- Obsidian vault is already configured and accessible at `E:\AI_Employee_Vault`
- Users will manually restart watcher process if it crashes (no auto-recovery in Bronze Tier)
- Task files are primarily text-based markdown (system accepts other formats but cannot interpret them)
- Single user environment (no concurrent access or file locking concerns)
- Windows environment with PowerShell available for watcher script
- Claude Code CLI is installed and authenticated
- Users understand folder-based state model and will not manually create conflicting states

## Out of Scope

- Multi-user collaboration or concurrent access
- Real-time notifications (beyond watcher console output)
- Task scheduling or deadline management
- Email integration or external communication
- Authentication or access control
- Cloud synchronization or backup
- Mobile access or web interface
- Task dependencies or project management features
- Time tracking or productivity analytics
- Integration with external tools (Jira, Trello, etc.)
- Automated task execution (all execution is manual)
- Natural language processing beyond basic task interpretation
- File versioning or change history (beyond git if user chooses)

## Dependencies

- **Obsidian**: Vault must exist and be accessible for file operations
- **Claude Code CLI**: Must be installed and authenticated for AI processing
- **PowerShell**: Required for file system watcher script (Windows)
- **Git**: Optional but recommended for version control of vault contents
- **Node.js**: May be required depending on watcher implementation choice

## Constraints

- **Bronze Tier Boundary**: No external APIs, no MCP servers, no cloud services
- **File System Only**: All operations must use file I/O within vault boundary
- **Manual Trigger**: No autonomous loops; all AI processing requires explicit user invocation
- **Single Watcher**: Only one file system watcher process may run concurrently
- **Local Only**: No network operations permitted
- **No Database**: All state must be represented in file system structure
- **Constitution Compliance**: Must adhere to all principles in `.specify/memory/constitution.md`
