"""
Email Handler for Silver Tier MCP Server.

Implements send_email function with SMTP integration, validation, and retry logic.
"""
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class EmailHandler:
    """
    Handles email sending via SMTP with validation and retry logic.
    """

    def __init__(self):
        """Initialize email handler with SMTP configuration."""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_address = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")

        # Validate configuration
        if not self.from_address or not self.password:
            logger.error("Email configuration incomplete: EMAIL_ADDRESS or EMAIL_PASSWORD not set")
            raise ValueError("Email credentials not configured in environment variables")

        logger.info(f"Email handler initialized: {self.smtp_host}:{self.smtp_port}")

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        content_type: str = "text/plain"
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            content_type: Email content type (text/plain or text/html)

        Returns:
            Dictionary with success status, message_id, timestamp, and optional error

        Raises:
            ValueError: If parameters are invalid
            smtplib.SMTPException: If SMTP operation fails
        """
        logger.info(f"Sending email to {to}, subject: {subject}")

        # Validate parameters
        self._validate_email_params(to, subject, body)

        # Create message
        msg = self._create_message(to, subject, body, cc, bcc, content_type)

        # Send with retry logic
        try:
            message_id = self._send_with_retry(msg, to, cc, bcc)

            result = {
                "success": True,
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Email sent successfully to {to}, message_id: {message_id}")
            return result

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "AUTHENTICATION_ERROR",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Invalid recipient: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "INVALID_RECIPIENT",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "SMTP_CONNECTION_ERROR",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": "UNKNOWN_ERROR",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    def _validate_email_params(self, to: str, subject: str, body: str):
        """
        Validate email parameters.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate recipient email
        if not to or not self._is_valid_email(to):
            raise ValueError(f"Invalid recipient email address: {to}")

        # Validate subject
        if not subject or len(subject.strip()) == 0:
            raise ValueError("Email subject cannot be empty")

        if len(subject) > 200:
            raise ValueError(f"Email subject too long: {len(subject)} chars (max 200)")

        # Validate body
        if not body or len(body.strip()) == 0:
            raise ValueError("Email body cannot be empty")

        if len(body) > 50000:
            raise ValueError(f"Email body too large: {len(body)} chars (max 50000)")

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
        content_type: str
    ) -> MIMEMultipart:
        """
        Create email message.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            content_type: Content type

        Returns:
            MIMEMultipart message
        """
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = to
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = ', '.join(cc)

        # Attach body
        if content_type == "text/html":
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        return msg

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        retry=retry_if_exception_type((smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected)),
        reraise=True
    )
    def _send_with_retry(
        self,
        msg: MIMEMultipart,
        to: str,
        cc: Optional[List[str]],
        bcc: Optional[List[str]]
    ) -> str:
        """
        Send email with automatic retry on transient errors.

        Args:
            msg: Email message
            to: Recipient
            cc: CC recipients
            bcc: BCC recipients

        Returns:
            Message ID

        Raises:
            smtplib.SMTPException: If sending fails after retries
        """
        # Build recipient list
        recipients = [to]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)

        # Connect to SMTP server
        server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)

        try:
            # Enable TLS if configured
            if self.smtp_use_tls:
                server.starttls()

            # Authenticate
            server.login(self.from_address, self.password)

            # Send email
            server.send_message(msg)

            # Get message ID (if available)
            message_id = msg.get('Message-ID', f"<{datetime.now().timestamp()}@{self.smtp_host}>")

            return message_id

        finally:
            server.quit()


if __name__ == "__main__":
    # Test email handler
    try:
        handler = EmailHandler()
        print(f"Email handler initialized successfully")
        print(f"SMTP: {handler.smtp_host}:{handler.smtp_port}")
        print(f"From: {handler.from_address}")

        # Test email validation
        print(f"\nValidating test@example.com: {handler._is_valid_email('test@example.com')}")
        print(f"Validating invalid-email: {handler._is_valid_email('invalid-email')}")

    except Exception as e:
        print(f"Error: {e}")
