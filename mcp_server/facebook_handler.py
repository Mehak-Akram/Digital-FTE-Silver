"""
Facebook Handler for Silver Tier MCP Server.

Implements post_facebook_page function with Meta Graph API integration and circuit breaker.
"""
import os
import requests
import time
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dotenv import load_dotenv

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for Facebook API calls.

    Opens after consecutive failures, closes after successful recovery.
    """

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Seconds to wait before half-open state
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self.last_failure_time and \
               time.time() - self.last_failure_time >= self.timeout_seconds:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                logger.info("Circuit breaker CLOSED after successful recovery")
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker reopening after failure in HALF_OPEN state")
            self.state = CircuitState.OPEN
            self.success_count = 0

        elif self.failure_count >= self.failure_threshold:
            logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")
            self.state = CircuitState.OPEN


class FacebookHandler:
    """
    Handles Facebook Page posting via Meta Graph API with circuit breaker.
    """

    def __init__(self):
        """Initialize Facebook handler with API configuration."""
        self.api_version = "v18.0"
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

        # Validate configuration
        if not self.page_id or not self.access_token:
            logger.error("Facebook configuration incomplete: FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set")
            raise ValueError("Facebook credentials not configured in environment variables")

        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

        logger.info(f"Facebook handler initialized: Page ID {self.page_id}")

    def post_facebook_page(
        self,
        message: str,
        link: Optional[str] = None,
        published: bool = True
    ) -> Dict[str, Any]:
        """
        Post a message to Facebook Page.

        Args:
            message: Post content (text)
            link: Optional URL to include in post
            published: Whether to publish immediately (default: True)

        Returns:
            Dictionary with success status, post_id, post_url, timestamp, and optional error

        Raises:
            ValueError: If parameters are invalid
        """
        logger.info(f"Posting to Facebook Page, message length: {len(message)}")

        # Validate parameters
        self._validate_post_params(message)

        # Post with circuit breaker protection
        try:
            result = self.circuit_breaker.call(
                self._post_with_api,
                message,
                link,
                published
            )
            return result

        except requests.exceptions.HTTPError as e:
            return self._handle_http_error(e)

        except Exception as e:
            error_msg = f"Facebook posting error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": "FACEBOOK_POST_ERROR",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    def _validate_post_params(self, message: str):
        """
        Validate Facebook post parameters.

        Args:
            message: Post message

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate message
        if not message or len(message.strip()) == 0:
            raise ValueError("Facebook post message cannot be empty")

        if len(message) > 63206:
            raise ValueError(f"Facebook post message too long: {len(message)} chars (max 63206)")

    def _post_with_api(
        self,
        message: str,
        link: Optional[str],
        published: bool
    ) -> Dict[str, Any]:
        """
        Post to Facebook via Graph API.

        Args:
            message: Post message
            link: Optional link
            published: Publish immediately

        Returns:
            Result dictionary

        Raises:
            requests.exceptions.HTTPError: If API call fails
        """
        endpoint = f"{self.base_url}/{self.page_id}/feed"

        # Build request payload
        payload = {
            "message": message,
            "access_token": self.access_token,
            "published": str(published).lower()
        }

        if link:
            payload["link"] = link

        # Make API request
        response = requests.post(endpoint, data=payload, timeout=30)
        response.raise_for_status()

        # Parse response
        data = response.json()
        post_id = data.get("id")

        # Build post URL
        post_url = f"https://facebook.com/{post_id.replace('_', '/posts/')}" if post_id else None

        result = {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Facebook post published successfully: {post_id}")
        return result

    def _handle_http_error(self, error: requests.exceptions.HTTPError) -> Dict[str, Any]:
        """
        Handle HTTP errors from Facebook API.

        Args:
            error: HTTP error

        Returns:
            Error result dictionary
        """
        status_code = error.response.status_code
        error_data = error.response.json() if error.response.text else {}
        error_message = error_data.get("error", {}).get("message", str(error))

        if status_code == 401 or status_code == 403:
            error_code = "INVALID_ACCESS_TOKEN"
            logger.error(f"Facebook authentication error: {error_message}")
        elif status_code == 429:
            error_code = "RATE_LIMIT_EXCEEDED"
            logger.warning(f"Facebook rate limit exceeded: {error_message}")
        elif status_code >= 500:
            error_code = "API_CONNECTION_ERROR"
            logger.error(f"Facebook API server error: {error_message}")
        else:
            error_code = "FACEBOOK_API_ERROR"
            logger.error(f"Facebook API error {status_code}: {error_message}")

        return {
            "success": False,
            "error": error_code,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test Facebook handler
    try:
        handler = FacebookHandler()
        print(f"Facebook handler initialized successfully")
        print(f"API Version: {handler.api_version}")
        print(f"Page ID: {handler.page_id}")
        print(f"Circuit breaker state: {handler.circuit_breaker.state.value}")

    except Exception as e:
        print(f"Error: {e}")
