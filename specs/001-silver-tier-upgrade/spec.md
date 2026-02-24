# Feature Specification: Silver Tier Upgrade

**Feature Branch**: `001-silver-tier-upgrade`
**Created**: 2026-02-14
**Status**: Draft
**Input**: User description: "Create the Silver Tier specification for the Personal AI Employee. Upgrade the Bronze AI Employee into a functional assistant capable of external business automation using Facebook Page posting and email sending."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Task Planning (Priority: P1) 🎯 MVP

The AI Employee automatically scans pending tasks every 10 minutes, analyzes them, and generates structured execution plans without manual intervention. Plans requiring external actions are automatically routed for human approval.

**Why this priority**: This is the foundation of Silver Tier - transforming from manual trigger (Bronze) to scheduled autonomous reasoning. Without this, all other Silver Tier features cannot function.

**Independent Test**: Can be fully tested by placing a task file in Needs_Action folder, waiting for the scheduled scan (max 10 minutes), and verifying a Plan file is generated and routed to the appropriate folder (Plans for file-only tasks, Pending_Approval for external actions).

**Acceptance Scenarios**:

1. **Given** a task file exists in Needs_Action folder, **When** the scheduled reasoning loop executes, **Then** the AI reads the task, generates a structured Plan file with objective, steps, risks, and rollback procedure
2. **Given** a generated plan contains only file system operations, **When** the plan is complete, **Then** the plan is moved to Plans folder for immediate execution
3. **Given** a generated plan requires external actions (email or Facebook posting), **When** the plan is complete, **Then** the plan is moved to Pending_Approval folder and human is notified
4. **Given** the reasoning loop encounters an error, **When** processing fails, **Then** the task remains in Needs_Action with error details logged in frontmatter

---

### User Story 2 - Email Automation (Priority: P2)

The AI Employee can send emails on behalf of the user after receiving explicit approval. Emails are composed based on task requirements and sent through a secure email service.

**Why this priority**: Email is the most common business communication tool. This enables the AI to handle routine email tasks like notifications, reminders, and status updates.

**Independent Test**: Can be fully tested by creating a task requesting an email be sent, approving the generated plan in Pending_Approval, and verifying the email is sent and logged in Done folder.

**Acceptance Scenarios**:

1. **Given** an approved plan in Approved folder contains send_email action, **When** the AI executes the plan, **Then** the email is sent via MCP server with specified recipient, subject, and body
2. **Given** an email sending task, **When** the AI generates the plan, **Then** the plan includes email preview (to, subject, body) for human review before approval
3. **Given** email sending fails, **When** the MCP server returns an error, **Then** the plan is moved back to Pending_Approval with error details and retry option
4. **Given** a successfully sent email, **When** execution completes, **Then** the plan is moved to Done with timestamp, recipient confirmation, and email content logged

---

### User Story 3 - Facebook Page Posting (Priority: P3)

The AI Employee can post content to a Facebook Page using the official Meta Graph API after receiving explicit approval. Posts are composed based on task requirements and published to the specified Page.

**Why this priority**: Social media automation enables consistent business presence. Facebook Pages are business accounts (not personal profiles), making this appropriate for business automation.

**Independent Test**: Can be fully tested by creating a task requesting a Facebook post, approving the generated plan, and verifying the post appears on the Facebook Page and is logged in Done folder.

**Acceptance Scenarios**:

1. **Given** an approved plan in Approved folder contains post_facebook_page action, **When** the AI executes the plan, **Then** the post is published to the Facebook Page via Meta Graph API
2. **Given** a Facebook posting task, **When** the AI generates the plan, **Then** the plan includes post preview (message content, target Page) for human review before approval
3. **Given** Facebook posting fails, **When** the API returns an error, **Then** the plan is moved back to Pending_Approval with error details and retry option
4. **Given** a successfully published post, **When** execution completes, **Then** the plan is moved to Done with timestamp, post URL, and content logged

---

### User Story 4 - Gmail Monitoring (Priority: P4)

The AI Employee monitors a Gmail inbox using IMAP protocol and automatically creates task files for incoming emails that match specified criteria. This enables email-driven task creation.

**Why this priority**: This completes the automation loop - the AI can now both receive inputs (via email) and send outputs (via email). Lower priority because the system is functional without it.

**Independent Test**: Can be fully tested by sending an email to the monitored Gmail account and verifying a task file is created in Inbox folder with email details (sender, subject, body) within the monitoring interval.

**Acceptance Scenarios**:

