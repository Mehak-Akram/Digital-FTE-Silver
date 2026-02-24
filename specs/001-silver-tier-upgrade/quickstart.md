# Silver Tier Quickstart Guide

**Feature**: 001-silver-tier-upgrade | **Version**: 1.0.0 | **Date**: 2026-02-15

This guide walks you through setting up and using the Silver Tier AI Employee with scheduled reasoning loops, approval workflows, and external integrations (email and Facebook Page posting).

## Prerequisites

- Windows 10 or later
- Python 3.11 or higher
- Obsidian vault at `E:\AI_Employee_Vault`
- Claude Code CLI installed
- Gmail account with IMAP enabled
- Facebook Page (not personal profile) with Page Access Token
- SMTP email service credentials

## Installation

### 1. Install Python Dependencies

```bash
cd E:\AI_Employee_Vault
pip install mcp watchdog python-frontmatter tenacity python-dotenv requests pyyaml pytest
```

### 2. Create Folder Structure

Create the Silver Tier folder structure:

```bash
# State management folders
mkdir -p Pending_Approval Approved Rejected Skills mcp_server

# MCP server subdirectories
mkdir -p mcp_server/logs

# Watcher and reasoning loop directories
mkdir -p watchers reasoning_loop shared tests/unit tests/integration tests/contract
```

Verify Bronze Tier folders exist:
- `Inbox/`
- `Needs_Action/`
- `Plans/`
- `Done/`

### 3. Configure Environment Variables

Create `.env` file in vault root:

```bash
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Facebook Configuration
FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_PAGE_ACCESS_TOKEN=your-page-access-token

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
```

**Security**: Never commit `.env` to version control. Add to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

### 4. Generate Facebook Page Access Token

