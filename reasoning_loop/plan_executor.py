"""
Plan Executor for Silver Tier AI Employee.

Executes approved plans by calling MCP server functions.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from shared.folder_paths import APPROVED, DONE, PENDING_APPROVAL
from shared.file_utils import read_plan_file, update_plan_metadata
from shared.mcp_client import MCPClient
import shutil

logger = get_logger(__name__)


class PlanExecutor:
    """
    Executes approved plans with external actions.

    Note: For Silver Tier MVP, this is a simplified executor that logs
    execution attempts. Full MCP integration requires the MCP server to be running.
    """

    def __init__(self):
        """Initialize plan executor."""
        self.mcp_client = MCPClient()
        logger.info("Plan executor initialized with MCP client")

    def execute_approved_plans(self):
        """
        Scan Approved folder and execute all approved plans.

        Returns:
            Tuple of (executed_count, error_count)
        """
        if not APPROVED.exists():
            logger.warning(f"Approved folder not found: {APPROVED}")
            return 0, 0

        # Get all approved plans
        approved_plans = list(APPROVED.glob("*.md"))

        if not approved_plans:
            logger.debug("No approved plans to execute")
            return 0, 0

        logger.info(f"Found {len(approved_plans)} approved plans to execute")

        executed_count = 0
        error_count = 0

        for plan_file in approved_plans:
            try:
                self.execute_plan(plan_file)
                executed_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Error executing plan {plan_file.name}: {e}", exc_info=True)
                self.handle_execution_error(plan_file, str(e))

        return executed_count, error_count

    def execute_plan(self, plan_file: Path):
        """
        Execute a single approved plan.

        Args:
            plan_file: Path to approved plan file

        Raises:
            Exception: If execution fails
        """
        logger.info(f"Executing plan: {plan_file.name}")

        # Read plan
        plan_data = read_plan_file(plan_file)
        metadata = plan_data['metadata']
        content = plan_data['content']

        plan_id = metadata.get('id', 'unknown')

        # Verify plan is approved
        if not metadata.get('approved_at'):
            raise ValueError(f"Plan {plan_id} not approved (missing approved_at timestamp)")

        # Update execution status
        update_plan_metadata(plan_file, {
            'execution_status': 'in_progress',
            'executed_at': datetime.now().isoformat()
        })

        # Extract action steps
        steps = self._extract_steps(content)

        # Execute each step
        execution_results = []
        task_id = metadata.get('task_id')
        for step in steps:
            action_type = step.get('action_type')

            if action_type == 'send_email':
                result = self._execute_email_action(step, content, task_id)
                execution_results.append(result)
            elif action_type == 'post_facebook':
                result = self._execute_facebook_action(step, content, task_id)
                execution_results.append(result)
            else:
                # File operations - log only for now
                logger.info(f"File operation: {action_type} - {step.get('action')}")
                execution_results.append({
                    'action_type': action_type,
                    'success': True,
                    'message': 'File operation logged (not executed in MVP)'
                })

        # Check if all steps succeeded
        all_success = all(r.get('success', False) for r in execution_results)

        if all_success:
            # Move to Done
            self._complete_plan(plan_file, execution_results)
        else:
            # Move back to Pending_Approval with errors
            self._fail_plan(plan_file, execution_results)

    def _extract_steps(self, content: str) -> list:
        """
        Extract execution steps from plan content.

        Args:
            content: Plan markdown content

        Returns:
            List of step dictionaries
        """
        steps = []

        # Find Steps section
        steps_match = re.search(r'## Steps\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not steps_match:
            return steps

        steps_text = steps_match.group(1)

        # Parse each step
        step_pattern = r'\d+\.\s+\*\*(.+?)\*\*\s+\(action_type:\s+(\w+)\)'
        for match in re.finditer(step_pattern, steps_text):
            action = match.group(1)
            action_type = match.group(2)

            steps.append({
                'action': action,
                'action_type': action_type
            })

        return steps

    def _execute_email_action(self, step: Dict[str, Any], content: str, task_id: str = None) -> Dict[str, Any]:
        """
        Execute email sending action.

        Args:
            step: Step dictionary
            content: Full plan content
            task_id: Original task ID to read from

        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing email action: {step.get('action')}")

        # Try to read from original task file first (more reliable)
        email_preview = None
        if task_id:
            from shared.folder_paths import NEEDS_ACTION
            task_file = NEEDS_ACTION / f"{task_id}.md"
            if task_file.exists():
                task_data = read_plan_file(task_file)
                email_preview = self._extract_email_preview(task_data['content'])
                logger.info(f"Extracted email params from original task file")

        # Fallback to plan content
        if not email_preview:
            email_preview = self._extract_email_preview(content)

        logger.debug(f"Extracted email preview: {email_preview}")

        if not email_preview:
            logger.error("Failed to extract email parameters from plan content")
            logger.debug(f"Plan content (first 500 chars): {content[:500]}")
            return {
                'action_type': 'send_email',
                'success': False,
                'error': 'EMAIL_PREVIEW_NOT_FOUND',
                'message': 'Could not extract email parameters from plan'
            }

        # Call MCP server to send email
        try:
            logger.info(f"Calling MCP send_email with: to={email_preview.get('to')}, subject={email_preview.get('subject')[:50]}...")

            result = self.mcp_client.call_tool_sync(
                "send_email",
                {
                    "to": email_preview.get('to'),
                    "subject": email_preview.get('subject'),
                    "body": email_preview.get('body'),
                    "content_type": "text/plain"
                }
            )

            logger.info(f"Email action result: {result.get('success')}, message: {result.get('message')}")

            return {
                'action_type': 'send_email',
                'success': result.get('success', False),
                'message': result.get('message', 'Email sent'),
                'message_id': result.get('message_id'),
                'timestamp': result.get('timestamp'),
                'error': result.get('error') if not result.get('success') else None
            }

        except Exception as e:
            logger.error(f"Email action failed: {e}", exc_info=True)
            return {
                'action_type': 'send_email',
                'success': False,
                'error': 'EXECUTION_ERROR',
                'message': str(e)
            }

    def _execute_facebook_action(self, step: Dict[str, Any], content: str, task_id: str = None) -> Dict[str, Any]:
        """
        Execute Facebook posting action.

        Args:
            step: Step dictionary
            content: Full plan content
            task_id: Original task ID to read from

        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing Facebook action: {step.get('action')}")

        # Try to read from original task file first (more reliable)
        facebook_params = None
        if task_id:
            from shared.folder_paths import NEEDS_ACTION
            task_file = NEEDS_ACTION / f"{task_id}.md"
            if task_file.exists():
                task_data = read_plan_file(task_file)
                facebook_params = self._extract_facebook_params(task_data['content'])
                logger.info(f"Extracted Facebook params from original task file")

        # Fallback to plan content
        if not facebook_params:
            facebook_params = self._extract_facebook_params(content)
            logger.info(f"Extracted Facebook params from plan content")

        logger.info(f"Facebook params: message length={len(facebook_params.get('message', '')) if facebook_params else 0}")

        if not facebook_params or not facebook_params.get('message'):
            logger.error("Failed to extract Facebook parameters from plan content")
            logger.debug(f"Plan content (first 500 chars): {content[:500]}")
            return {
                'action_type': 'post_facebook',
                'success': False,
                'error': 'FACEBOOK_PARAMS_NOT_FOUND',
                'message': 'Could not extract Facebook parameters from plan'
            }

        # Call MCP server to post to Facebook
        try:
            result = self.mcp_client.call_tool_sync(
                "post_facebook_page",
                {
                    "message": facebook_params.get('message'),
                    "link": facebook_params.get('link'),
                    "published": facebook_params.get('published', True)
                }
            )

            logger.info(f"Facebook action result: {result.get('success')}")

            return {
                'action_type': 'post_facebook',
                'success': result.get('success', False),
                'message': result.get('message', 'Facebook post created'),
                'post_id': result.get('post_id'),
                'timestamp': result.get('timestamp'),
                'error': result.get('error') if not result.get('success') else None
            }

        except Exception as e:
            logger.error(f"Facebook action failed: {e}", exc_info=True)
            return {
                'action_type': 'post_facebook',
                'success': False,
                'error': 'EXECUTION_ERROR',
                'message': str(e)
            }

    def _extract_email_preview(self, content: str) -> Optional[Dict[str, str]]:
        """
        Extract email parameters from action preview section or embedded task content.

        Args:
            content: Plan content

        Returns:
            Dictionary with to, subject, body or None
        """
        # Try to extract from the embedded task content (list format: "- To:", "- Subject:", "- Body:")
        to_match = re.search(r'-\s*To:\s*(.+)', content)
        subject_match = re.search(r'-\s*Subject:\s*(.+)', content)
        body_match = re.search(r'-\s*Body:\s*\n\n(.+?)(?=\n\*\*|\n##|\Z)', content, re.DOTALL)

        if to_match and subject_match and body_match:
            return {
                'to': to_match.group(1).strip(),
                'subject': subject_match.group(1).strip(),
                'body': body_match.group(1).strip()
            }

        # Fallback: try bold format (**To:**, **Subject:**, **Body:**)
        to_match = re.search(r'\*\*To:\*\*\s*(.+)', content)
        subject_match = re.search(r'\*\*Subject:\*\*\s*(.+)', content)
        body_match = re.search(r'\*\*Body:\*\*\s*\n(.+?)(?=\n\*\*|\n##|\Z)', content, re.DOTALL)

        if to_match and subject_match and body_match:
            return {
                'to': to_match.group(1).strip(),
                'subject': subject_match.group(1).strip(),
                'body': body_match.group(1).strip()
            }

        # Fallback: try Email Preview format
        preview_match = re.search(
            r'\*\*Email Preview\*\*:\s*\n- To:\s*(.+?)\n- Subject:\s*(.+?)\n- Body:.*?\n\s+(.+?)(?=\n\n|\Z)',
            content,
            re.DOTALL
        )

        if preview_match:
            return {
                'to': preview_match.group(1).strip(),
                'subject': preview_match.group(2).strip(),
                'body': preview_match.group(3).strip()
            }

        return None

    def _extract_facebook_params(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract Facebook parameters from plan content.

        Args:
            content: Plan content

        Returns:
            Dictionary with message, link, published or None
        """
        # First, try to find the "Post Details:" section specifically (from original task)
        post_details_match = re.search(r'\*\*Post Details:\*\*\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)

        if post_details_match:
            post_details_section = post_details_match.group(1)

            # Extract message from Post Details section
            message_match = re.search(r'-\s*Message:\s*(.+?)(?=\n-\s*Link:|\n-\s*Published:|\n\n|\Z)', post_details_section, re.DOTALL)

            if message_match:
                message = message_match.group(1).strip()

                # Extract link if present
                link_match = re.search(r'-\s*Link:\s*(.+)', post_details_section)
                link = link_match.group(1).strip() if link_match else None

                # Extract published flag if present
                published_match = re.search(r'-\s*Published:\s*(\w+)', post_details_section)
                published = published_match.group(1).lower() == 'true' if published_match else True

                return {
                    'message': message,
                    'link': link,
                    'published': published
                }

        # Fallback: try bold format (**Message:**, **Link:**, **Published:**) outside of preview
        message_match = re.search(
            r'\*\*Message:\*\*\s*\n(.+?)(?=\n\*\*Link:\*\*|\n\*\*Published:\*\*|\n##|\Z)',
            content,
            re.DOTALL
        )

        if message_match:
            message = message_match.group(1).strip()

            # Extract link if present
            link_match = re.search(r'\*\*Link:\*\*\s*(.+)', content)
            link = link_match.group(1).strip() if link_match else None

            # Extract published flag if present
            published_match = re.search(r'\*\*Published:\*\*\s*(\w+)', content)
            published = published_match.group(1).lower() == 'true' if published_match else True

            return {
                'message': message,
                'link': link,
                'published': published
            }

        return None

    def _complete_plan(self, plan_file: Path, results: list):
        """
        Mark plan as completed and move to Done folder.

        Args:
            plan_file: Path to plan file
            results: List of execution results
        """
        # Create execution summary
        summary_parts = []
        for result in results:
            action_type = result.get('action_type')
            if result.get('success'):
                summary_parts.append(f"{action_type}: {result.get('message', 'Success')}")
            else:
                summary_parts.append(f"{action_type}: FAILED - {result.get('message', 'Unknown error')}")

        execution_summary = "\n".join(summary_parts)

        # Update plan metadata
        update_plan_metadata(plan_file, {
            'execution_status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'execution_summary': execution_summary
        })

        # Move to Done folder
        done_path = DONE / plan_file.name
        shutil.move(str(plan_file), str(done_path))

        logger.info(f"Plan completed and moved to Done: {plan_file.name}")

    def _fail_plan(self, plan_file: Path, results: list):
        """
        Mark plan as failed and move back to Pending_Approval.

        Args:
            plan_file: Path to plan file
            results: List of execution results
        """
        # Create error summary
        error_parts = []
        for result in results:
            if not result.get('success'):
                action_type = result.get('action_type')
                error_parts.append(f"{action_type}: {result.get('error', 'UNKNOWN')} - {result.get('message', '')}")

        error_message = "\n".join(error_parts)

        # Update plan metadata
        update_plan_metadata(plan_file, {
            'execution_status': 'failed',
            'completed_at': datetime.now().isoformat(),
            'error_message': error_message
        })

        # Move back to Pending_Approval
        pending_path = PENDING_APPROVAL / plan_file.name
        shutil.move(str(plan_file), str(pending_path))

        logger.warning(f"Plan failed and moved back to Pending_Approval: {plan_file.name}")

    def handle_execution_error(self, plan_file: Path, error_message: str):
        """
        Handle unexpected execution errors.

        Args:
            plan_file: Path to plan file
            error_message: Error description
        """
        try:
            update_plan_metadata(plan_file, {
                'execution_status': 'failed',
                'error_message': error_message
            })

            # Move back to Pending_Approval
            pending_path = PENDING_APPROVAL / plan_file.name
            if plan_file.exists():
                shutil.move(str(plan_file), str(pending_path))

            logger.error(f"Plan execution error handled: {plan_file.name}")

        except Exception as e:
            logger.error(f"Failed to handle execution error for {plan_file.name}: {e}", exc_info=True)


if __name__ == "__main__":
    # Test plan executor
    executor = PlanExecutor()
    executed, errors = executor.execute_approved_plans()
    print(f"Executed: {executed}, Errors: {errors}")
