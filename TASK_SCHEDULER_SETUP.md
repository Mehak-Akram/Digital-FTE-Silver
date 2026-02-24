# Windows Task Scheduler Configuration Instructions

## Task: AI Employee Reasoning Loop

Follow these steps to configure the scheduled reasoning loop:

### 1. Open Task Scheduler
- Press `Win + R`, type `taskschd.msc`, press Enter
- Or search "Task Scheduler" in Start menu

### 2. Create New Task
- Click **Create Task** (not "Create Basic Task")

### 3. General Tab
- **Name**: `AI Employee Reasoning Loop`
- **Description**: `Runs Silver Tier reasoning loop every 10 minutes to process tasks`
- **Security options**:
  - ☑ Run whether user is logged on or not
  - ☐ Run with highest privileges (not needed)
  - Configure for: Windows 10

### 4. Triggers Tab
- Click **New**
- **Begin the task**: On a schedule
- **Settings**: Daily
- **Start**: Today at 00:00:00
- **Recur every**: 1 days
- ☑ **Repeat task every**: 10 minutes
- **For a duration of**: Indefinitely
- ☑ **Enabled**
- Click **OK**

### 5. Actions Tab
- Click **New**
- **Action**: Start a program
- **Program/script**: `E:\AI_Employee_Vault\run_reasoning_loop.bat`
- **Start in**: `E:\AI_Employee_Vault`
- Click **OK**

### 6. Conditions Tab
- ☐ Start only if computer is on AC power (optional - uncheck for laptops)
- ☐ Wake the computer to run this task

### 7. Settings Tab
- ☑ Allow task to be run on demand
- ☑ Stop the task if it runs longer than: **8 minutes**
- **If the running task does not end when requested**: Stop the existing instance
- ☐ Do not start a new instance (leave unchecked)

### 8. Save Task
- Click **OK**
- Enter your Windows password if prompted

### 9. Test the Task
- Right-click the task → **Run**
- Check logs: `E:\AI_Employee_Vault\mcp_server\logs\reasoning-loop.log`
- Verify task completes successfully

### 10. Monitor Execution
- Task Scheduler shows last run time and result
- Check "Last Run Result" column (0x0 = success)
- Review logs for any errors

## Troubleshooting

**Task doesn't run:**
- Verify Python is in system PATH
- Check batch file path is correct
- Review Task Scheduler History tab for errors

**Task runs but fails:**
- Check `reasoning-loop.log` for error details
- Verify all Python dependencies installed
- Ensure folder permissions are correct

**Task runs too long:**
- Increase timeout from 8 to 9 minutes if needed
- Check for performance issues in logs
