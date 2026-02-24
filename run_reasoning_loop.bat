@echo off
REM Reasoning Loop Batch File for Windows Task Scheduler
REM Silver Tier AI Employee

cd /d E:\AI_Employee_Vault

REM Run the reasoning loop
python reasoning_loop\main.py

REM Exit with the Python script's exit code
exit /b %ERRORLEVEL%
