---
id: 002
title: Create Bronze Tier Plan
stage: plan
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-bronze-tier
branch: 001-bronze-tier
user: system
command: /sp.plan
labels: ["bronze-tier", "planning", "architecture", "watcher", "cli-workflows"]
links:
  spec: specs/001-bronze-tier/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-bronze-tier/plan.md
  - specs/001-bronze-tier/research.md
  - specs/001-bronze-tier/data-model.md
  - specs/001-bronze-tier/contracts/cli-commands.md
  - specs/001-bronze-tier/quickstart.md
  - CLAUDE.md
tests:
  - none
---

## Prompt

Create the Bronze Tier technical plan for the "Personal AI Employee".

The plan must strictly follow the Bronze specification and constitution.

WATCHER PLAN:
1. Use Python watchdog library
2. Monitor /Inbox directory
3. Copy new files to /Needs_Action
4. Log actions in console

AI PROCESSING PLAN:
1. Manual Claude CLI invocation
2. Claude reads /Needs_Action
3. Claude generates structured Plan file in /Plans
4. Claude updates Dashboard.md
5. Claude moves completed tasks to /Done

DATA PLAN:
1. No database
2. All state stored as Markdown
3. Folder transitions define status

INTEGRATION PLAN:
1. File drop → Watcher copies
2. User runs Claude
3. Claude processes tasks
4. Files transition to next state

CONSTRAINTS:
- No external APIs
- No MCP servers
- No autonomous loops
- No background reasoning engine

The plan must describe HOW Bronze works without introducing Silver features.

## Response snapshot

Created comprehensive Bronze Tier implementation plan with complete Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts.

**Implementation Plan (plan.md):**
- Technical Context: Python 3.11+, watchdog, python-frontmatter, file-based storage
- Constitution Check: All 6 principles validated and passed
- Project Structure: Single project with watcher script + vault structure
- No constitutional violations detected

**Research (research.md):**
- Q1: File system watcher → Python watchdog library (cross-platform, event-driven)
- Q2: YAML frontmatter → python-frontmatter library (standard, preserves formatting)
- Q3: File collisions → ISO 8601 timestamp suffix (no data loss)
- Q4: Dashboard updates → On-demand folder scan (single source of truth)
- Q5: Single instance → PID file with process validation
- Q6: CLI commands → Claude Code with explicit file paths (manual trigger)

**Data Model (data-model.md):**
- Task File: Markdown with YAML frontmatter (id, title, status, dates, tags, priority)
- Plan File: Structured sections (Goal, Steps, Acceptance Criteria, Questions)
- Dashboard: System state overview (counts, recent activity, status)
- Company Handbook: AI context and guidelines
- Folder State Model: Inbox → Needs_Action → Done (Plans parallel)

**CLI Commands (contracts/cli-commands.md):**
- Process Task: Generate plan from task description
- Update Dashboard: Scan folders and regenerate state
- Complete Task: Move to Done with timestamp
- List Tasks: Display folder contents as table
- Create Task: New task with frontmatter
- Review Plan: Provide feedback on plan quality

**Quickstart Guide (quickstart.md):**
- Setup instructions (folders, files, Python dependencies, watcher script)
- Usage workflows (creating tasks, processing, completing)
- Common workflows (simple task, complex task, batch processing)
- Troubleshooting guide
- Quick reference for commands and folder states

**Agent Context Updated:**
- CLAUDE.md updated with Python 3.11+, watchdog, PyYAML, file-based storage

## Outcome

- ✅ Impact: Complete Bronze Tier implementation plan with all Phase 0 and Phase 1 artifacts, constitution-compliant, ready for task generation
- 🧪 Tests: No tests (planning phase)
- 📁 Files: Created plan.md, research.md, data-model.md, cli-commands.md, quickstart.md; updated CLAUDE.md
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation task breakdown
- 🧠 Reflection: Plan successfully balances Bronze Tier constraints with practical implementation. Python watchdog provides reliable file monitoring, folder-based state eliminates database complexity, manual Claude CLI invocation maintains constitutional compliance. All technical unknowns resolved through research phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (6/6 principles satisfied)
- Prompt variant (if applicable): N/A - standard planning workflow
- Next experiment (smallest change to try): During implementation, validate that PID file locking works correctly on Windows and handles stale locks from crashed processes
