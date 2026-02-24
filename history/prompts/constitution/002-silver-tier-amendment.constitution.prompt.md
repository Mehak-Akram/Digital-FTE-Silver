---
id: 002
title: Silver Tier Amendment
stage: constitution
date: 2026-02-14
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: User
command: /sp.constitution
labels: ["constitution", "silver-tier", "governance", "mcp", "approval-workflow", "external-integrations"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - Pending_Approval/ (created)
  - Approved/ (created)
  - Rejected/ (created)
  - Skills/ (created)
  - mcp_server/ (created)
tests:
  - none
---

## Prompt

Amend the constitution to enable Silver Tier for the Personal AI Employee.

SILVER AUTHORIZATIONS:
- Multiple watchers allowed
- Scheduled Claude reasoning loop allowed
- One MCP server allowed
- Email sending allowed via MCP
- Facebook Page posting allowed via official Meta Graph API
- Human-in-the-loop approval required for sensitive actions
- All AI functionality implemented as Agent Skills

SILVER RULES:
- No automation of personal Facebook profiles
- Only Facebook Page posting allowed via official Graph API
- No browser automation or scraping
- All external actions must go through MCP server
- No direct API calls from Claude
- Sensitive actions require approval workflow
- All actions must originate from a Plan.md file
- No autonomous destructive behavior
- Local-first architecture preserved

NEW REQUIRED FOLDERS:
- Pending_Approval
- Approved
- Rejected
- Skills
- mcp_server

This amendment authorizes Silver Tier functionality only.

## Response snapshot

Constitution amended from v1.0.0 to v1.1.0 (MINOR version bump).

**Changes Made**:
- Added 5 new principles (VII-XI) for Silver Tier capabilities
- Expanded Principle V to support multiple watchers in Silver Tier
- Created Silver Tier Architecture Enhancements section
- Defined approval workflow: Pending_Approval → Approved/Rejected → Done
- Established MCP server integration requirements (one server maximum)
- Mandated Agent Skills architecture for all AI functionality
- Defined external action boundaries (email, Facebook Pages via official API)
- Required plan-driven execution for all external actions
- Preserved all Bronze Tier principles as foundation

**Folder Structure Created**:
- /Pending_Approval - Actions awaiting human review
- /Approved - Actions approved for execution
- /Rejected - Actions denied by human
- /Skills - Agent skill definitions
- /mcp_server - MCP server configuration

**Key Constraints**:
- Human approval required for all sensitive external actions
- No personal Facebook profile automation (only Pages via official API)
- No browser automation or scraping
- All external actions route through single MCP server
- No direct API calls from Claude
- Local-first architecture preserved from Bronze Tier

## Outcome

- ✅ Impact: Constitution upgraded to Silver Tier (v1.1.0), enabling controlled external integrations while preserving Bronze Tier safety guarantees
- 🧪 Tests: No tests required (governance document)
- 📁 Files: Updated constitution.md, created 5 new folders for Silver Tier workflow
- 🔁 Next prompts: Implement MCP server configuration, define initial Agent Skills, document approval workflow procedures
- 🧠 Reflection: Amendment successfully balances expanded capabilities with strong safety controls through human-in-the-loop approval gates

## Evaluation notes (flywheel)

- Failure modes observed: None - amendment completed successfully with proper versioning and sync impact report
- Graders run and results (PASS/FAIL): N/A (governance document, no automated grading)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement first Agent Skill to validate Skills architecture, then configure MCP server for email integration
