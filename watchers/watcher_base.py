"""
Base watcher class for file system monitoring.

Provides common functionality for all watchers with debounce logic and error handling.
"""
import time
from pathlib import Path
from typing import Callable, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger


class WatcherBase(FileSystemEventHandler):
    """
    Base class for file system watchers.

    Provides debounce logic, error handling, and common watcher functionality.
    """

    def __init__(
        self,
        watcher_name: str,
        monitored_folder: Path,
        file_pattern: str = "*.md",
        debounce_seconds: int = 1,
        event_types: List[str] = None
    ):
        """
        Initialize base watcher.

        Args:
            watcher_name: Unique watcher identifier
            monitored_folder: Path to folder to monitor
            file_pattern: File extension filter (default: *.md)
            debounce_seconds: Wait time after last change (default: 1)
            event_types: Events to monitor (default: ['created', 'modified'])
        """
        super().__init__()
        self.watcher_name = watcher_name
        self.monitored_folder = Path(monitored_folder)
        self.file_pattern = file_pattern
        self.debounce_seconds = debounce_seconds
        self.event_types = event_types or ['created', 'modified']

        # State tracking
        self.last_processed: dict = {}  # file_path -> timestamp
        self.error_count = 0
        self.max_errors = 5
        self.status = "running"

        # Logger
        self.logger = get_logger(f"watcher.{watcher_name}")

        # Ensure monitored folder exists
        self.monitored_folder.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Watcher initialized: {watcher_name} monitoring {monitored_folder}")

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if 'created' in self.event_types:
            self._handle_event(event, 'created')

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if 'modified' in self.event_types:
            self._handle_event(event, 'modified')

    def on_moved(self, event: FileSystemEvent):
        """Handle file move events."""
        if 'moved' in self.event_types:
            self._handle_event(event, 'moved')

    def _handle_event(self, event: FileSystemEvent, event_type: str):
        """
        Internal event handler with debounce and filtering.

        Args:
            event: File system event
            event_type: Type of event (created, modified, moved)
        """
        # Ignore directories
        if event.is_directory:
            return

        # Filter by file pattern
        file_path = Path(event.src_path)
        if not file_path.match(self.file_pattern):
            return

        # Debounce: Check if we recently processed this file
        now = time.time()
        last_time = self.last_processed.get(str(file_path), 0)
        if now - last_time < self.debounce_seconds:
            return

        # Update last processed time
        self.last_processed[str(file_path)] = now

        # Log event
        self.logger.debug(f"Event detected: {event_type} - {file_path.name}")

        # Call subclass handler
        try:
            self.process_file(file_path, event_type)
            self.error_count = 0  # Reset error count on success
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error processing {file_path.name}: {e}", exc_info=True)

            # Circuit breaker: Stop watcher after too many errors
            if self.error_count >= self.max_errors:
                self.status = "circuit_open"
                self.logger.error(f"Circuit breaker opened after {self.max_errors} errors")

    def process_file(self, file_path: Path, event_type: str):
        """
        Process a file event. Must be implemented by subclasses.

        Args:
            file_path: Path to the file that triggered the event
            event_type: Type of event (created, modified, moved)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement process_file()")

    def start(self):
        """Start the watcher."""
        if self.status == "circuit_open":
            self.logger.warning("Cannot start watcher: circuit breaker is open")
            return

        self.observer = Observer()
        self.observer.schedule(self, str(self.monitored_folder), recursive=False)
        self.observer.start()
        self.status = "running"
        self.logger.info(f"Watcher started: {self.watcher_name}")

    def stop(self):
        """Stop the watcher."""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        self.status = "stopped"
        self.logger.info(f"Watcher stopped: {self.watcher_name}")

    def reset_circuit_breaker(self):
        """Reset circuit breaker and error count."""
        self.error_count = 0
        self.status = "running"
        self.logger.info(f"Circuit breaker reset for {self.watcher_name}")


if __name__ == "__main__":
    # Test base watcher
    class TestWatcher(WatcherBase):
        def process_file(self, file_path: Path, event_type: str):
            print(f"Processing: {file_path.name} ({event_type})")

    test_folder = Path("E:/AI_Employee_Vault/Inbox")
    watcher = TestWatcher("test_watcher", test_folder)

    print(f"Starting test watcher on {test_folder}")
    print("Create or modify a .md file in the folder to test...")
    print("Press Ctrl+C to stop")

    try:
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("Watcher stopped")
