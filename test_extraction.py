"""Test parameter extraction from plan files."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from reasoning_loop.plan_executor import PlanExecutor

# Read the actual plan file
plan_path = Path("Pending_Approval/task-001.md")
with open(plan_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("Plan content length:", len(content))
print("\n" + "="*80)
print("PLAN CONTENT:")
print("="*80)
print(content)
print("\n" + "="*80)

# Test extraction
executor = PlanExecutor()
email_params = executor._extract_email_preview(content)

print("\nEXTRACTED EMAIL PARAMETERS:")
print("="*80)
if email_params:
    print(f"To: {email_params.get('to')}")
    print(f"Subject: {email_params.get('subject')}")
    print(f"Body (first 200 chars): {email_params.get('body')[:200]}")
else:
    print("FAILED TO EXTRACT")
