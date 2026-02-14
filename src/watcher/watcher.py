"""File system watcher for Bronze Tier AI Employee.

Monitors the Inbox folder and automatically moves new files to Needs_Action.
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from watcher.config import INBOX, NEEDS_ACTION, LOCK_FILE
from watcher.file_mover import safe_move
from watcher.lock_manager import acquire_lock, release_lock


class InboxHandler(FileSystemEventHandler):
    """Handler for file system events in the Inbox folder."""

    def on_created(self, event):
        """
        Handle file creation events in Inbox.

        When a new file is created in Inbox, move it to Needs_Action
        and log the action to console.

        Args:
            event: FileSystemEvent containing event details
        """
        # Ignore directory creation events
        if event.is_directory:
            return

        source = Path(event.src_path)
        timestamp = datetime.now().isoformat()

        try:
            # Move file to Needs_Action
            dest = safe_move(source, NEEDS_ACTION)
            print(f"[{timestamp}] Moved: {source.name} -> Needs_Action/")
        except Exception as e:
            print(f"[{timestamp}] ERROR: Failed to move {source.name}: {e}")


def main():
    """
    Main entry point for the watcher.

    Sets up the file system observer, acquires lock for single instance,
    and runs until interrupted by user (Ctrl+C).
    """
    # Acquire lock to ensure single instance
    if not acquire_lock(LOCK_FILE):
        print("ERROR: Watcher already running (lock file exists)")
        print(f"Lock file: {LOCK_FILE}")
        print("If the watcher is not running, delete the lock file and try again.")
        sys.exit(1)

    try:
        print(f"Starting Bronze Tier Watcher")
        print(f"Monitoring: {INBOX}")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        # Create observer and schedule handler
        event_handler = InboxHandler()
        observer = Observer()
        observer.schedule(event_handler, str(INBOX), recursive=False)
        observer.start()

        # Run until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nStopping watcher...")

        observer.join()

    finally:
        # Always release lock on exit
        release_lock(LOCK_FILE)
        print("Watcher stopped")


if __name__ == "__main__":
    main()
