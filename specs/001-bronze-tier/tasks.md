---
description: "Task list for Bronze Tier AI Employee implementation"
---

# Tasks: Bronze Tier AI Employee

**Input**: Design documents from `/specs/001-bronze-tier/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT requested in the specification. This is a manual integration testing approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Vault root**: E:\AI_Employee_Vault
- **Watcher source**: src/watcher/
- **Tests**: tests/watcher/
- **Scripts**: scripts/

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize vault structure and project foundation

- [x] T001 Create Obsidian vault folder structure at E:\AI_Employee_Vault with subdirectories: Inbox, Needs_Action, Plans, Done, .watcher
- [x] T002 Create Dashboard.md in E:\AI_Employee_Vault with initial template (Task Counts, Recent Activity, System Status sections)
- [x] T003 Create Company_Handbook.md in E:\AI_Employee_Vault with project context, task guidelines, quality standards, and communication style
- [x] T004 Initialize Python project structure with src/watcher/, tests/watcher/, and scripts/ directories
- [x] T005 Create requirements.txt in project root with dependencies: watchdog>=3.0.0, python-frontmatter>=1.0.0, pyyaml>=6.0, pytest>=7.0.0

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create Python virtual environment and install dependencies from requirements.txt
- [x] T007 [P] Create src/watcher/__init__.py as empty module initializer
- [x] T008 [P] Create src/watcher/config.py with vault path constants (VAULT_PATH, INBOX, NEEDS_ACTION, PLANS, DONE, LOCK_FILE)
- [x] T009 [P] Create src/watcher/file_mover.py with safe_move() function implementing collision handling via ISO 8601 timestamp suffix
- [x] T010 Create src/watcher/lock_manager.py with acquire_lock() and release_lock() functions using PID file for single instance enforcement

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Intake and Triage (Priority: P1) 🎯 MVP

**Goal**: Watcher detects files dropped in Inbox and moves them to Needs_Action within 5 seconds

**Independent Test**: Drop task-001.md into E:\AI_Employee_Vault\Inbox. Verify file appears in Needs_Action within 5 seconds and is removed from Inbox.

### Implementation for User Story 1

- [x] T011 [US1] Create src/watcher/watcher.py with InboxHandler class extending FileSystemEventHandler
- [x] T012 [US1] Implement on_created() method in InboxHandler to detect new files and call file_mover.safe_move()
- [x] T013 [US1] Implement main() function in watcher.py with Observer setup, lock acquisition, and keyboard interrupt handling
- [x] T014 [US1] Add console logging to watcher.py for file move events with ISO 8601 timestamps
- [x] T015 [US1] Create scripts/start-watcher.ps1 PowerShell script to activate venv and launch watcher.py
- [x] T016 [US1] Create .watcher/watcher.log file path in config.py for future logging enhancement
- [ ] T017 [US1] Test watcher with single file drop: Create test-task.md in Inbox, verify move to Needs_Action
- [ ] T018 [US1] Test watcher with multiple simultaneous files: Drop 5 files in Inbox, verify all move to Needs_Action
- [ ] T019 [US1] Test watcher with filename collision: Drop task-001.md when task-001.md already exists in Needs_Action, verify timestamp suffix added

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Watcher reliably moves files from Inbox to Needs_Action.

---

## Phase 4: User Story 2 - Task Planning (Priority: P2)

**Goal**: Claude CLI processes tasks from Needs_Action and generates structured plans in Plans folder

**Independent Test**: Place task-001.md in Needs_Action with description "Research Bronze Tier architecture". Run Claude CLI command. Verify plan-001.md appears in Plans with Goal, Steps, and Acceptance Criteria sections.

### Implementation for User Story 2

- [x] T020 [US2] Create sample task file E:\AI_Employee_Vault\Needs_Action\task-001.md with YAML frontmatter (id, title, status, created, updated) and task description
- [x] T021 [US2] Document Claude CLI command pattern in contracts/cli-commands.md for "Process Task" workflow with explicit vault paths
- [x] T022 [US2] Create plan template structure in data-model.md showing required sections: Goal, Steps, Acceptance Criteria, Questions, Notes
- [ ] T023 [US2] Test Claude CLI "Process Task" command: Run command to generate plan-001.md from task-001.md
- [ ] T024 [US2] Verify plan-001.md in E:\AI_Employee_Vault\Plans contains valid YAML frontmatter (id, task_id, title, created, updated, status)
- [ ] T025 [US2] Verify plan-001.md contains all required sections with structured content
- [ ] T026 [US2] Test plan update scenario: Run process command again on same task, verify plan updates with new timestamp
- [ ] T027 [US2] Test ambiguous task scenario: Create task with unclear requirements, verify plan includes Questions section

**Checkpoint**: At this point, User Story 2 should be fully functional. Claude can generate structured plans from task descriptions.

---

## Phase 5: User Story 3 - Dashboard Updates (Priority: P3)

**Goal**: Dashboard.md reflects current system state with task counts and recent activity

**Independent Test**: Move a task from Needs_Action to Done. Run Dashboard update command. Verify Dashboard shows updated counts and recent activity.

### Implementation for User Story 3

- [x] T028 [US3] Document Claude CLI command pattern in contracts/cli-commands.md for "Update Dashboard" workflow with folder scanning logic
- [x] T029 [US3] Create Dashboard template in data-model.md with sections: Last Updated timestamp, Task Counts (Inbox, Needs_Action, Plans, Done), Recent Activity (last 10 events), System Status
- [ ] T030 [US3] Test Dashboard update command: Run Claude CLI to scan folders and regenerate Dashboard.md
- [ ] T031 [US3] Verify Dashboard.md shows correct counts matching actual folder contents (count .md files in each folder)
- [ ] T032 [US3] Verify Dashboard.md uses ISO 8601 format for all timestamps
- [ ] T033 [US3] Test Dashboard recreation: Delete Dashboard.md, run update command, verify Dashboard recreated with current state
- [ ] T034 [US3] Test Dashboard with empty folders: Remove all tasks, run update command, verify Dashboard shows zero counts

**Checkpoint**: At this point, User Story 3 should be fully functional. Dashboard accurately reflects system state on demand.

---

## Phase 6: User Story 4 - Task Completion (Priority: P4)

**Goal**: Claude CLI marks tasks complete, moves them to Done folder, and updates frontmatter with completion timestamp

**Independent Test**: Place task-001.md in Needs_Action. Run completion command. Verify task moves to Done with status='done' and completed date in frontmatter.

### Implementation for User Story 4

- [x] T035 [US4] Document Claude CLI command pattern in contracts/cli-commands.md for "Complete Task" workflow with frontmatter update and file move logic
- [ ] T036 [US4] Create sample task in E:\AI_Employee_Vault\Needs_Action\task-002.md for completion testing
- [ ] T037 [US4] Test completion command: Run Claude CLI to mark task-002.md complete
- [ ] T038 [US4] Verify task-002.md moved to E:\AI_Employee_Vault\Done with updated frontmatter (status='done', completed=today, updated=today)
- [ ] T039 [US4] Test completion with associated plan: Create task-003.md and plan-003.md, run completion, verify both move to Done
- [ ] T040 [US4] Test completion of already-completed task: Run completion command on task in Done, verify "already completed" message
- [ ] T041 [US4] Test Dashboard update after completion: Run completion command, then update Dashboard, verify Done count incremented

**Checkpoint**: At this point, all user stories (US1-US4) should be independently functional. Complete task lifecycle works end-to-end.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and system robustness

- [ ] T042 [P] Test watcher crash recovery: Kill watcher process, verify lock file cleanup, restart watcher successfully
- [ ] T043 [P] Test malformed YAML frontmatter: Create task with invalid YAML, verify watcher moves file and logs warning
- [ ] T044 [P] Test empty file handling: Drop empty .md file in Inbox, verify watcher moves to Needs_Action without error
- [ ] T045 [P] Test non-markdown file handling: Drop .pdf file in Inbox, verify watcher moves to Needs_Action
- [ ] T046 [P] Test manual file moves: Manually move task between folders while watcher running, verify no conflicts
- [ ] T047 [P] Test missing Dashboard recovery: Delete Dashboard.md, trigger state change, verify Dashboard recreated
- [ ] T048 [P] Test missing Company_Handbook: Delete Company_Handbook.md, run Claude command, verify warning logged
- [ ] T049 [P] Document all Claude CLI commands in quickstart.md with examples and expected outputs
- [x] T050 [P] Create README.md in project root with setup instructions, usage guide, and troubleshooting section
- [ ] T051 Validate end-to-end workflow: Drop task in Inbox → Watcher moves → Claude processes → Claude completes → Dashboard updates
- [ ] T052 Validate 100-task stress test: Process 100 tasks through full lifecycle, verify no data loss or corruption

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P3): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 4 (P4): Can start after Foundational - No dependencies on other stories (independent)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (can test with manually placed files)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (can test with manually placed files)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent of US1/US2/US3 (can test with manually placed files)

### Within Each User Story

- US1: Config → File mover → Lock manager → Watcher → Start script → Testing
- US2: Sample task → CLI command docs → Plan template → Testing
- US3: CLI command docs → Dashboard template → Testing
- US4: CLI command docs → Sample task → Testing

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- Foundational tasks T007, T008, T009 can run in parallel (different files)
- Once Foundational phase completes, all user stories (US1-US4) can start in parallel (if team capacity allows)
- All Polish tasks marked [P] (T042-T050) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational tasks in parallel:
Task T007: Create src/watcher/__init__.py
Task T008: Create src/watcher/config.py
Task T009: Create src/watcher/file_mover.py
# Then sequentially:
Task T010: Create src/watcher/lock_manager.py (may depend on config.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T011-T019)
4. **STOP and VALIDATE**: Test watcher independently (drop files, verify moves)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (T011-T019) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (T020-T027) → Test independently → Deploy/Demo
4. Add User Story 3 (T028-T034) → Test independently → Deploy/Demo
5. Add User Story 4 (T035-T041) → Test independently → Deploy/Demo
6. Add Polish (T042-T052) → Final validation → Production ready
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T019) - Watcher implementation
   - Developer B: User Story 2 (T020-T027) - Claude task processing
   - Developer C: User Story 3 (T028-T034) - Dashboard updates
   - Developer D: User Story 4 (T035-T041) - Task completion
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests requested in spec - using manual integration testing approach
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All paths are absolute (E:\AI_Employee_Vault\...)
- No external APIs, no MCP servers, no autonomous loops (Bronze Tier constraints)
