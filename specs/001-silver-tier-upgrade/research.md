# Research & Technology Decisions: Silver Tier Upgrade

**Feature**: 001-silver-tier-upgrade | **Date**: 2026-02-14
**Purpose**: Document technology choices, rationale, and alternatives for Silver Tier implementation

## Research Areas

### 1. MCP SDK Selection

**Decision**: Use official `mcp` Python package from Anthropic

**Rationale**:
- Official SDK ensures compatibility with Claude Code CLI
- Built-in support for function registration and parameter validation
- Active maintenance and documentation from Anthropic
- Handles JSON-RPC protocol details automatically

**Alternatives Considered**:
- Custom JSON-RPC implementation: Rejected due to maintenance burden and protocol complexity
- Third-party MCP libraries: Rejected due to lack of official support and potential compatibility issues

**Implementation Notes**:
- Install via `pip install mcp`
- Server runs as standalone process, communicates via stdio
- Functions registered using `@server.call_tool()` decorator pattern

---

### 2. Windows Task Scheduler Integration

**Decision**: Use Python script with batch file wrapper triggered by Windows Task Scheduler

**Rationale**:
- Native Windows scheduling mechanism (no additional dependencies)
- Reliable execution every 10 minutes with built-in retry logic
- Can run with user privileges (no admin required)
- Logs accessible via Task Scheduler interface

**Alternatives Considered**:
- Python `schedule` library with while loop: Rejected due to process management complexity and lack of system-level monitoring
- Cron (via WSL): Rejected due to additional dependency and Windows-native requirement
- Windows Service: Rejected due to admin privileges requirement and deployment complexity

**Implementation Notes**:
- Create `.bat` file that activates Python venv and runs `reasoning_loop/main.py`
- Configure Task Scheduler with:
  - Trigger: Every 10 minutes, indefinitely
  - Action: Run batch file
  - Settings: Stop if runs longer than 8 minutes (prevent overlap)
  - Conditions: Start only if computer is on AC power (optional)

---

### 3. IMAP Email Monitoring

**Decision**: Use Python built-in `imaplib` with connection pooling and exponential backoff

**Rationale**:
- Built-in library (no external dependencies)
- Mature, stable implementation with Gmail IMAP support
- Supports IDLE command for efficient monitoring
- Well-documented error handling patterns

**Alternatives Considered**:
- `imapclient` library: Rejected due to external dependency when built-in solution sufficient
- Gmail API (REST): Rejected due to OAuth complexity and MCP server scope creep
- POP3: Rejected due to lack of message state tracking and folder support

**Implementation Notes**:
- Use IMAP IDLE for efficient monitoring (push-based, not polling)
- Implement exponential backoff: 1min → 2min → 5min → 10min on connection failures
- Mark processed emails as "seen" to avoid duplicate task creation
- Store last processed email UID in watcher state file

**Connection Pattern**:
```python
import imaplib
import time

def connect_with_retry(max_retries=4):
    backoff_times = [60, 120, 300, 600]  # 1min, 2min, 5min, 10min
    for attempt, wait_time in enumerate(backoff_times):
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email, password)
            return mail
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                raise
```

---

### 4. Meta Graph API Authentication

**Decision**: Use long-lived Page Access Token stored in `.env` file

**Rationale**:
- Page Access Tokens don't expire (unlike User Access Tokens)
- Simpler authentication flow (no OAuth redirect required)
- Appropriate for server-side automation
- Tokens scoped to specific Page (not user account)

**Alternatives Considered**:
- User Access Token: Rejected due to 60-day expiration and broader permissions
- OAuth flow: Rejected due to complexity and manual refresh requirement
- App Access Token: Rejected due to lack of Page posting permissions

**Implementation Notes**:
- Generate Page Access Token via Meta Developer Portal
- Store in `.env` file: `FACEBOOK_PAGE_ACCESS_TOKEN=<token>`
- Store Page ID in `.env` file: `FACEBOOK_PAGE_ID=<page_id>`
- Use Graph API v18.0 or later
- Endpoint: `POST https://graph.facebook.com/v18.0/{page_id}/feed`

**Security**:
- Never commit `.env` file to version control
- Provide `.env.example` with placeholder values
- Validate token on MCP server startup
- Implement token rotation reminder (manual process)

---

### 5. File Locking Mechanism

**Decision**: Use Python `fcntl` (Unix) / `msvcrt` (Windows) with retry logic

**Rationale**:
- Prevents race conditions between watchers and reasoning loop
- Built-in OS-level locking (no external dependencies)
- Cross-platform support with platform-specific implementations
- Automatic lock release on process termination

**Alternatives Considered**:
- File-based semaphores: Rejected due to stale lock file issues
- Database locks: Rejected due to no-database constraint
- Optimistic locking with timestamps: Rejected due to race condition risk

**Implementation Notes**:
- Wrap all file read/write operations with lock acquisition
- Use exclusive locks for writes, shared locks for reads
- Implement timeout (5 seconds) to prevent deadlocks
- Log lock contention for debugging

**Cross-Platform Pattern**:
```python
import sys
import time

if sys.platform == 'win32':
    import msvcrt
    def lock_file(file_handle):
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
else:
    import fcntl
    def lock_file(file_handle):
        fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
```

