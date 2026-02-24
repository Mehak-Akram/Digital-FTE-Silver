"""
Plan Router for Silver Tier AI Employee.

Routes plans to appropriate folders based on requires_approval flag.
"""
from pathlib import Path
from typing import Dict, Any
import shutil
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from shared.folder_paths import PLANS, PENDING_APPROVAL
from shared.file_utils import write_plan_file

logger = get_logger(__name__)


class PlanRouter:
    """
    Routes execution plans to appropriate folders.

    Plans with external actions go to Pending_Approval.
    Plans with only file operations go to Plans.
    """

    def __init__(self):
        """Initialize plan router."""
        # Ensure destination folders exist
        PLANS.mkdir(parents=True, exist_ok=True)
        PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)

    def route_plan(
        self,
        plan_data: Dict[str, Any],
        plan_filename: str
    ) -> Path:
        """
        Route a plan to the appropriate folder.

        Args:
            plan_data: Plan data with 'metadata', 'content', 'requires_approval'
            plan_filename: Filename for the plan (e.g., "20260215-143000-task.md")

        Returns:
            Path to the created plan file

        Raises:
            ValueError: If plan data is invalid
        """
        # Validate plan data
        if 'metadata' not in plan_data or 'content' not in plan_data:
            raise ValueError("Plan data must contain 'metadata' and 'content' keys")

        requires_approval = plan_data.get('requires_approval', False)
        metadata = plan_data['metadata']
        content = plan_data['content']

        # Determine destination folder
        if requires_approval:
            destination_folder = PENDING_APPROVAL
            logger.info(f"Routing plan to Pending_Approval (requires human approval)")
        else:
            destination_folder = PLANS
            logger.info(f"Routing plan to Plans (file-only actions)")

        # Create plan file
        plan_path = destination_folder / plan_filename

        # Write plan file
        write_plan_file(plan_path, metadata, content)

        logger.info(
            f"Plan routed successfully: {plan_filename} -> {destination_folder.name}/"
        )

        return plan_path

    def validate_routing(self, plan_data: Dict[str, Any]) -> bool:
        """
        Validate that plan routing is correct.

        Args:
            plan_data: Plan data to validate

        Returns:
            True if routing is valid, False otherwise
        """
        requires_approval = plan_data.get('requires_approval', False)
        metadata = plan_data.get('metadata', {})

        # Check if requires_approval matches action types
        # This is a safety check to ensure plan generator set the flag correctly
        if requires_approval:
            # Plan should have risks and rollback procedure
            content = plan_data.get('content', '')
            if '## Risks' not in content:
                logger.warning("Plan requires approval but missing Risks section")
                return False
            if '## Rollback Procedure' not in content:
                logger.warning("Plan requires approval but missing Rollback Procedure")
                return False
            if '## Action Preview' not in content:
                logger.warning("Plan requires approval but missing Action Preview")
                return False

        return True


if __name__ == "__main__":
    # Test plan router
    from datetime import datetime

    router = PlanRouter()

    # Test file-only plan
    file_plan = {
        'metadata': {
            'id': 'test-001',
            'task_id': 'test-001',
            'objective': 'Test file operation',
            'requires_approval': False,
            'created_at': datetime.now().isoformat(),
            'execution_status': 'pending'
        },
        'content': '# Test Plan\n\n## Steps\n\n1. Read file\n\n## Risks\n\n- None\n\n## Rollback Procedure\n\nNo rollback needed.',
        'requires_approval': False
    }

    # Test approval-required plan
    approval_plan = {
        'metadata': {
            'id': 'test-002',
            'task_id': 'test-002',
            'objective': 'Test email sending',
            'requires_approval': True,
            'created_at': datetime.now().isoformat(),
            'execution_status': 'pending'
        },
        'content': '# Test Plan\n\n## Steps\n\n1. Send email\n\n## Risks\n\n- Email failure\n\n## Rollback Procedure\n\nRetry\n\n## Action Preview\n\nEmail to: test@example.com',
        'requires_approval': True
    }

    # Validate and route
    print(f"File plan valid: {router.validate_routing(file_plan)}")
    print(f"Approval plan valid: {router.validate_routing(approval_plan)}")

    file_path = router.route_plan(file_plan, "test-001.md")
    print(f"File plan routed to: {file_path}")

    approval_path = router.route_plan(approval_plan, "test-002.md")
    print(f"Approval plan routed to: {approval_path}")

    # Cleanup
    file_path.unlink()
    approval_path.unlink()
    print("Test completed successfully")
