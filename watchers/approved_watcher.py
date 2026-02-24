"""
Approved Watcher for Silver Tier AI Employee.

Monitors Approved folder and detects human-approved plans ready for execution.
"""
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent))

from watchers.watcher_base import WatcherBase
from shared.folder_paths import APPROVED
from shared.file_utils import read_plan_file, update_plan_metadata


class ApprovedWatcher(WatcherBase):
    """
    Monitors Approved folder for human-approved plans.

    Detects when plans are moved to Approved and marks them ready for execution.
    """

    def __init__(self):
        """Initialize approved watcher."""
        super().__init__(
            watcher_name="approved_watcher",
            monitored_folder=APPROVED,
            file_pattern="*.md",
            debounce_seconds=2,
            event_types=['created']
        )

    def process_file(self, file_path: Path, event_type: str):
        """
        Process approved plan files.

        Args:
            file_path: Path to the approved plan file
            event_type: Type of event (created)
        """
        self.logger.info(f"Approved plan detected: {file_path.name}")

        try:
            # Read plan file
            plan_data = read_plan_file(file_path)
            metadata = plan_data['metadata']

            # Extract key information
            plan_id = metadata.get('id', 'unknown')
            objective = metadata.get('objective', 'No objective specified')

            # Check if already marked as approved
            if metadata.get('approved_at'):
                self.logger.debug(f"Plan {plan_id} already has approval timestamp")
                return

            # Update plan metadata with approval timestamp
            approval_updates = {
                'approved_at': datetime.now().isoformat(),
                'approved_by': 'human',
                'execution_status': 'pending'
            }

            update_plan_metadata(file_path, approval_updates)

            self.logger.info(
                f"✅ Plan approved and ready for execution\n"
                f"Plan ID: {plan_id}\n"
                f"Objective: {objective}\n"
                f"File: {file_path.name}\n"
                f"Status: Waiting for reasoning loop to execute"
            )

        except Exception as e:
            self.logger.error(f"Error processing approved plan {file_path.name}: {e}", exc_info=True)
            raise


def main():
    """Run the approved watcher."""
    import time

    watcher = ApprovedWatcher()

    print(f"Starting Approved Watcher...")
    print(f"Monitoring: {APPROVED}")
    print("Press Ctrl+C to stop")

    try:
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\nWatcher stopped")


if __name__ == "__main__":
    main()
