"""
Gmail Watcher for Silver Tier AI Employee.

Monitors Gmail inbox via IMAP and creates task files for incoming emails.
"""
import imaplib
import email
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger
from shared.folder_paths import INBOX
from shared.file_utils import write_task_file

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class GmailWatcher:
    """
    Monitors Gmail inbox via IMAP and creates task files for new emails.
    """

    def __init__(self):
        """Initialize Gmail watcher with IMAP configuration."""
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.imap_host = "imap.gmail.com"
        self.imap_port = 993

        # Validate configuration
        if not self.email_address or not self.email_password:
            logger.error("Gmail configuration incomplete: EMAIL_ADDRESS or EMAIL_PASSWORD not set")
            raise ValueError("Gmail credentials not configured in environment variables")

        # State tracking
        self.last_uid = self._load_last_uid()
        self.connection = None
        self.retry_count = 0
        self.max_retries = 4
        self.backoff_times = [60, 120, 300, 600]  # 1min, 2min, 5min, 10min

        logger.info(f"Gmail watcher initialized for {self.email_address}")

    def connect(self) -> bool:
        """
        Connect to Gmail IMAP server with retry logic.

        Returns:
            True if connected successfully, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Connecting to Gmail IMAP (attempt {attempt + 1}/{self.max_retries})")

                self.connection = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
                self.connection.login(self.email_address, self.email_password)
                self.connection.select('inbox')

                logger.info("Successfully connected to Gmail IMAP")
                self.retry_count = 0
                return True

            except Exception as e:
                logger.error(f"IMAP connection failed (attempt {attempt + 1}): {e}")
                self.retry_count += 1

                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_times[attempt]
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        logger.error("Failed to connect to Gmail after all retries")
        return False

    def disconnect(self):
        """Disconnect from Gmail IMAP server."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from Gmail IMAP")
            except Exception as e:
                logger.error(f"Error disconnecting from IMAP: {e}")
            finally:
                self.connection = None

    def check_new_emails(self) -> int:
        """
        Check for new emails and create task files.

        Returns:
            Number of new emails processed
        """
        if not self.connection:
            if not self.connect():
                return 0

        try:
            # Search for unseen messages
            status, messages = self.connection.search(None, 'UNSEEN')

            if status != 'OK':
                logger.error(f"IMAP search failed: {status}")
                return 0

            email_ids = messages[0].split()

            if not email_ids:
                logger.debug("No new emails found")
                return 0

            logger.info(f"Found {len(email_ids)} new emails")

            processed_count = 0
            for email_id in email_ids:
                try:
                    if self._process_email(email_id):
                        processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}", exc_info=True)

            return processed_count

        except Exception as e:
            logger.error(f"Error checking emails: {e}", exc_info=True)
            self.disconnect()
            return 0

    def _process_email(self, email_id: bytes) -> bool:
        """
        Process a single email and create task file.

        Args:
            email_id: Email UID

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Fetch email
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')

            if status != 'OK':
                logger.error(f"Failed to fetch email {email_id}")
                return False

            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Extract email details
            from_addr = email_message.get('From', 'unknown@example.com')
            subject = email_message.get('Subject', 'No Subject')
            date_str = email_message.get('Date', datetime.now().isoformat())

            # Extract body
            body = self._extract_body(email_message)

            # Create task file
            task_id = self._generate_task_id(email_id.decode())
            self._create_task_file(task_id, from_addr, subject, body, date_str, email_id.decode())

            # Mark as seen
            self.connection.store(email_id, '+FLAGS', '\\Seen')

            # Update last UID
            self._save_last_uid(email_id.decode())

            logger.info(f"Created task from email: {subject} (from {from_addr})")
            return True

        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}", exc_info=True)
            return False

    def _extract_body(self, email_message) -> str:
        """
        Extract email body content.

        Args:
            email_message: Email message object

        Returns:
            Email body text
        """
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())

        return body.strip()

    def _generate_task_id(self, email_uid: str) -> str:
        """
        Generate unique task ID from email UID.

        Args:
            email_uid: Email UID

        Returns:
            Task ID
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{timestamp}-email-{email_uid}"

    def _create_task_file(
        self,
        task_id: str,
        from_addr: str,
        subject: str,
        body: str,
        date_str: str,
        email_uid: str
    ):
        """
        Create task file from email.

        Args:
            task_id: Task ID
            from_addr: Sender email address
            subject: Email subject
            body: Email body
            date_str: Email date
            email_uid: Email UID
        """
        # Create task metadata
        metadata = {
            'id': task_id,
            'title': f"Email: {subject}",
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'priority': 'P3',
            'source': 'email',
            'email_source': True,
            'original_email_id': email_uid
        }

        # Create task content
        content = f"""# Email: {subject}

**From**: {from_addr}
**Date**: {date_str}
**Subject**: {subject}

## Email Content

{body}

---

*This task was automatically created from an incoming email.*
"""

        # Write task file
        task_filename = f"{task_id}.md"
        task_path = INBOX / task_filename
        write_task_file(task_path, metadata, content)

        logger.info(f"Task file created: {task_filename}")

    def _load_last_uid(self) -> Optional[str]:
        """Load last processed email UID from state file."""
        state_file = Path(__file__).parent / "gmail_watcher_state.txt"

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Error loading last UID: {e}")

        return None

    def _save_last_uid(self, uid: str):
        """Save last processed email UID to state file."""
        state_file = Path(__file__).parent / "gmail_watcher_state.txt"

        try:
            with open(state_file, 'w') as f:
                f.write(uid)
        except Exception as e:
            logger.error(f"Error saving last UID: {e}")

    def run(self, check_interval: int = 300):
        """
        Run Gmail watcher continuously.

        Args:
            check_interval: Seconds between checks (default: 300 = 5 minutes)
        """
        logger.info(f"Starting Gmail watcher (check interval: {check_interval}s)")

        while True:
            try:
                processed = self.check_new_emails()
                if processed > 0:
                    logger.info(f"Processed {processed} new emails")

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Gmail watcher stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in Gmail watcher loop: {e}", exc_info=True)
                time.sleep(60)  # Wait before retrying

        self.disconnect()


def main():
    """Run the Gmail watcher."""
    try:
        watcher = GmailWatcher()
        watcher.run(check_interval=300)  # Check every 5 minutes
    except Exception as e:
        logger.error(f"Gmail watcher failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
