# ADR-001: Bronze Tier Architecture - Local-Only AI Employee System

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-14
- **Feature:** 001-bronze-tier
- **Context:** Establishing foundational architecture for Personal AI Employee system with strict constraints on external dependencies, autonomous behavior, and operational complexity.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes foundation for all tiers
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Cloud-based, MCP servers, autonomous loops
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all system components
-->

## Decision

Implement Bronze Tier as a **local-only, manually-triggered, file-system-based AI Employee** with the following architectural components:

**Core Architecture:**
- **AI Logic**: Claude Code (Sonnet 4.5) via CLI interface, manually invoked
- **State Management**: Folder-based state (Inbox → Needs_Action → Plans → Done)
- **Perception Layer**: Single Python watchdog process monitoring `/Inbox`
- **Action Layer**: File system operations only (read, write, move within vault boundary)
- **Memory Layer**: Markdown files with YAML frontmatter in Obsidian vault

**Technology Stack:**
- **Language**: Python 3.12+
- **File Monitoring**: watchdog 3.0+ (cross-platform file system events)
- **Metadata Parsing**: python-frontmatter 1.0+, PyYAML 6.0+
- **Testing**: pytest 7.0+
- **Deployment**: Local process (PowerShell launcher script)

**Constitutional Constraints:**
1. File system only operations (no external APIs)
2. Vault boundary enforcement (E:\AI_Employee_Vault)
3. Manual trigger model (no autonomous loops)
4. Folder-based state management (no databases)
5. Single watcher architecture (one process maximum)
6. No cloud or external services

## Consequences

### Positive

- **Predictable Behavior**: All actions leave traceable file system footprint; no hidden state
- **Privacy & Security**: Zero external dependencies eliminates data leakage and network attack surface
- **Human Oversight**: Manual triggering ensures user control over every AI action
- **Simple Mental Model**: Folder location = task state; users understand system at a glance
- **Version Control Friendly**: All state in text files enables git-based history and rollback
- **Zero Infrastructure**: No databases, servers, or cloud accounts required
- **Fast Iteration**: File-based development enables rapid prototyping and debugging
- **Portable**: Entire system state contained in single vault directory

### Negative

- **Manual Overhead**: User must explicitly invoke Claude for every task processing step
- **No Real-Time Notifications**: Watcher only logs to console; no push notifications or alerts
- **Limited Scalability**: File system operations don't scale to thousands of concurrent tasks
- **Single User Only**: No collaboration features or concurrent access support
- **No Task Scheduling**: Cannot trigger actions at specific times or on deadlines
- **Watcher Fragility**: If watcher crashes, user must manually restart (no auto-recovery)
- **Platform Constraints**: Windows-specific PowerShell launcher (though Python code is cross-platform)

## Alternatives Considered

**Alternative A: MCP Server Architecture**
- Components: Claude Desktop + MCP servers + local database
- Pros: Richer integrations, autonomous capabilities, better UX
- Cons: Violates Bronze Tier simplicity constraint; adds infrastructure complexity; requires MCP server development
- **Rejected**: Too complex for foundational tier; deferred to Silver Tier

**Alternative B: Autonomous Loop with Background AI**
- Components: Long-running AI process + task queue + scheduler
- Pros: Fully automated workflow; no manual triggering needed
- Cons: Runaway process risk; difficult to debug; violates manual trigger principle
- **Rejected**: Eliminates human oversight; creates "Ralph Wiggum" failure mode

**Alternative C: Cloud-Based System (Notion/Airtable + Zapier)**
- Components: Cloud database + webhook integrations + hosted AI
- Pros: Multi-device access; real-time sync; rich integrations
- Cons: External dependencies; privacy concerns; network latency; subscription costs
- **Rejected**: Violates local-only constraint; introduces external failure points

**Alternative D: Node.js + Chokidar Watcher**
- Components: Node.js runtime + chokidar file watcher + TypeScript
- Pros: JavaScript ecosystem; potentially faster startup
- Cons: Additional runtime dependency; Python better for file operations and AI tooling
- **Rejected**: Python chosen for better alignment with AI/ML ecosystem and simpler deployment

## References

- Feature Spec: `specs/001-bronze-tier/spec.md`
- Implementation Plan: `specs/001-bronze-tier/plan.md`
- Constitution: `.specify/memory/constitution.md`
- Related ADRs: None (foundational ADR)
- Implementation Evidence: `src/watcher/` (watcher.py, config.py, file_mover.py, lock_manager.py)
- Evaluator Evidence: `history/prompts/001-bronze-tier/005-process-needs-action-tasks.misc.prompt.md`
