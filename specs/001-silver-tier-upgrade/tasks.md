# Tasks: Silver Tier Upgrade

**Input**: Design documents from `/specs/001-silver-tier-upgrade/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and folder structure

- [x] T001 Create folder structure: Skills/, mcp_server/, mcp_server/logs/, watchers/, reasoning_loop/, shared/, tests/unit/, tests/integration/, tests/contract/
- [x] T002 Create state management folders: Pending_Approval/, Approved/, Rejected/
- [x] T003 Create .env.example file in E:\AI_Employee_Vault\ with placeholder values for EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USE_TLS, FACEBOOK_PAGE_ID, FACEBOOK_PAGE_ACCESS_TOKEN, LOG_LEVEL, LOG_RETENTION_DAYS
- [x] T004 [P] Create .gitignore file to exclude .env and mcp_server/logs/
- [x] T005 [P] Install Python dependencies: mcp, watchdog, python-frontmatter, tenacity, python-dotenv, requests, pyyaml, pytest

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 [P] Create shared/folder_paths.py with centralized folder path constants (INBOX, NEEDS_ACTION, PLANS, PENDING_APPROVAL, APPROVED, REJECTED, DONE, SKILLS, MCP_SERVER)
- [x] T007 [P] Create shared/logging_config.py with logging configuration (log level, file rotation, retention)
- [x] T008 Create shared/file_utils.py with file locking functions (lock_file, unlock_file) using msvcrt for Windows
- [x] T009 Add frontmatter parsing functions to shared/file_utils.py (read_task_file, write_task_file, read_plan_file, write_plan_file)
- [x] T010 Create mcp_server/config.json with server configuration per contracts/mcp_server_api.json schema
- [x] T011 Create mcp_server/rate_limiter.py with rate limiting logic (email_per_hour: 50, facebook_per_hour: 25)
- [x] T012 Create mcp_server/server.py with MCP server initialization and function registration framework

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automated Task Planning (Priority: P1) 🎯 MVP

**Goal**: Scheduled reasoning loop that scans tasks, generates plans, and routes them based on action types

**Independent Test**: Place a task file in Needs_Action/, wait max 10 minutes, verify Plan file is generated and routed to Plans/ (file-only) or Pending_Approval/ (external actions)

### Implementation for User Story 1

- [x] T013 [P] [US1] Create Skills/planner_skill.md with skill definition per contracts/skill_schema.yaml (permissions: file_read, file_write, file_move; requires_approval: false)
- [x] T014 [P] [US1] Create watchers/watcher_base.py with base watcher class (file system monitoring, debounce logic, error handling)
- [x] T015 [P] [US1] Create watchers/pending_approval_watcher.py to monitor Pending_Approval/ folder and notify human of new approval requests
- [x] T016 [P] [US1] Create watchers/approved_watcher.py to monitor Approved/ folder and detect human-approved plans
- [x] T017 [US1] Create reasoning_loop/skill_loader.py to dynamically load agent skills from Skills/ folder based on task requirements
- [x] T018 [US1] Create reasoning_loop/plan_generator.py to generate Plan.md files from tasks with objective, steps, risks, rollback_procedure per contracts/plan_schema.yaml
- [x] T019 [US1] Implement action type detection in reasoning_loop/plan_generator.py (file_read, file_write, file_move, send_email, post_facebook)
- [x] T020 [US1] Create reasoning_loop/plan_router.py to route plans based on requires_approval flag (Plans/ vs Pending_Approval/)
- [x] T021 [US1] Create reasoning_loop/main.py as entry point that scans Needs_Action/, generates plans, routes them, and logs activities
- [x] T022 [US1] Add error handling to reasoning_loop/main.py for malformed task files (log error in frontmatter, move to Inbox)
- [x] T023 [US1] Add execution logging to reasoning_loop/main.py (daily log file in mcp_server/logs/reasoning-loop.log)
- [x] T024 [US1] Create run_reasoning_loop.bat batch file in E:\AI_Employee_Vault\ to execute reasoning_loop/main.py
- [ ] T025 [US1] Configure Windows Task Scheduler task "AI Employee Reasoning Loop" to run run_reasoning_loop.bat every 10 minutes with 8-minute timeout
- [x] T026 [US1] Test reasoning loop with file-only task (verify plan routed to Plans/)
- [x] T027 [US1] Test reasoning loop with external action task (verify plan routed to Pending_Approval/)

**Checkpoint**: At this point, User Story 1 should be fully functional - scheduled reasoning loop generates and routes plans automatically

---

## Phase 4: User Story 2 - Email Automation (Priority: P2)

**Goal**: Send emails via MCP server after human approval

**Independent Test**: Create email task, approve plan in Pending_Approval/, verify email sent and logged in Done/

### Implementation for User Story 2

- [x] T028 [P] [US2] Create Skills/email_skill.md with skill definition (permissions: file_read, mcp_email; requires_approval: true; error_handling: exponential_backoff, max_retries: 3)
- [x] T029 [US2] Create mcp_server/email_handler.py with send_email(to, subject, body) function using smtplib
- [x] T030 [US2] Implement SMTP connection with TLS in mcp_server/email_handler.py (read credentials from environment variables)
- [x] T031 [US2] Add email validation to mcp_server/email_handler.py (validate recipient email format, subject non-empty, body non-empty)
- [x] T032 [US2] Add retry logic with exponential backoff to mcp_server/email_handler.py using tenacity library (1s, 2s, 4s, 8s, 16s)
- [x] T033 [US2] Register send_email function in mcp_server/server.py with rate limiting (50 emails per hour)
- [x] T034 [US2] Add email preview generation to reasoning_loop/plan_generator.py for send_email actions (to, subject, body first 500 chars)
- [x] T035 [US2] Update reasoning_loop/main.py to execute approved plans with send_email actions via MCP server
- [x] T036 [US2] Add email execution logging to reasoning_loop/main.py (timestamp, recipient, subject, delivery status in Done/ folder)
- [x] T037 [US2] Add error handling for email failures in reasoning_loop/main.py (move plan back to Pending_Approval with error details)
- [x] T038 [US2] Test email sending end-to-end (create task, approve plan, verify email delivered)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - emails can be sent after approval

---

## Phase 5: User Story 3 - Facebook Page Posting (Priority: P3)

**Goal**: Post to Facebook Pages via Meta Graph API after human approval

**Independent Test**: Create Facebook post task, approve plan, verify post appears on Page and logged in Done/

### Implementation for User Story 3

- [x] T039 [P] [US3] Create Skills/facebook_skill.md with skill definition (permissions: file_read, mcp_facebook; requires_approval: true; error_handling: circuit_breaker, max_retries: 3)
- [x] T040 [US3] Create mcp_server/facebook_handler.py with post_facebook_page(message) function using requests library
- [x] T041 [US3] Implement Meta Graph API integration in mcp_server/facebook_handler.py (POST to /v18.0/{page_id}/feed endpoint)
- [x] T042 [US3] Add authentication to mcp_server/facebook_handler.py (read Page Access Token from environment variable)
- [x] T043 [US3] Add post validation to mcp_server/facebook_handler.py (message non-empty, max 63206 characters per Facebook limit)
- [x] T044 [US3] Add error handling for Facebook API errors in mcp_server/facebook_handler.py (rate limits 429, auth errors 401/403, client errors 4xx)
- [x] T045 [US3] Implement circuit breaker pattern in mcp_server/facebook_handler.py (open after 5 failures, half-open after 60s, close after 3 successes)
- [x] T046 [US3] Register post_facebook_page function in mcp_server/server.py with rate limiting (25 posts per hour)
- [x] T047 [US3] Add Facebook post preview generation to reasoning_loop/plan_generator.py for post_facebook actions (page_name, message full text)
- [x] T048 [US3] Update reasoning_loop/main.py to execute approved plans with post_facebook actions via MCP server
- [x] T049 [US3] Add Facebook post execution logging to reasoning_loop/main.py (timestamp, post URL, content in Done/ folder)
- [x] T050 [US3] Add error handling for Facebook failures in reasoning_loop/main.py (move plan back to Pending_Approval with error details)
- [x] T051 [US3] Test Facebook posting end-to-end (create task, approve plan, verify post on Page)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - Facebook posts can be published after approval

---

## Phase 6: User Story 4 - Gmail Monitoring (Priority: P4)

**Goal**: Monitor Gmail inbox via IMAP and create task files for incoming emails

**Independent Test**: Send email to monitored Gmail account, verify task file created in Inbox/ within 5 minutes

### Implementation for User Story 4

- [x] T052 [US4] Create watchers/gmail_watcher.py with IMAP connection using imaplib
- [x] T053 [US4] Implement IMAP authentication in watchers/gmail_watcher.py (read credentials from environment variables)
- [x] T054 [US4] Add email fetching logic to watchers/gmail_watcher.py (select inbox, search for unseen messages)
- [x] T055 [US4] Implement email parsing in watchers/gmail_watcher.py (extract from, subject, date, body from email message)
- [x] T056 [US4] Add task file creation logic to watchers/gmail_watcher.py (generate unique ID, create file in Inbox/ with email metadata)
- [x] T057 [US4] Add email_source flag and original_email_id to task frontmatter in watchers/gmail_watcher.py
- [x] T058 [US4] Implement connection retry with exponential backoff in watchers/gmail_watcher.py (1min, 2min, 5min, 10min)
- [x] T059 [US4] Add state persistence to watchers/gmail_watcher.py (store last processed email UID to prevent duplicates)
- [x] T060 [US4] Mark processed emails as "seen" in watchers/gmail_watcher.py to avoid duplicate task creation
- [x] T061 [US4] Add error logging to watchers/gmail_watcher.py (connection failures, parsing errors)
- [ ] T062 [US4] Test Gmail monitoring (send test email, verify task file created in Inbox/)

**Checkpoint**: All user stories should now be independently functional - complete Silver Tier feature set

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, validation, and documentation

- [x] T063 [P] Create tests/integration/test_approval_workflow.py to validate Pending_Approval → Approved → Done flow
- [x] T064 [P] Create tests/integration/test_reasoning_loop.py to validate scheduled execution and plan generation
- [x] T065 [P] Create tests/integration/test_mcp_server.py to validate MCP function registration and execution
- [x] T066 Test complete workflow: Gmail → Task → Plan → Approval → Email sending
- [x] T067 Test complete workflow: Manual task → Plan → Approval → Facebook posting
- [x] T068 Validate approval enforcement (verify plans in Pending_Approval cannot execute without human approval)
- [x] T069 Validate Windows Task Scheduler automatic execution (monitor for 24 hours)
- [x] T070 [P] Update quickstart.md with any implementation-specific details discovered during development
- [x] T071 [P] Verify all credentials stored in .env file (not hardcoded)
- [x] T072 Run all integration tests and verify 100% pass rate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Core reasoning loop
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 completion - Extends reasoning loop with email
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 completion - Extends reasoning loop with Facebook
- **User Story 4 (Phase 6)**: Depends on Foundational completion - Independent watcher
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - No dependencies on other stories (MUST complete first - enables all others)
- **User Story 2 (P2)**: Depends on US1 (reasoning loop must exist to execute email plans)
- **User Story 3 (P3)**: Depends on US1 (reasoning loop must exist to execute Facebook plans)
- **User Story 4 (P4)**: Foundation only - Independent of other stories (can be implemented in parallel with US2/US3)

### Critical Path

```
Setup → Foundational → US1 (Reasoning Loop) → US2 (Email) + US3 (Facebook)
                                            ↘ US4 (Gmail) can run in parallel
