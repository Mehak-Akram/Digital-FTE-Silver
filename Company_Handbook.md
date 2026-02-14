# Company Handbook

## Project Context

This is the Bronze Tier AI Employee project - a minimal local AI assistant that manages tasks through an Obsidian vault using folder-based state management.

**Architecture**: Bronze Tier (local-only, file system operations, manual AI trigger)

**Core Principles**:
- File system only operations within vault boundary
- Manual trigger model (no autonomous loops)
- Folder-based state management (Inbox → Needs_Action → Plans → Done)
- Single watcher architecture
- No external APIs or cloud services

## Task Guidelines

When processing tasks:
- Read task description carefully from the task file
- Interpret requirements based on project context
- Generate structured plans with clear, actionable steps
- Include acceptance criteria for verification
- Ask clarifying questions if requirements are ambiguous
- Reference this handbook for project-specific context

## Quality Standards

All plans must include:
- **Goal**: Clear statement of what the plan achieves
- **Steps**: Numbered list with specific actions and acceptance criteria
- **Acceptance Criteria**: Testable checkboxes for validation
- **Questions**: Section for clarifications (if needed)
- **Notes**: Additional context or considerations

Plans should be:
- Actionable and specific
- Testable with clear success criteria
- Free of implementation details (focus on WHAT, not HOW)
- Aligned with Bronze Tier constraints

## Communication Style

- Be concise and actionable
- Use bullet points and numbered lists for clarity
- Include examples when helpful
- Avoid jargon unless necessary
- Use ISO 8601 format for dates (YYYY-MM-DD)
- Use markdown formatting for structure

## Bronze Tier Constraints

**Allowed**:
- File system operations within E:\AI_Employee_Vault
- Manual Claude CLI invocation for task processing
- Folder-based state transitions
- Console logging for watcher events
- Markdown files with YAML frontmatter

**Prohibited**:
- External API calls
- MCP servers
- Cloud services
- Autonomous background loops
- Database systems
- Network operations beyond file I/O

## References

- Constitution: `.specify/memory/constitution.md`
- Specification: `specs/001-bronze-tier/spec.md`
- Implementation Plan: `specs/001-bronze-tier/plan.md`
- Data Model: `specs/001-bronze-tier/data-model.md`
- CLI Commands: `specs/001-bronze-tier/contracts/cli-commands.md`
- Quickstart Guide: `specs/001-bronze-tier/quickstart.md`

## State Transition Rules

- New tasks must start in Inbox/
- Watcher moves tasks to Needs_Action/
- Claude generates a Plan in Plans/
- After successful completion, move task and plan to Done/
- Dashboard.md must be updated after task completion
