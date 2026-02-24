"""
Centralized folder path constants for Silver Tier AI Employee.

All folder paths are absolute and rooted at the vault directory.
"""
import os
from pathlib import Path

# Vault root directory
VAULT_ROOT = Path(r"E:\AI_Employee_Vault")

# Bronze Tier folders (existing)
INBOX = VAULT_ROOT / "Inbox"
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
PLANS = VAULT_ROOT / "Plans"
DONE = VAULT_ROOT / "Done"

# Silver Tier folders (new)
PENDING_APPROVAL = VAULT_ROOT / "Pending_Approval"
APPROVED = VAULT_ROOT / "Approved"
REJECTED = VAULT_ROOT / "Rejected"
SKILLS = VAULT_ROOT / "Skills"
MCP_SERVER = VAULT_ROOT / "mcp_server"
MCP_SERVER_LOGS = MCP_SERVER / "logs"

# Watchers and reasoning loop
WATCHERS = VAULT_ROOT / "watchers"
REASONING_LOOP = VAULT_ROOT / "reasoning_loop"
SHARED = VAULT_ROOT / "shared"

# Test directories
TESTS = VAULT_ROOT / "tests"
TESTS_UNIT = TESTS / "unit"
TESTS_INTEGRATION = TESTS / "integration"
TESTS_CONTRACT = TESTS / "contract"

# Ensure all directories exist
def ensure_directories():
    """Create all required directories if they don't exist."""
    directories = [
        INBOX, NEEDS_ACTION, PLANS, DONE,
        PENDING_APPROVAL, APPROVED, REJECTED,
        SKILLS, MCP_SERVER, MCP_SERVER_LOGS,
        WATCHERS, REASONING_LOOP, SHARED,
        TESTS_UNIT, TESTS_INTEGRATION, TESTS_CONTRACT
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    ensure_directories()
    print("All directories created successfully")