1. Go to [Meta Developer Portal](https://developers.facebook.com/)
2. Create or select your app
3. Navigate to **Tools** → **Access Token Tool**
4. Select your Facebook Page
5. Generate a **Page Access Token** with permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
6. Copy token to `.env` file as `FACEBOOK_PAGE_ACCESS_TOKEN`
7. Copy Page ID to `.env` file as `FACEBOOK_PAGE_ID`

**Note**: Page Access Tokens don't expire (unlike User Access Tokens).

### 5. Enable Gmail IMAP

1. Go to [Gmail Settings](https://mail.google.com/mail/u/0/#settings/fwdandpop)
2. Click **Forwarding and POP/IMAP** tab
3. Enable **IMAP access**
4. Click **Save Changes**
5. Generate an **App Password** (if using 2FA):
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Select **2-Step Verification** → **App passwords**
   - Generate password for "Mail" on "Windows Computer"
   - Copy password to `.env` file as `EMAIL_PASSWORD`

### 6. Configure MCP Server

Create `mcp_server/config.json`:

```json
{
  "server_name": "silver_tier_mcp",
  "version": "1.0.0",
  "enabled_functions": ["send_email", "post_facebook_page"],
  "email_config": {
    "smtp_host": "${SMTP_HOST}",
    "smtp_port": "${SMTP_PORT}",
    "smtp_use_tls": "${SMTP_USE_TLS}",
    "from_address": "${EMAIL_ADDRESS}",
    "credentials_env_var": "EMAIL_PASSWORD"
  },
  "facebook_config": {
    "api_version": "v18.0",
    "page_id_env_var": "FACEBOOK_PAGE_ID",
    "access_token_env_var": "FACEBOOK_PAGE_ACCESS_TOKEN"
  },
  "rate_limits": {
    "email_per_hour": 50,
    "facebook_per_hour": 25
  },
  "logging": {
    "log_level": "${LOG_LEVEL}",
    "log_file_path": "mcp_server/logs/mcp-server-{date}.log",
    "log_retention_days": "${LOG_RETENTION_DAYS}"
  }
}
```

### 7. Set Up Windows Task Scheduler

Create batch file `run_reasoning_loop.bat`:

```batch
@echo off
cd /d E:\AI_Employee_Vault
python reasoning_loop/main.py >> mcp_server/logs/reasoning-loop.log 2>&1
```

Configure Task Scheduler:

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Task** (not "Create Basic Task")
3. **General** tab:
   - Name: `AI Employee Reasoning Loop`
   - Description: `Runs Silver Tier reasoning loop every 10 minutes`
   - Run whether user is logged on or not: ✓
   - Run with highest privileges: ✗ (not needed)
4. **Triggers** tab:
   - Click **New**
   - Begin the task: **On a schedule**
   - Settings: **Daily**, start at 00:00:00
   - Repeat task every: **10 minutes**
   - For a duration of: **Indefinitely**
   - Enabled: ✓
5. **Actions** tab:
   - Click **New**
   - Action: **Start a program**
   - Program/script: `E:\AI_Employee_Vault\run_reasoning_loop.bat`
   - Start in: `E:\AI_Employee_Vault`
6. **Conditions** tab:
   - Start only if computer is on AC power: ✗ (optional)
   - Wake the computer to run this task: ✗
7. **Settings** tab:
   - Allow task to be run on demand: ✓
   - Stop the task if it runs longer than: **8 minutes** (prevent overlap)
   - If the running task does not end when requested: **Stop the existing instance**
8. Click **OK** to save

**Test the task**: Right-click task → **Run** to verify it executes successfully.

## Usage

### Creating a Task

1. Create a new Markdown file in `Inbox/` folder:

```markdown
---
id: "20260215-143000-send-weekly-report"
title: "Send weekly report to team"
status: "new"
created_at: "2026-02-15T14:30:00Z"
updated_at: "2026-02-15T14:30:00Z"
priority: "P2"
source: "manual"
---

# Task: Send weekly report to team

Send the weekly project status report to the team via email.

**Recipients**: team@example.com
**Subject**: Weekly Project Status - Week of Feb 15
**Content**: Include completed tasks, blockers, and next week's priorities.
```

2. Save the file (e.g., `20260215-143000-send-weekly-report.md`)
3. The Inbox watcher will detect the new file
4. Move the file to `Needs_Action/` folder for processing

### Automated Processing

The reasoning loop (runs every 10 minutes) will:

1. Scan `Needs_Action/` folder for tasks
2. Generate a structured Plan file
3. Route the plan based on action types:
   - **File-only actions** → `Plans/` folder (execute immediately)
   - **External actions** → `Pending_Approval/` folder (requires human approval)

### Approving External Actions

When a plan requires approval:

1. Check `Pending_Approval/` folder for new plans
2. Open the plan file and review:
   - **Objective**: What the plan achieves
   - **Steps**: Detailed actions to perform
   - **Action Preview**: Email/Facebook post content
   - **Risks**: Potential failure modes
   - **Rollback Procedure**: How to undo if it fails
3. Make a decision:
   - **Approve**: Move file to `Approved/` folder
   - **Reject**: Move file to `Rejected/` folder
   - **Modify**: Edit plan content, keep in `Pending_Approval/`

The reasoning loop will detect approved plans and execute them via MCP server.

### Monitoring Execution

Check execution logs:

```bash
# Reasoning loop logs
tail -f mcp_server/logs/reasoning-loop.log

# MCP server logs
tail -f mcp_server/logs/mcp-server-2026-02-15.log
```

Completed tasks appear in `Done/` folder with execution summary in frontmatter.

## Watchers

Silver Tier runs four watchers:

### 1. Inbox Watcher (Bronze Tier)

**Purpose**: Detects new task files in `Inbox/` folder
**Action**: Notifies user of new tasks
**Status**: Check with `ps aux | grep inbox_watcher`

### 2. Gmail Watcher (New)

**Purpose**: Monitors Gmail inbox via IMAP for new emails
**Action**: Creates task files in `Inbox/` for each new email
**Configuration**: Edit `watchers/gmail_watcher.py` to set filter rules
**Status**: Check with `ps aux | grep gmail_watcher`

### 3. Pending Approval Watcher (New)

**Purpose**: Monitors `Pending_Approval/` folder for new approval requests
**Action**: Notifies user when plans require review
**Status**: Check with `ps aux | grep pending_approval_watcher`

### 4. Approved Watcher (New)

**Purpose**: Monitors `Approved/` folder for human-approved plans
**Action**: Triggers plan execution via reasoning loop
**Status**: Check with `ps aux | grep approved_watcher`

## Agent Skills

Silver Tier includes three agent skills in `Skills/` folder:

### 1. planner_skill.md

**Purpose**: Generates execution plans from tasks
**Permissions**: `file_read`, `file_write`, `file_move`
**Approval Required**: No

### 2. email_skill.md

**Purpose**: Composes and sends emails via MCP
**Permissions**: `file_read`, `mcp_email`
**Approval Required**: Yes

### 3. facebook_skill.md

**Purpose**: Posts to Facebook Pages via MCP
**Permissions**: `file_read`, `mcp_facebook`
**Approval Required**: Yes

Skills are loaded dynamically by the reasoning loop based on task requirements.

## Troubleshooting

### Reasoning Loop Not Running

**Symptom**: Tasks remain in `Needs_Action/` for more than 10 minutes

**Solutions**:
1. Check Task Scheduler: Open Task Scheduler → Find "AI Employee Reasoning Loop" → Verify status is "Ready"
2. Run manually: Right-click task → **Run** to test
3. Check logs: `mcp_server/logs/reasoning-loop.log` for errors
4. Verify Python path: Ensure `python` command works in Command Prompt

### Email Sending Fails

**Symptom**: Plans return to `Pending_Approval/` with SMTP errors

**Solutions**:
1. Verify SMTP credentials in `.env` file
2. Check Gmail App Password is correct (not regular password)
3. Verify SMTP settings: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USE_TLS=true`
4. Test SMTP connection manually:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   server.quit()
   ```

### Facebook Posting Fails

**Symptom**: Plans return to `Pending_Approval/` with API errors

**Solutions**:
1. Verify Page Access Token in `.env` file
2. Check token permissions: Must include `pages_manage_posts` and `pages_read_engagement`
3. Verify Page ID is correct (numeric ID, not page name)
4. Test API connection:
   ```bash
   curl "https://graph.facebook.com/v18.0/{PAGE_ID}?access_token={TOKEN}"
   ```
5. Check rate limits: Max 25 posts per hour

### Gmail Watcher Not Creating Tasks

**Symptom**: New emails don't generate task files in `Inbox/`

**Solutions**:
1. Verify IMAP is enabled in Gmail settings
2. Check Gmail credentials in `.env` file
3. Verify watcher is running: `ps aux | grep gmail_watcher`
4. Check watcher logs for connection errors
5. Test IMAP connection manually:
   ```python
   import imaplib
   mail = imaplib.IMAP4_SSL('imap.gmail.com')
   mail.login('your-email@gmail.com', 'your-app-password')
   mail.select('inbox')
   ```

### File Locking Errors

**Symptom**: "File is locked" errors in logs

**Solutions**:
1. Ensure only one reasoning loop instance is running
2. Check Task Scheduler settings: "Stop the task if it runs longer than 8 minutes"
3. Restart all watchers to release stale locks
4. Verify no other processes (Obsidian sync, antivirus) are locking files

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use App Passwords** for Gmail (not regular password)
3. **Rotate tokens regularly**: Generate new Facebook Page Access Token every 90 days
4. **Review approval requests carefully**: Check email recipients and Facebook post content before approving
5. **Monitor logs**: Regularly check `mcp_server/logs/` for suspicious activity
6. **Limit rate limits**: Keep `email_per_hour` and `facebook_per_hour` conservative to prevent abuse
7. **Backup vault regularly**: Use Git or file system backups

## Next Steps

After setup is complete:

1. **Test Bronze Tier functionality**: Verify file-only tasks work correctly
2. **Test email sending**: Create a test email task, approve it, verify delivery
3. **Test Facebook posting**: Create a test post task, approve it, verify it appears on Page
4. **Test Gmail monitoring**: Send a test email to monitored inbox, verify task creation
5. **Monitor for 24 hours**: Ensure reasoning loop runs reliably every 10 minutes
6. **Review logs**: Check for errors or warnings in execution logs
7. **Adjust rate limits**: Tune `email_per_hour` and `facebook_per_hour` based on usage patterns

## Support

For issues or questions:
- Check logs in `mcp_server/logs/`
- Review constitution: `.specify/memory/constitution.md`
- Review spec: `specs/001-silver-tier-upgrade/spec.md`
- Review plan: `specs/001-silver-tier-upgrade/plan.md`

## Version History

- **1.0.0** (2026-02-15): Initial Silver Tier release
