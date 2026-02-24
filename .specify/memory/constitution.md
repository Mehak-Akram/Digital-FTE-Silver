# Personal AI Employee Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Rationale: Silver Tier amendment - adds controlled external integrations while preserving Bronze Tier foundation

Modified Principles:
- Expanded Principle V: Single Watcher Architecture → Multiple Watchers (Silver Tier)
- Enhanced Operational Model with approval workflows

Added Sections:
- Silver Tier Architecture Enhancements
- Principle VII: Human-in-the-Loop Approval
- Principle VIII: MCP Server Integration
- Principle IX: Agent Skills Architecture
- Principle X: External Action Boundaries
- Principle XI: Plan-Driven Execution
- Silver Tier Folder Structure
- Approval Workflow specification

Removed Sections: None (Bronze Tier principles preserved)

Templates Requiring Updates:
- ✅ constitution.md (this file)
- ⚠ .specify/templates/plan-template.md (pending validation)
- ⚠ .specify/templates/spec-template.md (pending validation)
- ⚠ .specify/templates/tasks-template.md (pending validation)

Follow-up TODOs:
- Create folder structure: Pending_Approval, Approved, Rejected, Skills, mcp_server
- Document MCP server configuration requirements
- Define approval workflow implementation details
-->

## Core Principles

### I. File System Only Operations (Bronze Tier)

The AI MUST interact with the system exclusively through file system operations within the designated Obsidian vault. No external API calls, network requests, or system calls beyond file I/O are permitted in Bronze Tier.

**Rationale**: This constraint ensures predictable, auditable behavior and eliminates security risks associated with external integrations. All actions leave a traceable file system footprint.

### II. Vault Boundary Enforcement

All file operations MUST occur within the Obsidian vault directory (`E:\AI_Employee_Vault`). The AI MUST NOT read, write, modify, or delete files outside this boundary.

**Rationale**: Strict boundary enforcement prevents accidental data corruption, maintains system integrity, and provides a clear security perimeter for AI operations.

### III. Manual Trigger Model (Bronze Tier)

Task processing MUST be initiated manually via Claude CLI commands in Bronze Tier. Silver Tier introduces scheduled Claude reasoning loops with human approval gates.

**Rationale**: Manual triggering ensures human oversight for every AI action, preventing runaway processes and maintaining user control over system behavior. Silver Tier scheduling requires explicit plan approval.

### IV. Folder-Based State Management

System state MUST be represented through folder location and structure. State transitions follow the canonical flow:
- `/Inbox` → New items requiring triage
- `/Needs_Action` → Triaged items awaiting execution
- `/Plans` → Items with execution plans ready for implementation
- `/Done` → Completed items

Silver Tier adds:
- `/Pending_Approval` → Actions requiring human approval
- `/Approved` → Actions approved for execution
- `/Rejected` → Actions denied by human review
- `/Skills` → Agent skill definitions
- `/mcp_server` → MCP server configuration and state

File movement between folders represents state changes. No external state databases or registries are permitted.

**Rationale**: Folder-based state is human-readable, version-controllable, and requires no additional infrastructure. Users can understand system state at a glance through file explorer.

### V. Watcher Architecture

**Bronze Tier**: Only ONE file system watcher process may run concurrently. The watcher's sole responsibility is detecting new files in `/Inbox` and notifying the user.

**Silver Tier**: Multiple watchers are permitted for monitoring different folders (Inbox, Pending_Approval, Approved). Each watcher MUST have a single, well-defined responsibility.

**Rationale**: Bronze Tier's single watcher minimizes complexity. Silver Tier's multiple watchers enable approval workflows while maintaining clear separation of concerns.

### VI. No Cloud or External Services (Bronze Tier)

Bronze Tier MUST operate entirely locally. Prohibited:
- Cloud storage synchronization during AI operations
- External API calls (email, messaging, web services)
- Browser automation
- Network-dependent features

**Silver Tier Exceptions**: See Principle VIII (MCP Server Integration) and Principle X (External Action Boundaries) for controlled external access.

**Rationale**: Local-only operation ensures privacy, eliminates network dependencies, and provides a stable foundation before introducing external integrations in higher tiers.

### VII. Human-in-the-Loop Approval (Silver Tier)

All sensitive actions MUST require explicit human approval before execution. Sensitive actions include:
- Sending emails
- Posting to social media (Facebook Pages)
- Modifying external systems via MCP
- Executing plans with external side effects

**Approval Workflow**:
1. AI generates action plan and writes to `/Pending_Approval`
2. Human reviews plan details, risks, and intended outcomes
3. Human moves file to `/Approved` (consent) or `/Rejected` (denial)
4. AI executes only approved actions
5. Results logged to `/Done` with execution summary

**Rationale**: Human approval gates prevent unauthorized actions, maintain user control, and provide accountability for all external operations.

### VIII. MCP Server Integration (Silver Tier)

Silver Tier permits ONE Model Context Protocol (MCP) server for controlled external integrations.

**Requirements**:
- MCP server MUST be configured in `/mcp_server` directory
- All external actions MUST route through the MCP server (no direct API calls from Claude)
- MCP server MUST implement rate limiting and error handling
- MCP server configuration MUST be version-controlled