---

### 6. File System Monitoring (Watchdog)

**Decision**: Use `watchdog` library with `FileSystemEventHandler`

**Rationale**:
- Cross-platform file system monitoring
- Event-driven architecture (efficient, no polling)
- Mature library with active maintenance
- Supports recursive directory watching

**Alternatives Considered**:
- Polling with `os.listdir()`: Rejected due to inefficiency and CPU usage
- Built-in `os.stat()` with timestamps: Rejected due to polling overhead
- Windows-specific APIs: Rejected due to lack of cross-platform support

**Implementation Notes**:
- Install via `pip install watchdog`
- Use `Observer` pattern with folder-specific event handlers
- Filter events by file extension (`.md` only)
- Debounce rapid file changes (wait 1 second after last modification)

**Watcher Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        # Process new task file

observer = Observer()
observer.schedule(InboxHandler(), path='E:/AI_Employee_Vault/Inbox', recursive=False)
observer.start()
```

---

### 7. YAML Frontmatter Parsing

**Decision**: Use `python-frontmatter` library

**Rationale**:
- Purpose-built for Markdown files with YAML frontmatter
- Handles both frontmatter and content body
- Preserves formatting on round-trip (read → modify → write)
- Widely used in static site generators (proven reliability)

**Alternatives Considered**:
- Manual parsing with `yaml.safe_load()`: Rejected due to edge case handling complexity
- `PyYAML` alone: Rejected due to lack of Markdown integration
- Regex-based parsing: Rejected due to fragility and maintenance burden

**Implementation Notes**:
- Install via `pip install python-frontmatter`
- Use `frontmatter.load()` to read files
- Use `frontmatter.dump()` to write files
- Access frontmatter via dictionary: `post.metadata['status']`
- Access content via: `post.content`

**Usage Pattern**:
```python
import frontmatter

# Read
post = frontmatter.load('task.md')
status = post.metadata.get('status', 'new')

# Modify
post.metadata['status'] = 'completed'
post.metadata['completed_at'] = '2026-02-14T10:30:00Z'

# Write
with open('task.md', 'w', encoding='utf-8') as f:
    f.write(frontmatter.dumps(post))
```

---

### 8. Error Handling & Retry Strategies

**Decision**: Implement exponential backoff with circuit breaker pattern for external APIs

**Rationale**:
- Exponential backoff prevents API rate limit exhaustion
- Circuit breaker prevents cascading failures
- Graceful degradation maintains system stability
- Aligns with industry best practices (AWS, Google Cloud patterns)

**Retry Strategy**:
- **Transient errors** (network timeout, 5xx): Retry with exponential backoff (1s, 2s, 4s, 8s, 16s)
- **Rate limits** (429): Retry after `Retry-After` header value
- **Authentication errors** (401, 403): No retry, move plan to Pending_Approval with error
- **Client errors** (4xx except 429): No retry, log error and fail plan

**Circuit Breaker**:
- Open circuit after 5 consecutive failures
- Half-open after 60 seconds (allow single test request)
- Close circuit after 3 consecutive successes
- Log circuit state changes for monitoring

**Implementation Notes**:
- Use `tenacity` library for retry logic: `pip install tenacity`
- Implement circuit breaker in MCP server handlers
- Log all retry attempts with timestamps
- Include retry count in plan execution summary

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| MCP Server | `mcp` (official SDK) | Latest | Official support, protocol handling |
| Task Scheduler | Windows Task Scheduler | Built-in | Native, reliable, no dependencies |
| Email Monitoring | `imaplib` | Built-in | Mature, Gmail support, no dependencies |
| Facebook API | Meta Graph API v18.0+ | v18.0+ | Official API, Page posting support |
| File Watching | `watchdog` | 4.0+ | Event-driven, cross-platform |
| Frontmatter | `python-frontmatter` | 1.0+ | Purpose-built, formatting preservation |
| File Locking | `msvcrt` (Windows) | Built-in | OS-level, automatic cleanup |
| Retry Logic | `tenacity` | 8.0+ | Declarative, exponential backoff |
| Environment | `python-dotenv` | 1.0+ | Secure credential management |
| HTTP Client | `requests` | 2.31+ | Industry standard, reliable |

---

## Dependencies Installation

```bash
pip install mcp watchdog python-frontmatter tenacity python-dotenv requests pyyaml pytest
```

---

## Security Considerations

1. **Credential Storage**: All sensitive credentials (email passwords, Facebook tokens) stored in `.env` file, never committed to version control
2. **Token Validation**: MCP server validates tokens on startup, fails fast if invalid
3. **Input Sanitization**: All external action parameters validated before execution (prevent injection attacks)
4. **Rate Limiting**: MCP server implements per-API rate limits to prevent quota exhaustion
5. **Audit Logging**: All external actions logged with timestamps, parameters, and results
6. **Approval Enforcement**: MCP server checks plan approval status before execution (defense in depth)

---

## Open Questions

None - all technology decisions resolved.

---

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with entity definitions
- Create contracts/ directory with API schemas
- Create quickstart.md with setup instructions
