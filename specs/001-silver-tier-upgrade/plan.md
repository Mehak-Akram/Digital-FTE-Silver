# Implementation Plan: Silver Tier Upgrade

**Branch**: `001-silver-tier-upgrade` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-silver-tier-upgrade/spec.md`

## Summary

Upgrade the Bronze AI Employee into a functional assistant capable of external business automation. The Silver Tier introduces scheduled Claude reasoning loops (every 10 minutes), human-in-the-loop approval workflows for external actions, and controlled external integrations via a single MCP server. Core capabilities include email sending and Facebook Page posting, both requiring explicit human approval before execution.

**Technical Approach**: Build a Python-based automation system with four file system watchers (Inbox, Gmail IMAP, Pending_Approval, Approved), a scheduled reasoning loop triggered by Windows Task Scheduler, and an MCP server exposing send_email() and post_facebook_page() functions. All external actions route through the MCP server and require human approval via folder-based state transitions.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- MCP SDK (Model Context Protocol server implementation)
- imaplib (built-in, for Gmail IMAP monitoring)
- requests (for Meta Graph API integration)
- smtplib (built-in, for email sending via SMTP)
- watchdog (for file system watchers)
- PyYAML (for YAML frontmatter parsing)
- python-dotenv (for secure credential management)

**Storage**: File system (Markdown files with YAML frontmatter in Obsidian vault)
**Testing**: pytest with unit, integration, and contract test suites
**Target Platform**: Windows 10+ (requires Windows Task Scheduler)
**Project Type**: Single project (CLI-based automation system)
**Performance Goals**:
- Process tasks within 10-minute reasoning loop cycle
- Handle 20 concurrent tasks without degradation
- Email delivery within 2 minutes of approval
- Gmail monitoring with 5-minute detection latency

**Constraints**:
- <10 minute processing cycle per reasoning loop execution
- 99% watcher uptime over 7-day period
- 95% email sending success rate
- Zero unauthorized external actions (100% approval compliance)
- Single MCP server (no multiple servers)
- Windows Task Scheduler dependency

**Scale/Scope**:
- Single user system
- Local file system operations within E:\AI_Employee_Vault
- Estimated 10-20 tasks per day
- 4 concurrent watchers + 1 scheduled reasoning loop
- Support for Gmail IMAP and Facebook Page API integrations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Bronze Tier Principles (Preserved)

✅ **Principle I: File System Only Operations (Bronze Tier)**
Status: COMPLIANT - Silver Tier extends Bronze with controlled external actions via MCP server, as explicitly permitted by constitution Principle VIII.

✅ **Principle II: Vault Boundary Enforcement**
Status: COMPLIANT - All file operations remain within E:\AI_Employee_Vault boundary.

✅ **Principle III: Manual Trigger Model (Bronze Tier)**
Status: COMPLIANT - Silver Tier introduces scheduled reasoning loops with human approval gates, as explicitly permitted by constitution amendment.

✅ **Principle IV: Folder-Based State Management**
Status: COMPLIANT - Extends Bronze folders (Inbox, Needs_Action, Plans, Done) with Silver folders (Pending_Approval, Approved, Rejected, Skills, mcp_server).

✅ **Principle V: Watcher Architecture**
Status: COMPLIANT - Multiple watchers permitted in Silver Tier (Inbox, Gmail, Pending_Approval, Approved), each with single responsibility.

✅ **Principle VI: No Cloud or External Services (Bronze Tier)**
Status: COMPLIANT - Silver Tier exceptions explicitly permitted via Principle VIII (MCP Server Integration) and Principle X (External Action Boundaries).

### Silver Tier Principles (New)

✅ **Principle VII: Human-in-the-Loop Approval**
Status: COMPLIANT - All external actions (email, Facebook) require explicit human approval via Pending_Approval → Approved folder transition.

✅ **Principle VIII: MCP Server Integration**
Status: COMPLIANT - Single MCP server in /mcp_server directory, all external actions routed through MCP, rate limiting implemented.

✅ **Principle IX: Agent Skills Architecture**
Status: COMPLIANT - Three skills (planner_skill, email_skill, facebook_skill) stored in /Skills folder with permission declarations.

✅ **Principle X: External Action Boundaries**
Status: COMPLIANT - Only email sending and Facebook Page posting permitted. Personal Facebook profiles, browser automation, and web scraping explicitly prohibited.

✅ **Principle XI: Plan-Driven Execution**
Status: COMPLIANT - All external actions originate from Plan.md files with objective, risks, rollback procedures, and approval checkpoints.

### Gate Result

**✅ PASS** - No constitution violations detected. This is a clean Silver Tier upgrade following all constitutional principles and amendments.

## Project Structure

### Documentation (this feature)

```text
specs/001-silver-tier-upgrade/
├── spec.md                   # Feature specification (completed)
├── plan.md                   # This file (implementation plan)
├── research.md               # Phase 0: Technology research and decisions
├── data-model.md             # Phase 1: Entity definitions and state transitions
├── quickstart.md             # Phase 1: Setup and usage guide
├── contracts/                # Phase 1: API contracts and schemas
│   ├── mcp_server_api.json   # MCP server function signatures
│   ├── plan_schema.yaml      # Plan.md file format specification
│   └── skill_schema.yaml     # Agent skill file format specification
└── tasks.md                  # Phase 2: Implementation tasks (/sp.tasks command)
```

### Source Code (repository root)

```text
E:\AI_Employee_Vault\
├── Skills/                           # Agent skill definitions
│   ├── planner_skill.md              # Plan generation and routing logic
│   ├── email_skill.md                # Email composition and sending
│   └── facebook_skill.md             # Facebook Page posting
│
├── mcp_server/                       # MCP server implementation
│   ├── server.py                     # Main MCP server entry point
│   ├── email_handler.py              # SMTP email sending logic
│   ├── facebook_handler.py           # Meta Graph API integration
│   ├── rate_limiter.py               # API rate limiting
│   ├── config.json                   # MCP server configuration
│   ├── .env.example                  # Example environment variables
│   └── logs/                         # MCP server execution logs
│
├── watchers/                         # File system watchers
│   ├── inbox_watcher.py              # Monitors /Inbox for new tasks
│   ├── gmail_watcher.py              # IMAP email monitoring
│   ├── pending_approval_watcher.py   # Notifies human of approval requests
│   ├── approved_watcher.py           # Detects approved plans
│   └── watcher_base.py               # Shared watcher utilities
│
├── reasoning_loop/                   # Scheduled reasoning loop
│   ├── main.py                       # Entry point for Windows Task Scheduler
│   ├── plan_generator.py             # Generates Plan.md from tasks
│   ├── plan_router.py                # Routes plans to Plans or Pending_Approval
│   └── skill_loader.py               # Dynamically loads agent skills
│
├── shared/                           # Shared utilities
│   ├── file_utils.py                 # File locking, frontmatter parsing
│   ├── folder_paths.py               # Centralized folder path definitions
│   └── logging_config.py             # Logging configuration
│
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests for individual components
│   │   ├── test_plan_generator.py
│   │   ├── test_email_handler.py
│   │   └── test_facebook_handler.py
│   ├── integration/                  # Integration tests for workflows
│   │   ├── test_approval_workflow.py
│   │   ├── test_reasoning_loop.py
│   │   └── test_mcp_server.py
│   └── contract/                     # Contract tests for MCP API
│       └── test_mcp_contracts.py
│
└── [State management folders]        # Folder-based state
    ├── Inbox/                        # New tasks
    ├── Needs_Action/                 # Triaged tasks awaiting processing
    ├── Plans/                        # File-system-only execution plans
    ├── Pending_Approval/             # Plans requiring human approval
    ├── Approved/                     # Human-approved plans ready for execution
    ├── Rejected/                     # Human-rejected plans
    └── Done/                         # Completed tasks with execution logs
