# Silver Tier AI Employee - Quick Start Guide

## Prerequisites

- Python 3.12+
- Gmail account with App Password
- Facebook Page with access token
- Git (optional)

## Installation

1. **Clone/Navigate to project:**
```bash
cd E:\AI_Employee_Vault
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
Edit `.env` file with your credentials:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_PAGE_ACCESS_TOKEN=your-token
```

## Running the System

### Single Execution
```bash
python reasoning_loop/main.py
```

### Continuous Mode (with watcher)
```bash
python run_reasoning_loop.bat
```

## Testing the System

### Test 1: Send Email

1. **Create task file:** `Needs_Action/test-email.md`
```markdown
---
id: test-email
title: Test Email
priority: P1
source: manual
status: needs_action
tags: [email]
---

# Task: Test Email

Send a test email.

**Email Details:**
- To: mehakakram089@gmail.com
- Subject: Test from AI Employee
- Body:

This is a test email from the Silver Tier AI Employee system.
```

2. **Run reasoning loop:**
```bash
python reasoning_loop/main.py
```

3. **Approve the plan:**
```bash
mv Pending_Approval/test-email.md Approved/
```

4. **Add approval timestamp:**
Edit `Approved/test-email.md` and add to frontmatter:
```yaml
approved_at: '2026-02-24T22:00:00Z'
```

5. **Execute:**
```bash
python reasoning_loop/main.py
```

6. **Verify:**
- Check `Done/` folder for completed plan
- Check your email inbox

### Test 2: Post to Facebook

1. **Create task file:** `Needs_Action/test-facebook.md`
```markdown
---
id: test-facebook
title: Test Facebook Post
priority: P2
source: manual
status: needs_action
tags: [facebook]
---

# Task: Test Facebook Post

Post a test message to Facebook.

**Post Details:**
- Message: Testing the Silver Tier AI Employee system! 🚀
- Link: https://example.com
- Published: true
```

2. **Follow same approval workflow as email test**

3. **Verify:**
- Check `Done/` folder
- Check your Facebook page

## Folder Structure

```
Needs_Action/     # New tasks go here
Pending_Approval/ # Plans awaiting human approval
Approved/         # Approved plans ready for execution
Done/             # Completed plans
Plans/            # File-only operations (auto-execute)
```

## Workflow

1. **Create Task** → Place in `Needs_Action/`
2. **Generate Plan** → Reasoning loop creates plan
3. **Route Plan** → External actions → `Pending_Approval/`
4. **Human Review** → Review plan details
5. **Approve** → Move to `Approved/` + add timestamp
6. **Execute** → Reasoning loop executes
7. **Complete** → Plan moves to `Done/`

## Troubleshooting

### Email not sending
- Check Gmail App Password
- Verify SMTP settings in `.env`
- Check logs in `logs/` folder

### Facebook not posting
- Verify Page Access Token is valid
- Check Page ID matches your page
- Ensure token has `pages_manage_posts` permission

### Plan not executing
- Verify `approved_at` timestamp exists in frontmatter
- Check plan is in `Approved/` folder
- Review logs for errors

## Rate Limits

- **Email:** 10 per hour
- **Facebook:** 5 per hour

Limits reset every hour.

## Logs

All logs stored in `logs/` folder:
- `reasoning-loop.log` - Main loop activity
- `mcp-server.log` - MCP server activity

## Support

For issues or questions:
1. Check logs in `logs/` folder
2. Review `SILVER_TIER_COMPLETION_REPORT.md`
3. Check task file format matches examples

---

**Ready to test!** 🚀
