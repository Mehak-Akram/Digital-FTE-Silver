---
skill_name: facebook_skill
description: Composes and posts to Facebook Pages via MCP server with approval workflow and circuit breaker pattern
version: 1.0.0
required_permissions:
  - file_read
  - mcp_facebook
external_dependencies:
  - mcp_server
requires_approval: true
error_handling:
  retry_strategy: circuit_breaker
  max_retries: 3
  fallback_action: Move plan back to Pending_Approval with error message and retry instructions
rollback_procedure: If Facebook posting fails, log error details in plan frontmatter, move plan back to Pending_Approval with error message, notify human via pending_approval_watcher for manual retry or modification. Note that posts cannot be automatically deleted once published.
---

# Facebook Skill

**Purpose**: Post content to Facebook Pages via Meta Graph API after human approval with circuit breaker protection.

## Execution Logic

1. **Validate plan approval**
   - Verify plan is in Approved folder
   - Check approved_at timestamp exists
   - Confirm approved_by field is set

2. **Extract Facebook post parameters from plan**
   - Parse plan steps to find post_facebook action
   - Extract message content from parameters
   - Extract optional link if present

3. **Call MCP server post_facebook_page function**
   - Connect to MCP server via stdio
   - Invoke post_facebook_page with parameters
   - Handle response (success or error)

4. **Implement circuit breaker pattern**
   - Track consecutive failures
   - Open circuit after 5 consecutive failures
   - Half-open after 60 seconds (allow single test request)
   - Close circuit after 3 consecutive successes
   - Log circuit state changes

5. **Handle API-specific errors**
   - Rate limit (429): Wait for retry_after_seconds, then retry
   - Invalid token (401/403): No retry, return error immediately
   - Spam detected: No retry, return error immediately
   - Connection errors: Retry with circuit breaker logic

6. **Log execution results**
   - Success: Log post_id, post_url, timestamp
   - Failure: Log error code, error message, retry count

7. **Update plan status**
   - Success: Move plan to Done/ with execution summary
   - Failure after max retries: Move plan back to Pending_Approval with error details

8. **Notify human of results**
   - Success: Log completion message with post URL
   - Failure: Trigger pending_approval_watcher notification

## Input Format

**Approved Plan File** (in Approved/ folder):

```yaml
---
id: "20260215-150000-announce-product"
task_id: "20260215-150000-announce-product"
objective: "Post product announcement to Facebook Page"
requires_approval: true
created_at: "2026-02-15T15:00:00Z"
approved_at: "2026-02-15T15:30:00Z"
approved_by: "human"
execution_status: "pending"
---

# Execution Plan: Announce product launch

## Steps

1. **Post to Facebook Page via MCP** (action_type: post_facebook)
   - Parameters: message=<content>, link="https://example.com/product"
   - Expected outcome: Post published successfully

## Risks

- Facebook API rate limit may be exceeded
- Access token may be invalid or expired
- Content may be flagged as spam

## Rollback Procedure

1. Log error details in plan frontmatter
2. Move plan back to Pending_Approval with error message
3. Notify human via pending_approval_watcher
4. Human can modify content or retry
5. Note: Published posts cannot be automatically deleted

## Action Preview

**Facebook Post Preview**:
- Message: Excited to announce our new product launch! Learn more at https://example.com/product
```

## Output Format

**Completed Plan** (moved to Done/ folder):

```yaml
---
id: "20260215-150000-announce-product"
task_id: "20260215-150000-announce-product"
objective: "Post product announcement to Facebook Page"
requires_approval: true
created_at: "2026-02-15T15:00:00Z"
approved_at: "2026-02-15T15:30:00Z"
approved_by: "human"
executed_at: "2026-02-15T15:35:00Z"
completed_at: "2026-02-15T15:35:15Z"
execution_status: "completed"
execution_summary: "Facebook post published successfully. Post ID: 123456789_987654321. Post URL: https://facebook.com/123456789/posts/987654321. Timestamp: 2026-02-15T15:35:15Z"
---

[Plan content remains the same]
```

## Examples

### Example 1: Successful post

**Input**: Approved plan with post_facebook action
**Process**: MCP server posts to Facebook Page via Graph API
**Output**: Plan moved to Done/ with post_id and post_url

### Example 2: Rate limit error with circuit breaker

**Input**: Approved plan when rate limit is near
**Process**: First attempt fails with 429, circuit breaker opens, retry after cooldown
**Output**: Plan moved to Done/ after successful retry, or back to Pending_Approval if circuit remains open

### Example 3: Invalid access token

**Input**: Approved plan with expired token
**Process**: MCP server returns INVALID_ACCESS_TOKEN error
**Output**: Plan moved back to Pending_Approval with clear error message, no retry

## Edge Cases

- **Empty message**: Validate message is non-empty before posting
- **Message too long**: Validate message length (max 63,206 characters per Facebook limit)
- **Spam detection**: If Facebook flags content as spam, return error with explanation
- **Circuit breaker open**: Refuse to execute, move plan back to Pending_Approval with circuit status
- **Network timeout**: Retry with circuit breaker logic up to max_retries
- **Plan not approved**: Refuse to execute, log security warning
- **Post already published**: Check for duplicate post_id in execution logs to prevent duplicates
