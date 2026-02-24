"""
Plan Generator for Silver Tier AI Employee.

Generates structured execution plans from tasks with action type detection.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
import re
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from shared.file_utils import read_task_file

logger = get_logger(__name__)


class PlanGenerator:
    """
    Generates execution plans from task descriptions.

    Analyzes task content and creates structured plans with action type detection.
    """

    def __init__(self):
        """Initialize plan generator."""
        # Action type detection patterns
        self.action_patterns = {
            'send_email': [
                r'send\s+(?:an?\s+)?email',
                r'email\s+(?:to|someone)',
                r'notify\s+(?:via\s+)?email',
                r'send\s+(?:a\s+)?message\s+to\s+\S+@\S+',
            ],
            'post_facebook': [
                r'post\s+(?:to|on)\s+facebook',
                r'facebook\s+post',
                r'publish\s+(?:to|on)\s+(?:the\s+)?(?:facebook\s+)?page',
                r'social\s+media\s+post',
            ],
            'file_read': [
                r'read\s+(?:the\s+)?file',
                r'check\s+(?:the\s+)?(?:contents?\s+of)',
                r'review\s+(?:the\s+)?file',
                r'scan\s+(?:the\s+)?folder',
            ],
            'file_write': [
                r'write\s+(?:to\s+)?(?:a\s+)?file',
                r'create\s+(?:a\s+)?file',
                r'save\s+(?:to\s+)?file',
                r'update\s+(?:the\s+)?file',
            ],
            'file_move': [
                r'move\s+(?:the\s+)?file',
                r'relocate\s+(?:the\s+)?file',
                r'transfer\s+(?:the\s+)?file',
                r'organize\s+files',
            ],
            'file_delete': [
                r'delete\s+(?:the\s+)?file',
                r'remove\s+(?:the\s+)?file',
                r'clean\s+up\s+files',
            ]
        }

    def generate_plan(self, task_file_path: Path) -> Dict[str, Any]:
        """
        Generate an execution plan from a task file.

        Args:
            task_file_path: Path to the task file

        Returns:
            Dictionary with 'metadata', 'content', and 'requires_approval' keys

        Raises:
            FileNotFoundError: If task file doesn't exist
            ValueError: If task format is invalid
        """
        logger.info(f"Generating plan for task: {task_file_path.name}")

        # Read task file
        task_data = read_task_file(task_file_path)
        task_metadata = task_data['metadata']
        task_content = task_data['content']

        # Extract task information
        task_id = task_metadata.get('id', 'unknown')
        task_title = task_metadata.get('title', 'Untitled Task')

        # Detect action types
        detected_actions = self.detect_action_types(task_content)
        logger.debug(f"Detected actions for {task_id}: {detected_actions}")

        # Determine if approval is required
        requires_approval = self._requires_approval(detected_actions)

        # Generate plan steps
        steps = self._generate_steps(task_content, detected_actions)

        # Generate risks
        risks = self._generate_risks(detected_actions, task_content)

        # Generate rollback procedure
        rollback = self._generate_rollback(detected_actions, requires_approval)

        # Generate action preview if approval required
        action_preview = ""
        if requires_approval:
            action_preview = self._generate_action_preview(task_content, detected_actions)

        # Create plan metadata
        plan_metadata = {
            'id': task_id,
            'task_id': task_id,
            'objective': self._extract_objective(task_title, task_content),
            'requires_approval': requires_approval,
            'created_at': datetime.now().isoformat(),
            'execution_status': 'pending'
        }

        # Create plan content
        plan_content = self._format_plan_content(
            task_title,
            steps,
            risks,
            rollback,
            action_preview
        )

        logger.info(
            f"Plan generated for {task_id}: "
            f"requires_approval={requires_approval}, "
            f"actions={detected_actions}"
        )

        return {
            'metadata': plan_metadata,
            'content': plan_content,
            'requires_approval': requires_approval
        }

    def detect_action_types(self, content: str) -> List[str]:
        """
        Detect action types from task content.

        Args:
            content: Task content text

        Returns:
            List of detected action types
        """
        detected = []
        content_lower = content.lower()

        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    if action_type not in detected:
                        detected.append(action_type)
                    break

        # Default to file_read if no actions detected
        if not detected:
            detected.append('file_read')

        return detected

    def _requires_approval(self, action_types: List[str]) -> bool:
        """
        Determine if plan requires human approval.

        Args:
            action_types: List of detected action types

        Returns:
            True if approval required, False otherwise
        """
        external_actions = {'send_email', 'post_facebook'}
        return any(action in external_actions for action in action_types)

    def _generate_steps(self, content: str, action_types: List[str]) -> List[Dict[str, str]]:
        """
        Generate execution steps based on detected actions.

        Args:
            content: Task content
            action_types: Detected action types

        Returns:
            List of step dictionaries
        """
        steps = []

        # Extract email details if present
        email_match = re.search(r'(?:to|recipients?):\s*(\S+@\S+)', content, re.IGNORECASE)
        subject_match = re.search(r'subject:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)

        for action_type in action_types:
            if action_type == 'send_email':
                # Updated regex to handle multiple markdown formats
                email_match = re.search(r'\*?\*?(?:to|recipients?)\*?\*?:\s*\*?\*?\s*(\S+@\S+)', content, re.IGNORECASE)
                subject_match = re.search(r'subject:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
                recipient = email_match.group(1) if email_match else 'recipient@example.com'
                subject = subject_match.group(1).strip() if subject_match else 'Email Subject'
                steps.append({
                    'action': f'Send email via MCP',
                    'action_type': 'send_email',
                    'parameters': f'to="{recipient}", subject="{subject}", body=<content>',
                    'expected_outcome': 'Email delivered successfully'
                })
            elif action_type == 'post_facebook':
                steps.append({
                    'action': 'Post to Facebook Page via MCP',
                    'action_type': 'post_facebook',
                    'parameters': 'message=<content>',
                    'expected_outcome': 'Post published successfully'
                })
            elif action_type == 'file_read':
                steps.append({
                    'action': 'Read required files',
                    'action_type': 'file_read',
                    'parameters': 'folder=<target_folder>',
                    'expected_outcome': 'File contents retrieved'
                })
            elif action_type == 'file_write':
                steps.append({
                    'action': 'Write to file',
                    'action_type': 'file_write',
                    'parameters': 'file_path=<target_file>, content=<data>',
                    'expected_outcome': 'File created/updated successfully'
                })
            elif action_type == 'file_move':
                steps.append({
                    'action': 'Move file to destination',
                    'action_type': 'file_move',
                    'parameters': 'source=<source_path>, destination=<dest_path>',
                    'expected_outcome': 'File moved successfully'
                })

        return steps

    def _generate_risks(self, action_types: List[str], content: str) -> List[str]:
        """Generate risk list based on action types."""
        risks = []

        if 'send_email' in action_types:
            risks.append('Email delivery failure due to SMTP server issues')
            risks.append('Recipient email address may be invalid')

        if 'post_facebook' in action_types:
            risks.append('Facebook API rate limit may be exceeded')
            risks.append('Access token may be invalid or expired')

        if 'file_write' in action_types or 'file_move' in action_types:
            risks.append('File system permissions may prevent operation')

        # Always include a generic risk
        if not risks:
            risks.append('Task requirements may be incomplete or ambiguous')

        return risks

    def _generate_rollback(self, action_types: List[str], requires_approval: bool) -> str:
        """Generate rollback procedure."""
        if not requires_approval:
            return "If execution fails, log error and move task back to Needs_Action."

        rollback_steps = []

        if 'send_email' in action_types or 'post_facebook' in action_types:
            rollback_steps.append("1. Log error details in plan frontmatter")
            rollback_steps.append("2. Move plan back to Pending_Approval with error message")
            rollback_steps.append("3. Notify human via pending_approval_watcher")
            rollback_steps.append("4. Human can modify parameters or retry")

        return "\n".join(rollback_steps) if rollback_steps else "No rollback needed for file-only operations."

    def _generate_action_preview(self, content: str, action_types: List[str]) -> str:
        """Generate action preview for approval."""
        preview_parts = []

        if 'send_email' in action_types:
            # Updated regex to handle multiple markdown formats:
            # - To: email@example.com
            # **To:** email@example.com
            # **Recipients**: email@example.com
            email_match = re.search(r'\*?\*?(?:to|recipients?)\*?\*?:\s*\*?\*?\s*(\S+@\S+)', content, re.IGNORECASE)
            subject_match = re.search(r'subject:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)

            recipient = email_match.group(1) if email_match else 'recipient@example.com'
            subject = subject_match.group(1).strip() if subject_match else 'Email Subject'
            body_preview = content[:500] if len(content) > 500 else content

            preview_parts.append(
                f"**Email Preview**:\n"
                f"- To: {recipient}\n"
                f"- Subject: {subject}\n"
                f"- Body: (first 500 chars)\n"
                f"  {body_preview}"
            )

        if 'post_facebook' in action_types:
            message_preview = content[:500] if len(content) > 500 else content
            preview_parts.append(
                f"**Facebook Post Preview**:\n"
                f"- Message: {message_preview}"
            )

        return "\n\n".join(preview_parts)

    def _extract_objective(self, title: str, content: str) -> str:
        """Extract clear objective from task."""
        # Use title as base objective
        objective = title

        # Try to extract more specific objective from content
        first_line = content.split('\n')[0].strip()
        if first_line and len(first_line) < 200:
            objective = first_line.replace('#', '').strip()

        return objective[:500]  # Limit to 500 chars

    def _format_plan_content(
        self,
        title: str,
        steps: List[Dict[str, str]],
        risks: List[str],
        rollback: str,
        action_preview: str
    ) -> str:
        """Format plan content as markdown."""
        content_parts = [
            f"# Execution Plan: {title}",
            "",
            "## Steps",
            ""
        ]

        # Add steps
        for i, step in enumerate(steps, 1):
            content_parts.append(
                f"{i}. **{step['action']}** (action_type: {step['action_type']})\n"
                f"   - Parameters: {step['parameters']}\n"
                f"   - Expected outcome: {step['expected_outcome']}"
            )

        content_parts.extend(["", "## Risks", ""])
        content_parts.extend([f"- {risk}" for risk in risks])

        content_parts.extend(["", "## Rollback Procedure", "", rollback])

        if action_preview:
            content_parts.extend(["", "## Action Preview", "", action_preview])

        return "\n".join(content_parts)


if __name__ == "__main__":
    # Test plan generator
    generator = PlanGenerator()

    # Test action detection
    test_content = "Send an email to team@example.com with the weekly report"
    actions = generator.detect_action_types(test_content)
    print(f"Detected actions: {actions}")

    test_content2 = "Post announcement to Facebook Page about new product"
    actions2 = generator.detect_action_types(test_content2)
    print(f"Detected actions: {actions2}")

    test_content3 = "Move completed tasks to archive folder"
    actions3 = generator.detect_action_types(test_content3)
    print(f"Detected actions: {actions3}")
