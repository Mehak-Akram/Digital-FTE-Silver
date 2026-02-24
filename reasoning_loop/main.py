"""
Main Reasoning Loop for Silver Tier AI Employee.

Entry point for scheduled execution. Scans Needs_Action folder, generates plans,
routes them, and logs all activities.
"""
from pathlib import Path
from datetime import datetime
from typing import List
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from shared.folder_paths import NEEDS_ACTION, INBOX, DONE, APPROVED
from shared.file_utils import read_task_file, update_task_metadata
from reasoning_loop.skill_loader import SkillLoader
from reasoning_loop.plan_generator import PlanGenerator
from reasoning_loop.plan_router import PlanRouter
from reasoning_loop.plan_executor import PlanExecutor

logger = get_logger(__name__, "reasoning-loop.log")


class ReasoningLoop:
    """
    Main reasoning loop for Silver Tier AI Employee.

    Processes tasks from Needs_Action folder and generates execution plans.
    """

    def __init__(self):
        """Initialize reasoning loop components."""
        self.skill_loader = SkillLoader()
        self.plan_generator = PlanGenerator()
        self.plan_router = PlanRouter()
        self.plan_executor = PlanExecutor()

        logger.info("Reasoning loop initialized")

    def run(self):
        """
        Execute one iteration of the reasoning loop.

        Scans Needs_Action folder, processes tasks, generates and routes plans.
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info(f"Reasoning loop started at {start_time.isoformat()}")
        logger.info("=" * 60)

        try:
            # Scan for tasks
            tasks = self.scan_tasks()
            logger.info(f"Found {len(tasks)} tasks in Needs_Action folder")

            # Process tasks
            processed_count = 0
            error_count = 0

            if tasks:
                for task_file in tasks:
                    try:
                        self.process_task(task_file)
                        processed_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing task {task_file.name}: {e}", exc_info=True)
                        self.handle_task_error(task_file, str(e))
            else:
                logger.info("No tasks to process")

            # Execute approved plans
            logger.info("Checking for approved plans to execute...")
            executed_count, exec_error_count = self.plan_executor.execute_approved_plans()

            if executed_count > 0 or exec_error_count > 0:
                logger.info(f"Plans executed: {executed_count}, Execution errors: {exec_error_count}")

            # Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"Reasoning loop completed at {end_time.isoformat()}")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Tasks processed: {processed_count}")
            logger.info(f"Task errors: {error_count}")
            logger.info(f"Plans executed: {executed_count}")
            logger.info(f"Execution errors: {exec_error_count}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Critical error in reasoning loop: {e}", exc_info=True)
            raise

    def scan_tasks(self) -> List[Path]:
        """
        Scan Needs_Action folder for task files.

        Returns:
            List of task file paths
        """
        if not NEEDS_ACTION.exists():
            logger.warning(f"Needs_Action folder not found: {NEEDS_ACTION}")
            return []

        # Get all .md files
        task_files = list(NEEDS_ACTION.glob("*.md"))

        # Sort by filename (timestamp-based IDs)
        task_files.sort()

        return task_files

    def process_task(self, task_file: Path):
        """
        Process a single task: generate plan and route it.

        Args:
            task_file: Path to task file in Needs_Action folder

        Raises:
            Exception: If processing fails
        """
        logger.info(f"Processing task: {task_file.name}")

        # Read task to validate it
        try:
            task_data = read_task_file(task_file)
            task_id = task_data['metadata'].get('id', 'unknown')
            task_title = task_data['metadata'].get('title', 'Untitled')
        except Exception as e:
            logger.error(f"Failed to read task file {task_file.name}: {e}")
            raise ValueError(f"Invalid task file format: {e}")

        # Generate plan
        try:
            plan_data = self.plan_generator.generate_plan(task_file)
            logger.info(
                f"Plan generated for task {task_id}: "
                f"requires_approval={plan_data['requires_approval']}"
            )
        except Exception as e:
            logger.error(f"Failed to generate plan for {task_id}: {e}")
            raise

        # Validate plan routing
        if not self.plan_router.validate_routing(plan_data):
            logger.warning(f"Plan routing validation failed for {task_id}")
            # Continue anyway, but log the warning

        # Route plan
        try:
            plan_filename = f"{task_id}.md"
            plan_path = self.plan_router.route_plan(plan_data, plan_filename)
            logger.info(f"Plan routed to: {plan_path.parent.name}/{plan_filename}")
        except Exception as e:
            logger.error(f"Failed to route plan for {task_id}: {e}")
            raise

        # Update task status
        try:
            update_task_metadata(task_file, {
                'status': 'planned',
                'updated_at': datetime.now().isoformat(),
                'plan_id': task_id
            })
            logger.info(f"Task {task_id} status updated to 'planned'")
        except Exception as e:
            logger.error(f"Failed to update task status for {task_id}: {e}")
            # Non-critical error, continue

        logger.info(f"Task {task_id} processed successfully")

    def handle_task_error(self, task_file: Path, error_message: str):
        """
        Handle task processing errors.

        Moves task back to Inbox with error details.

        Args:
            task_file: Path to task file that failed
            error_message: Error description
        """
        try:
            logger.info(f"Handling error for task: {task_file.name}")

            # Read task to get metadata
            try:
                task_data = read_task_file(task_file)
                task_id = task_data['metadata'].get('id', 'unknown')
            except:
                task_id = task_file.stem

            # Update task with error information
            error_updates = {
                'status': 'failed',
                'updated_at': datetime.now().isoformat(),
                'error_message': error_message,
                'retry_count': task_data['metadata'].get('retry_count', 0) + 1
            }

            update_task_metadata(task_file, error_updates)

            # Move task back to Inbox for human review
            inbox_path = INBOX / task_file.name
            task_file.rename(inbox_path)

            logger.info(f"Task {task_id} moved to Inbox with error details")

        except Exception as e:
            logger.error(f"Failed to handle error for {task_file.name}: {e}", exc_info=True)


def main():
    """Main entry point for reasoning loop."""
    try:
        loop = ReasoningLoop()
        loop.run()
    except Exception as e:
        logger.error(f"Reasoning loop failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
