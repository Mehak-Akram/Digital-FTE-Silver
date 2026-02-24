"""
Rate limiter for MCP server functions.

Implements per-function rate limiting to prevent API quota exhaustion.
"""
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token bucket rate limiter with per-function limits.

    Tracks function calls within a sliding time window.
    """

    def __init__(self, limits: Dict[str, int]):
        """
        Initialize rate limiter.

        Args:
            limits: Dictionary mapping function names to requests per hour
                   e.g., {"send_email": 50, "post_facebook_page": 25}
        """
        self.limits = limits
        self.call_history: Dict[str, Deque[float]] = defaultdict(deque)
        self.window_seconds = 3600  # 1 hour window

    def check_limit(self, function_name: str) -> bool:
        """
        Check if function call is within rate limit.

        Args:
            function_name: Name of the function to check

        Returns:
            True if call is allowed, False if rate limit exceeded
        """
        if function_name not in self.limits:
            return True  # No limit configured, allow call

        limit = self.limits[function_name]
        now = time.time()
        cutoff_time = now - self.window_seconds

        # Remove calls outside the time window
        history = self.call_history[function_name]
        while history and history[0] < cutoff_time:
            history.popleft()

        # Check if we're under the limit
        return len(history) < limit

    def record_call(self, function_name: str):
        """
        Record a function call for rate limiting.

        Args:
            function_name: Name of the function that was called
        """
        self.call_history[function_name].append(time.time())

    def get_remaining_calls(self, function_name: str) -> int:
        """
        Get number of remaining calls allowed in current window.

        Args:
            function_name: Name of the function to check

        Returns:
            Number of calls remaining, or -1 if no limit configured
        """
        if function_name not in self.limits:
            return -1

        limit = self.limits[function_name]
        now = time.time()
        cutoff_time = now - self.window_seconds

        # Remove calls outside the time window
        history = self.call_history[function_name]
        while history and history[0] < cutoff_time:
            history.popleft()

        return max(0, limit - len(history))

    def get_reset_time(self, function_name: str) -> datetime:
        """
        Get time when rate limit will reset for a function.

        Args:
            function_name: Name of the function to check

        Returns:
            Datetime when the oldest call will expire from the window
        """
        history = self.call_history[function_name]
        if not history:
            return datetime.now()

        oldest_call = history[0]
        reset_time = oldest_call + self.window_seconds
        return datetime.fromtimestamp(reset_time)

    def reset(self, function_name: str = None):
        """
        Reset rate limit history.

        Args:
            function_name: Optional function name to reset. If None, resets all.
        """
        if function_name:
            self.call_history[function_name].clear()
        else:
            self.call_history.clear()


if __name__ == "__main__":
    # Test rate limiter
    limiter = RateLimiter({
        "send_email": 50,
        "post_facebook_page": 25
    })

    # Test email rate limiting
    print(f"Email remaining: {limiter.get_remaining_calls('send_email')}")

    for i in range(3):
        if limiter.check_limit("send_email"):
            limiter.record_call("send_email")
            print(f"Email call {i+1} allowed")
        else:
            print(f"Email call {i+1} blocked - rate limit exceeded")

    print(f"Email remaining: {limiter.get_remaining_calls('send_email')}")
    print(f"Reset time: {limiter.get_reset_time('send_email')}")

    # Test Facebook rate limiting
    print(f"\nFacebook remaining: {limiter.get_remaining_calls('post_facebook_page')}")

    for i in range(2):
        if limiter.check_limit("post_facebook_page"):
            limiter.record_call("post_facebook_page")
            print(f"Facebook call {i+1} allowed")
        else:
            print(f"Facebook call {i+1} blocked - rate limit exceeded")

    print(f"Facebook remaining: {limiter.get_remaining_calls('post_facebook_page')}")
