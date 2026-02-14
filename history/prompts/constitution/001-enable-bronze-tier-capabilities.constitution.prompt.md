---
id: 001
title: Enable Bronze Tier Capabilities
stage: constitution
date: 2026-02-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["bronze-tier", "architecture", "constraints", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Amend the global constitution to enable Bronze Tier capabilities for the "Personal AI Employee" project.

BRONZE TIER ARCHITECTURE:

- AI Logic: Claude Code
- Memory Layer: Local Obsidian Vault (Markdown files)
- Perception Layer: Single Watcher (File System Watcher)
- Action Layer: File system operations only (no external APIs)
- Task Processing: Manual trigger via Claude CLI
- State Management: Folder-based state transitions
- No MCP servers in Bronze tier

RULES:

- AI may ONLY interact with the system via file system operations inside the Obsidian vault.
- No external API calls allowed.
- No email sending.
- No WhatsApp automation.
- No browser automation.
- No background autonomous loops.
- No Ralph Wiggum loop in Bronze tier.
- All state must be represented via folder movement:
    - /Inbox → /Needs_Action → /Plans → /Done
- Claude must never modify files outside the vault.
- No cloud usage.
- No background daemons beyond the single watcher.

This amendment authorizes Bronze Tier functionality only.

## Response snapshot

Created Personal AI Employee Constitution v1.0.0 with Bronze Tier architectural constraints.

**Core Principles Established:**
1. File System Only Operations - AI restricted to file I/O within vault
2. Vault Boundary Enforcement - No operations outside E:\AI_Employee_Vault
3. Manual Trigger Model - No autonomous loops, CLI-initiated only
4. Folder-Based State Management - Inbox → Needs_Action → Plans → Done
5. Single Watcher Architecture - One file system watcher maximum
6. No Cloud or External Services - Local-only operation

**Architecture Constraints:**
- AI Logic: Claude Code (Sonnet 4.5)
- Memory: Markdown files with YAML frontmatter
- Perception: Single watcher on /Inbox
- Actions: File read/write/move/delete within vault only
- Prohibited: MCP servers, APIs, autonomous loops, network operations

**Governance Model:**
- Semantic versioning for amendments
- Sync Impact Reports required
- Template consistency validation
- Review before tier upgrades

## Outcome

- ✅ Impact: Constitution established from template, Bronze Tier constraints codified, governance framework defined
- 🧪 Tests: No tests (governance document)
- 📁 Files: Created constitution.md v1.0.0 with complete Bronze Tier specification
- 🔁 Next prompts: Validate dependent templates (plan/spec/tasks), create first feature spec, implement file watcher
- 🧠 Reflection: Constitution provides clear operational boundaries for Bronze Tier. All principles are testable and enforceable. Ready for feature development within constraints.

## Evaluation notes (flywheel)

- Failure modes observed: None - initial constitution creation
- Graders run and results (PASS/FAIL): Manual validation - PASS (all placeholders filled, principles clear and testable)
- Prompt variant (if applicable): N/A - initial creation
- Next experiment (smallest change to try): Validate constitution compliance during first feature implementation to identify any missing constraints or ambiguities