1. **Given** the Gmail watcher is running, **When** a new email arrives in the monitored inbox, **Then** a task file is created in Inbox folder with email metadata (from, subject, date) and body content
2. **Given** an email-generated task, **When** the task file is created, **Then** the frontmatter includes email_source: true and original_email_id for tracking
3. **Given** the Gmail watcher encounters connection errors, **When** IMAP connection fails, **Then** the watcher logs the error and retries with exponential backoff (1min, 2min, 5min, 10min)
4. **Given** multiple emails arrive simultaneously, **When** the watcher processes them, **Then** each email generates a separate task file with unique timestamp-based filenames

---

### Edge Cases

- What happens when the reasoning loop is already running and the next scheduled execution time arrives? (Skip the scheduled run and log a warning)
- How does the system handle approval timeout? (Plans remain in Pending_Approval indefinitely until human action)
- What happens when MCP server is unavailable during plan execution? (Log error, move plan back to Pending_Approval with retry instructions)
- How does the system handle malformed task files in Needs_Action? (Log error in file frontmatter, move to Inbox for user correction)
- What happens when Windows Task Scheduler fails to trigger the reasoning loop? (System continues to function manually; user notified via log file)
- How does the system handle Facebook API rate limits? (MCP server implements rate limiting; failed posts return to Pending_Approval with retry timing)
- What happens when Gmail watcher detects spam or promotional emails? (Configurable filter rules determine which emails create tasks)
- How does the system handle concurrent file access? (File locking mechanism prevents race conditions between watchers and reasoning loop)

## Requirements *(mandatory)*

### Functional Requirements

**Reasoning Loop:**
- **FR-001**: System MUST execute a scheduled reasoning loop every 10 minutes using Windows Task Scheduler
- **FR-002**: Reasoning loop MUST scan all files in Needs_Action folder and process them sequentially
- **FR-003**: Reasoning loop MUST generate structured Plan files containing: objective, steps, risks, rollback procedure, and approval requirement flag
- **FR-004**: System MUST route plans with external actions to Pending_Approval folder automatically
- **FR-005**: System MUST route plans with only file system operations to Plans folder automatically
- **FR-006**: Reasoning loop MUST log all activities (start time, files processed, plans generated, errors) to a daily log file

**Approval Workflow:**
- **FR-007**: System MUST monitor Approved folder for human-approved plans
- **FR-008**: System MUST execute only plans that have been moved to Approved folder by human action
- **FR-009**: System MUST NOT execute plans in Pending_Approval or Rejected folders
- **FR-010**: System MUST move completed plans to Done folder with execution summary in frontmatter
- **FR-011**: System MUST move failed plans back to Pending_Approval with error details and retry instructions

**MCP Server Integration:**
- **FR-012**: System MUST route all external actions through a single MCP server (no direct API calls from AI)
- **FR-013**: MCP server MUST implement send_email(to, subject, body) function with SMTP integration
- **FR-014**: MCP server MUST implement post_facebook_page(message) function using Meta Graph API
- **FR-015**: MCP server MUST implement rate limiting to prevent API quota exhaustion
- **FR-016**: MCP server MUST log all external actions with timestamps, parameters, and results
- **FR-017**: MCP server configuration MUST be stored in mcp_server folder and version-controlled

**Email Automation:**
- **FR-018**: System MUST support sending emails via MCP server with recipient, subject, and body parameters
- **FR-019**: Email plans MUST include full email preview (to, subject, body) for human review before approval
- **FR-020**: System MUST log sent emails in Done folder with timestamp, recipient, subject, and delivery status
- **FR-021**: System MUST handle email sending failures gracefully with error messages and retry options

**Facebook Page Posting:**
- **FR-022**: System MUST post to Facebook Pages using official Meta Graph API (not personal profiles)
- **FR-023**: System MUST use secure Page Access Token stored in environment configuration
- **FR-024**: Facebook post plans MUST include post preview (message content, target Page) for human review
- **FR-025**: System MUST log published posts in Done folder with timestamp, post URL, and content
- **FR-026**: System MUST handle Facebook API errors (rate limits, authentication failures) with appropriate error messages

**Gmail Monitoring:**
- **FR-027**: System MUST monitor Gmail inbox using IMAP protocol
- **FR-028**: Gmail watcher MUST check for new emails at regular intervals (configurable, default 5 minutes)
- **FR-029**: System MUST create task files in Inbox folder for each new email with metadata (from, subject, date, body)
- **FR-030**: Email-generated tasks MUST include email_source flag and original_email_id in frontmatter for tracking
- **FR-031**: Gmail watcher MUST implement connection retry logic with exponential backoff on failures

**Agent Skills:**
- **FR-032**: System MUST implement three agent skills: planner_skill, email_skill, facebook_skill
- **FR-033**: Each skill MUST be stored as a self-contained file in Skills folder
- **FR-034**: Skills MUST declare required permissions, external dependencies, and approval requirements
- **FR-035**: Skills MUST include error handling and rollback procedures
- **FR-036**: System MUST load and execute skills dynamically based on task requirements

