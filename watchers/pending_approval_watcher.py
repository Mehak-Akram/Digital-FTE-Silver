"""
Pending Approval Watcher for Silver Tier AI Employee.

Monitors Pending_Approval folder and notifies human when new plans require review.
"""
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from watchers.watcher_base import WatcherBase
from shared.folder_paths import PENDING_APPROVAL
from shared.file_utils import read_plan_file


class PendingApprovalWatcher(WatcherBase):
    """
    Monitors Pending_Approval folder for new approval requests.

    Notifies human when plans requiring approval are created.
    """

    def __init__(self):
        """Initialize pending approval watcher."""
        super().__init__(
            watcher_name="pending_approval_watcher",
            monitored_folder=PENDING_APPROVAL,
            file_pattern="*.md",
            debounce_seconds=2,
            event_types=['created']
        )

    def process_file(self, file_path: Path, event_type: str):
        """
        Process new plan files in Pending_Approval folder.

        Args:
            file_path: Path to the plan file
            event_type: Type of event (created)
        """
        self.logger.info(f"New approval request detected: {file_path.name}")

        try:
            # Read plan file
            plan_data = read_plan_file(file_path)
            metadata = plan_data['metadata']

            # Extract key information
            plan_id = metadata.get('id', 'unknown')
            objective = metadata.get('objective', 'No objective specified')
            requires_approval = metadata.get('requires_approval', False)

            # Validate this is actually an approval request
            if not requires_approval:
                self.logger.warning(
                    f"Plan {plan_id} in Pending_Approval but requires_approval=false. "
                    "This may be a routing error."
                )

            # Notify human (log notification)
            self.logger.info(
                f"⚠️  APPROVAL REQUIRED ⚠️\n"
                f"Plan ID: {plan_id}\n"
                f"Objective: {objective}\n"
                f"File: {file_path.name}\n"
                f"Action: Review plan and move to Approved/ or Rejected/ folder"
            )

            # In a full implementation, this could:
            # - Send desktop notification
            # - Send email alert
            # - Update a dashboard
            # For Silver Tier, logging is sufficient

        except Exception as e:
            self.logger.error(f"Error processing approval request {file_path.name}: {e}", exc_info=True)
            raise


def main():
    """Run the pending approval watcher."""
    import time

    watcher = PendingApprovalWatcher()

    print(f"Starting Pending Approval Watcher...")
    print(f"Monitoring: {PENDING_APPROVAL}")
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
