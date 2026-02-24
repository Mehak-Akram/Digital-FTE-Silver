---
skill_name: email_skill
description: Composes and sends emails via MCP server with approval workflow and retry logic
version: 1.0.0
required_permissions:
  - file_read
  - mcp_email
external_dependencies:
  - mcp_server
requires_approval: true
error_handling:
  retry_strategy: exponential_backoff
  max_retries: 3
  fallback_action: Move plan back to Pending_Approval with error message and retry instructions
rollback_procedure: If email sending fails, log error details in plan frontmatter, move plan back to Pending_Approval with error message, notify human via pending_approval_watcher for manual retry or modification
---

# Email Skill

**Purpose**: Send emails via MCP server after human approval with automatic retry on transient failures.

## Execution Logic

1. **Validate plan approval**
   - Verify plan is in Approved folder
   - Check approved_at timestamp exists
   - Confirm approved_by field is set

2. **Extract email parameters from plan**
   - Parse plan steps to find send_email action
   - Extract recipient (to), subject, body from parameters
   - Extract optional CC, BCC if present

3. **Call MCP server send_email function**
   - Connect to MCP server via stdio
   - Invoke send_email with parameters
   - Handle response (success or error)

4. **Implement retry logic on transient failures**
   - SMTP connection errors: Retry with exponential backoff (1s, 2s, 4s, 8s, 16s)
   - Rate limit errors: Wait for retry_after_seconds, then retry
   - Authentication errors: No retry, return error immediately
   - Invalid recipient: No retry, return error immediately

5. **Log execution results**
   - Success: Log message_id, timestamp, recipient
   - Failure: Log error code, error message, retry count

6. **Update plan status**
   - Success: Move plan to Done/ with execution summary
   - Failure after max retries: Move plan back to Pending_Approval with error details

7. **Notify human of results**
   - Success: Log completion message
   - Failure: Trigger pending_approval_watcher notification

## Input Format

**Approved Plan File** (in Approved/ folder):

```yaml
---
id: "20260215-143000-send-weekly-report"
task_id: "20260215-143000-send-weekly-report"
objective: "Send weekly project status report to team@example.com"
requires_approval: true
created_at: "2026-02-15T14:35:00Z"
approved_at: "2026-02-15T15:00:00Z"
approved_by: "human"
execution_status: "pending"
---

# Execution Plan: Send weekly report to team

## Steps

1. **Send email via MCP** (action_type: send_email)
   - Parameters: to="team@example.com", subject="Weekly Status", body=<content>
   - Expected outcome: Email delivered successfully

## Risks

- Email delivery failure due to SMTP server issues
- Recipient email address may be invalid

## Rollback Procedure

1. Log error details in plan frontmatter
2. Move plan back to Pending_Approval with error message
3. Notify human via pending_approval_watcher
4. Human can modify recipient or retry

## Action Preview

**Email Preview**:
- To: team@example.com
- Subject: Weekly Project Status
- Body: (first 500 chars)
  "Hi team, here's our weekly update..."
```

## Output Format

**Completed Plan** (moved to Done/ folder):

```yaml
---
id: "20260215-143000-send-weekly-report"
task_id: "20260215-143000-send-weekly-report"
objective: "Send weekly project status report to team@example.com"
requires_approval: true
created_at: "2026-02-15T14:35:00Z"
approved_at: "2026-02-15T15:00:00Z"
approved_by: "human"
executed_at: "2026-02-15T15:05:00Z"
completed_at: "2026-02-15T15:05:30Z"
execution_status: "completed"
execution_summary: "Email sent successfully to team@example.com. Message ID: <abc123@smtp.gmail.com>. Delivery timestamp: 2026-02-15T15:05:30Z"
---

[Plan content remains the same]
```

## Examples

### Example 1: Successful email delivery

**Input**: Approved plan with send_email action
**Process**: MCP server sends email via SMTP
**Output**: Plan moved to Done/ with message_id and timestamp

### Example 2: Transient SMTP error with retry

**Input**: Approved plan with send_email action
**Process**: First attempt fails with connection error, retry after 1s succeeds
**Output**: Plan moved to Done/ with retry_count=1 in execution summary

### Example 3: Invalid recipient error

**Input**: Approved plan with invalid email address
**Process**: MCP server returns INVALID_RECIPIENT error
**Output**: Plan moved back to Pending_Approval with error message, no retry

## Edge Cases

- **Empty email body**: Validate body is non-empty before sending
- **Missing recipient**: Return error if 'to' parameter not found
- **Rate limit exceeded**: Wait for retry_after_seconds from MCP response
- **SMTP authentication failure**: Move plan back to Pending_Approval with clear error message
- **Network timeout**: Retry with exponential backoff up to max_retries
- **Plan not approved**: Refuse to execute, log security warning
