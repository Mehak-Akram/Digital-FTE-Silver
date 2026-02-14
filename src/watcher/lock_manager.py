"""Single instance lock management using PID file."""
import os
from pathlib import Path


def acquire_lock(lock_file: Path) -> bool:
    """
    Acquire a lock to ensure single watcher instance.

    Uses a PID file to track the running process. If a stale lock
    exists (process no longer running), it is removed and the lock
    is acquired.

    Args:
        lock_file: Path to the lock file

    Returns:
        True if lock acquired successfully, False if another instance is running
    """
    if lock_file.exists():
        # Check if process is still running
        try:
            pid = int(lock_file.read_text().strip())
            # Signal 0 checks if process exists without sending actual signal
            os.kill(pid, 0)
            # Process exists, lock is held
            return False
        except (OSError, ValueError):
            # Stale lock (process doesn't exist or invalid PID)
            lock_file.unlink()

    # Acquire lock by writing current PID
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(str(os.getpid()))
    return True


def release_lock(lock_file: Path) -> None:
    """
    Release the lock by removing the PID file.

    Args:
        lock_file: Path to the lock file
    """
    lock_file.unlink(missing_ok=True)