```

**Structure Decision**: Single project structure selected because this is a CLI-based automation system with a single deployment target (Windows local machine). All components (watchers, reasoning loop, MCP server) run as separate processes but share common utilities and configuration. No web frontend or mobile app required.

## Complexity Tracking

> **No violations detected - this section intentionally left empty.**

All architectural decisions comply with the constitution. No complexity justifications required.

---

## Phase 0: Research & Technology Decisions

**Status**: Ready to begin

**Research Tasks**:
1. MCP SDK selection and best practices for Python
2. Windows Task Scheduler integration patterns for Python scripts
3. IMAP email monitoring best practices (connection pooling, error handling)
4. Meta Graph API authentication and Page Access Token management
5. File locking mechanisms for concurrent access prevention
6. Watchdog library patterns for reliable file system monitoring
7. YAML frontmatter parsing libraries and standards
8. Error handling and retry strategies for external API calls

**Output**: `research.md` with technology decisions, rationale, and alternatives considered.

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETED (2026-02-15)

**Deliverables**:
1. ✅ **data-model.md**: Entity definitions for Task, Plan, Approval Request, Agent Skill, MCP Server Configuration, Watcher, Execution Log
2. ✅ **contracts/mcp_server_api.json**: MCP server function signatures (send_email, post_facebook_page)
3. ✅ **contracts/plan_schema.yaml**: Plan.md file format specification with YAML frontmatter schema
4. ✅ **contracts/skill_schema.yaml**: Agent skill file format specification
5. ✅ **quickstart.md**: Setup guide for Silver Tier (folder creation, MCP server config, Windows Task Scheduler setup)

**Post-Design Constitution Check**: ✅ PASS - All design artifacts comply with constitutional principles. No violations introduced during Phase 1.

---

## Implementation Readiness

**Phase 0 & 1 Complete**: All research and design artifacts generated. The plan is ready for task generation.

**Next Command**: Run `/sp.tasks` to generate implementation tasks from this plan.

**Generated Artifacts**:
- `specs/001-silver-tier-upgrade/research.md` - Technology decisions and rationale
- `specs/001-silver-tier-upgrade/data-model.md` - Entity definitions and state transitions
- `specs/001-silver-tier-upgrade/contracts/mcp_server_api.json` - MCP server API specification
- `specs/001-silver-tier-upgrade/contracts/plan_schema.yaml` - Plan file format schema
- `specs/001-silver-tier-upgrade/contracts/skill_schema.yaml` - Agent skill format schema
- `specs/001-silver-tier-upgrade/quickstart.md` - Setup and usage guide

**Architecture Summary**:
- **Language**: Python 3.11+
- **Core Components**: 4 watchers, 1 reasoning loop, 1 MCP server, 3 agent skills
- **External Integrations**: Gmail IMAP, SMTP email, Meta Graph API (Facebook Pages)
- **Scheduling**: Windows Task Scheduler (10-minute intervals)
- **Approval Workflow**: Folder-based state transitions (Pending_Approval → Approved → Done)
- **Security**: Environment variables for credentials, human approval for all external actions

**Key Architectural Decisions**:
1. **MCP Server Pattern**: All external actions routed through single MCP server (no direct API calls from Claude)
2. **Folder-Based Approval**: Human approval via file movement between folders (Pending_Approval → Approved)
3. **Scheduled Reasoning Loop**: Windows Task Scheduler triggers Claude execution every 10 minutes
4. **Agent Skills Architecture**: Modular capabilities stored as Markdown files in /Skills folder
5. **File Locking**: OS-level locks (msvcrt on Windows) prevent race conditions between watchers and reasoning loop

📋 **Architectural decisions detected**: Multiple significant decisions made (MCP server pattern, approval workflow, scheduling strategy, skills architecture). Document reasoning and tradeoffs? Run `/sp.adr silver-tier-architecture`
