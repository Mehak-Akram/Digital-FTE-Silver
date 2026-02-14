"""Configuration constants for Bronze Tier AI Employee watcher."""
from pathlib import Path

# Vault root path
VAULT_PATH = Path("E:/AI_Employee_Vault")

# Folder paths
INBOX = VAULT_PATH / "Inbox"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PLANS = VAULT_PATH / "Plans"
DONE = VAULT_PATH / "Done"

# Watcher paths
WATCHER_DIR = VAULT_PATH / ".watcher"
LOCK_FILE = WATCHER_DIR / "watcher.lock"
LOG_FILE = WATCHER_DIR / "watcher.log"