**Permitted MCP Operations**:
- Email sending (via configured email service)
- Facebook Page posting (via official Meta Graph API only)
- Other approved external integrations documented in MCP server config

**Prohibited**:
- Direct API calls from Claude (must use MCP)
- Multiple concurrent MCP servers
- MCP operations without approval workflow

**Rationale**: MCP provides a controlled, auditable interface for external integrations. Single server constraint maintains simplicity while enabling essential external capabilities.

### IX. Agent Skills Architecture (Silver Tier)

All AI functionality MUST be implemented as Agent Skills stored in `/Skills` directory.

**Skill Requirements**:
- Each skill MUST be a self-contained Markdown file
- Skills MUST declare required permissions and external dependencies
- Skills MUST specify approval requirements (auto-approve vs human-approve)
- Skills MUST include error handling and rollback procedures

**Rationale**: Skills architecture provides modularity, reusability, and clear permission boundaries. Users can audit, enable, or disable specific capabilities.

### X. External Action Boundaries (Silver Tier)

**Permitted External Actions**:
- Email sending via MCP (with approval)
- Facebook Page posting via official Meta Graph API (with approval)
- Actions explicitly defined in approved skills

**Prohibited Actions**:
- Personal Facebook profile automation
- Browser automation or web scraping
- Unauthorized API access
- Actions bypassing MCP server
- Destructive operations without approval

**Rationale**: Clear boundaries prevent misuse while enabling legitimate productivity enhancements. Official APIs ensure compliance with platform terms of service.

### XI. Plan-Driven Execution (Silver Tier)

All external actions MUST originate from a documented Plan.md file. Ad-hoc external operations are prohibited.

**Plan Requirements**:
- Clear objective and success criteria
- List of external actions with justification
- Risk assessment and mitigation strategies
- Rollback procedure for failures
- Approval checkpoint before execution

**Rationale**: Plan-driven execution ensures thoughtful design, enables review before action, and provides documentation for audit trails.

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

## Silver Tier Architecture Enhancements

**AI Logic**: Claude Code (Sonnet 4.5) via CLI interface + scheduled reasoning loops (with approval)

**Memory Layer**: Local Obsidian vault (unchanged from Bronze)

**Perception Layer**: Multiple watchers permitted:
- Inbox watcher (detects new tasks)
- Pending_Approval watcher (detects items needing review)
- Approved watcher (detects approved actions ready for execution)

**Action Layer**: File system operations + controlled external actions via MCP:
- All Bronze Tier file operations
- Email sending (via MCP, with approval)
- Facebook Page posting (via MCP, with approval)
- Other MCP-enabled integrations (with approval)

**Task Processing**: Manual invocation + scheduled Claude reasoning loops (requires plan approval)

**State Management**: Folder-based (unchanged) + approval workflow folders

**Required Folder Structure**:
- `/Inbox` - New tasks
- `/Needs_Action` - Triaged tasks
- `/Plans` - Execution plans
- `/Pending_Approval` - Actions awaiting human review
- `/Approved` - Actions approved for execution
- `/Rejected` - Actions denied by human
- `/Done` - Completed tasks
- `/Skills` - Agent skill definitions
- `/mcp_server` - MCP server configuration

**Permitted in Silver Tier**:
- ONE MCP server for external integrations
- Multiple file system watchers (with clear responsibilities)
- Scheduled Claude reasoning loops (with plan approval)
- Email sending via MCP (with approval)
- Facebook Page posting via official Meta Graph API (with approval)
- Agent Skills architecture

**Still Prohibited in Silver Tier**:
- Personal Facebook profile automation
- Browser automation or web scraping
- Direct API calls from Claude (must use MCP)
- Actions without approval workflow
- Autonomous destructive behavior
- Multiple MCP servers

## Operational Model

### Bronze Tier Workflow

1. User creates task file in `/Inbox`
2. File watcher detects new file and notifies user
3. User manually invokes Claude CLI to process inbox
4. Claude reads task, generates plan, moves to appropriate folder
5. User reviews and approves actions
6. Claude executes approved actions, updates state via folder movement
7. Completed tasks move to `/Done`

### Silver Tier Workflow (with Approval Gates)

1. User creates task file in `/Inbox` OR scheduled reasoning loop triggers
2. Watcher detects new file and notifies user
3. Claude processes task and generates execution plan
4. **If plan includes external actions**:
   a. Claude writes detailed action plan to `/Pending_Approval`
   b. Plan includes: objective, actions, risks, rollback procedure
   c. Human reviews plan and moves to `/Approved` or `/Rejected`
   d. Approved watcher detects approved plan
   e. Claude executes approved actions via MCP server
   f. Results logged to `/Done` with execution summary
5. **If plan is file-system only**: Follows Bronze Tier workflow
6. Completed tasks move to `/Done`

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
- For external actions: rollback procedure MUST be executed if defined in plan

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
- Silver Tier features MUST NOT be enabled until approval workflow is implemented

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

**Version**: 1.1.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-14