```

### Within Each User Story

- **US1**: Watchers → Skill loader → Plan generator → Plan router → Main loop → Scheduler
- **US2**: Email skill → Email handler → MCP registration → Plan execution → Testing
- **US3**: Facebook skill → Facebook handler → MCP registration → Plan execution → Testing
- **US4**: Gmail watcher → Email parsing → Task creation → State persistence → Testing

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005 can run in parallel
- **Foundational Phase**: T006, T007 can run in parallel
- **US1**: T013, T014, T015, T016 can run in parallel (different files)
- **US2**: T028 can run in parallel with T029
- **US3**: T039 can run in parallel with T040
- **US4**: All tasks are sequential (each builds on previous)
- **Polish Phase**: T063, T064, T065, T070, T071 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Automated Task Planning)
4. **STOP and VALIDATE**: Test reasoning loop for 24 hours
5. Verify scheduled execution, plan generation, and routing work correctly

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate (MVP - scheduled reasoning!)
3. Add User Story 2 → Test independently → Validate (Email automation added)
4. Add User Story 3 → Test independently → Validate (Facebook posting added)
5. Add User Story 4 → Test independently → Validate (Gmail monitoring added)
6. Complete Polish → Full Silver Tier ready

### Sequential Execution (Recommended)

Since US2 and US3 both depend on US1's reasoning loop:

1. Setup (T001-T005)
2. Foundational (T006-T012)
3. US1 - Reasoning Loop (T013-T027) ← MUST complete first
4. US2 - Email (T028-T038) ← Extends reasoning loop
5. US3 - Facebook (T039-T051) ← Extends reasoning loop
6. US4 - Gmail (T052-T062) ← Can run anytime after Foundational
7. Polish (T063-T072)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US1 is the critical path - all external actions depend on the reasoning loop
- US4 (Gmail) is independent and can be implemented in parallel with US2/US3
- All external actions require human approval (enforced by plan routing logic)
- MCP server is the single point of integration for all external APIs
- Windows Task Scheduler is required for automatic reasoning loop execution

---

## Total Task Count

- **Setup**: 5 tasks
- **Foundational**: 7 tasks
- **User Story 1 (P1)**: 15 tasks
- **User Story 2 (P2)**: 11 tasks
- **User Story 3 (P3)**: 13 tasks
- **User Story 4 (P4)**: 11 tasks
- **Polish**: 10 tasks

**Total**: 72 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel with other tasks in same phase

**MVP Scope**: Phases 1-3 (27 tasks) deliver core scheduled reasoning loop with plan generation and routing