**Watchers:**
- **FR-037**: System MUST run Inbox file watcher (Bronze Tier) to detect new task files
- **FR-038**: System MUST run Pending_Approval watcher to notify human when new plans require review
- **FR-039**: System MUST run Approved watcher to detect human-approved plans ready for execution
- **FR-040**: System MUST run Gmail watcher to monitor incoming emails
- **FR-041**: Each watcher MUST have a single, well-defined responsibility and operate independently

**Security & Safety:**
- **FR-042**: System MUST require human approval for all external actions (email, Facebook posting)
- **FR-043**: System MUST NOT automate personal Facebook profiles (only business Pages)
- **FR-044**: System MUST NOT perform browser automation or web scraping
- **FR-045**: System MUST store sensitive credentials (email passwords, Facebook tokens) in secure environment configuration (not in files)
- **FR-046**: System MUST validate all external action parameters before execution to prevent injection attacks

### Key Entities

- **Task**: Represents work to be done; stored as Markdown file with YAML frontmatter; moves through folders (Inbox → Needs_Action → Plans/Pending_Approval → Approved → Done)
- **Plan**: Structured execution plan generated by reasoning loop; contains objective, steps, risks, rollback procedure, approval flag; determines routing to Plans or Pending_Approval
- **Approval Request**: Plan requiring human review; stored in Pending_Approval folder; includes action preview, risks, and approval instructions
- **Agent Skill**: Modular AI capability stored in Skills folder; declares permissions, dependencies, approval requirements, error handling, and rollback procedures
- **MCP Server Configuration**: Settings for external integrations; stored in mcp_server folder; includes API endpoints, authentication, rate limits, and logging preferences
- **Watcher**: Background process monitoring specific folder; detects file changes and triggers appropriate actions; four watchers in Silver Tier (Inbox, Pending_Approval, Approved, Gmail)
- **Execution Log**: Record of reasoning loop activities; daily log file containing timestamps, processed files, generated plans, executed actions, and errors

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Reasoning loop executes successfully every 10 minutes without manual intervention for 24 hours
- **SC-002**: Tasks in Needs_Action folder are processed and converted to Plans within one reasoning loop cycle (10 minutes maximum)
- **SC-003**: Plans requiring external actions are correctly routed to Pending_Approval with 100% accuracy
- **SC-004**: Approved plans are executed within one reasoning loop cycle after approval (10 minutes maximum)
- **SC-005**: Email sending success rate exceeds 95% for approved email plans
- **SC-006**: Facebook posts are published successfully within 2 minutes of plan approval
- **SC-007**: Gmail watcher detects new emails and creates task files within 5 minutes of email arrival
- **SC-008**: System handles 20 concurrent tasks across all folders without performance degradation
- **SC-009**: All external actions are logged with complete audit trail (timestamp, parameters, results) in Done folder
- **SC-010**: Zero unauthorized external actions occur (all external actions require and receive human approval)
- **SC-011**: System recovers gracefully from MCP server failures with appropriate error messages and retry options
- **SC-012**: Watchers maintain 99% uptime over 7-day period with automatic recovery from transient failures

## Assumptions

- Windows Task Scheduler is available and configured on the host system
- User has valid Gmail account with IMAP access enabled
- User has Facebook Page (not personal profile) with Page Access Token
- User has configured MCP server with email service credentials (SMTP)
- User has configured MCP server with Facebook Page Access Token
- Obsidian vault remains accessible at E:\AI_Employee_Vault
- Claude CLI is installed and accessible via command line
- User will manually review and approve plans in Pending_Approval folder (no automatic approval)
- Network connectivity is available for external actions (email, Facebook, Gmail)
- File system supports file locking to prevent concurrent access issues

## Dependencies

- Bronze Tier functionality (file system operations, folder-based state management, Inbox watcher)
- Windows Task Scheduler for reasoning loop scheduling
- MCP server implementation for external integrations
- Gmail account with IMAP enabled
- Facebook Page with valid Page Access Token
- Claude Code CLI (Sonnet 4.5)
- Secure environment configuration for credentials (.env file or equivalent)

## Out of Scope

- Personal Facebook profile automation (prohibited by constitution)
- Browser automation or web scraping (prohibited by constitution)
- Multiple MCP servers (Silver Tier limited to one)
- Automatic approval of external actions (human approval required)
- Email composition using AI language models (emails composed from task requirements only)
- Facebook post scheduling (posts published immediately upon approval)
- Gmail sending (only receiving/monitoring in Silver Tier)
- Multi-user support (single user system)
- Mobile app or web interface (file system and CLI only)
- Integration with other social media platforms (Facebook Pages only in Silver Tier)
