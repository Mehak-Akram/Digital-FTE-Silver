---
id: 002
title: Silver Tier Technical Plan
stage: plan
date: 2026-02-15
surface: agent
model: claude-sonnet-4-5
feature: 001-silver-tier-upgrade
branch: 001-silver-tier-upgrade
user: human
command: /sp.plan
labels: ["planning", "architecture", "silver-tier", "mcp-server", "approval-workflow"]
links:
  spec: specs/001-silver-tier-upgrade/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-silver-tier-upgrade/data-model.md
  - specs/001-silver-tier-upgrade/contracts/plan_schema.yaml
  - specs/001-silver-tier-upgrade/contracts/skill_schema.yaml
  - specs/001-silver-tier-upgrade/contracts/mcp_server_api.json
  - specs/001-silver-tier-upgrade/quickstart.md
  - specs/001-silver-tier-upgrade/plan.md (updated)
tests:
  - None (planning phase)
---

## Prompt

```text
Create the Silver Tier technical plan.

WATCHERS:
1. Inbox watcher (existing)
2. Gmail IMAP watcher (new)

REASONING LOOP:
1. Scheduled Claude execution
2. Scan Needs_Action
3. Generate Plan.md files
4. Detect sensitive actions
5. Route to Pending_Approval if required

MCP SERVER:
1. Build MCP server exposing:
   - send_email()
   - post_facebook_page()
2. Facebook integration via Meta Graph API

APPROVAL FLOW:
1. Plan created
2. If external → Pending_Approval
3. Human moves to Approved
4. Claude executes via MCP
5. Move to Done

AGENT SKILLS:
1. planner_skill.py
2. email_skill.py
3. facebook_skill.py

SCHEDULER:
- Windows Task Scheduler
- Run every 10 minutes

CONSTRAINTS:
- No direct API usage by Claude
- No personal Facebook automation
- All external actions must pass through MCP
```

## Response snapshot

Completed Phase 0 (Research) and Phase 1 (Design & Contracts) of the Silver Tier implementation plan following the SDD workflow.

**Phase 0 - Research (Already Complete)**:
- Reviewed existing research.md with technology decisions
- Validated choices: MCP SDK, Windows Task Scheduler, imaplib, Meta Graph API, watchdog, python-frontmatter, file locking

**Phase 1 - Design & Contracts (Completed)**:

1. **data-model.md**: Defined 7 core entities with validation rules and state transitions:
   - Task: File-based work items with folder-based state management
   - Plan: Structured execution plans with approval routing logic
   - Approval Request: Human review interface with action previews
   - Agent Skill: Modular AI capabilities with permission declarations
   - MCP Server Configuration: External integration settings
   - Watcher: Background monitoring processes (4 instances)
   - Execution Log: Daily activity records

2. **contracts/plan_schema.yaml**: Complete Plan.md file format specification with YAML frontmatter schema, validation rules, and routing logic

3. **contracts/skill_schema.yaml**: Agent skill file format with 3 predefined skills (planner_skill, email_skill, facebook_skill)

4. **contracts/mcp_server_api.json**: MCP server API specification with send_email() and post_facebook_page() function signatures, error codes, rate limits, and circuit breaker configuration

5. **quickstart.md**: Comprehensive setup guide covering installation, folder structure, environment configuration, Facebook token generation, Gmail IMAP setup, MCP server configuration, Windows Task Scheduler setup, usage instructions, and troubleshooting

**Constitution Check**: ✅ PASS - All design artifacts comply with constitutional principles. No violations detected.

**Key Architectural Decisions**:
- MCP Server Pattern: All external actions routed through single MCP server
- Folder-Based Approval: Human approval via file movement (Pending_Approval → Approved)
- Scheduled Reasoning Loop: Windows Task Scheduler (10-minute intervals)
- Agent Skills Architecture: Modular capabilities as Markdown files
- File Locking: OS-level locks prevent race conditions

## Outcome

- ✅ Impact: Phase 0 & 1 complete. All research and design artifacts generated. Plan ready for task generation via /sp.tasks.
- 🧪 Tests: None (planning phase - tests will be defined in tasks.md)
- 📁 Files: 5 new files created (data-model.md, 3 contract schemas, quickstart.md), 1 updated (plan.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks, then `/sp.adr silver-tier-architecture` to document architectural decisions
- 🧠 Reflection: Successfully completed planning workflow despite PowerShell script unavailability. Used agent-native tools to generate all required artifacts. Constitution check passed cleanly with no violations.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell scripts unavailable (setup-plan.ps1, update-agent-context.ps1, create-phr.sh) - worked around by using agent-native file operations
- Graders run and results (PASS/FAIL): Constitution Check: PASS, Phase 0 validation: PASS, Phase 1 validation: PASS
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided architectural constraints
- Next experiment (smallest change to try): Test /sp.tasks command to validate plan completeness and generate implementation tasks
