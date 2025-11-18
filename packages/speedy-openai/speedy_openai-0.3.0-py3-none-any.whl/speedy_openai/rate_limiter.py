"""
A flexible rate limiter implementation for managing API request rates and token consumption.

This class provides mechanisms to control both request frequency and token usage in API calls,
particularly useful for services with dual-limit systems. It supports dynamic limit updates
from API response headers and handles waiting periods when limits are reached.

Process Flow:
1. Initialize with maximum requests and/or token limits
2. Before making an API call:
   - Check current limits via wait_for_availability()
   - If limits are exceeded, sleep until reset
3. After API calls:
   - Update limits from response headers if available
   - Track remaining requests and tokens
4. Auto-reset limits when reset time is reached
"""

from __future__ import annotations

import asyncio
import re
import time

from loguru import logger as log


class RateLimiter:
    """A rate limiter implementation for managing API request and token limits.

    Attributes:
        REGEX_TIME (Pattern): Regular expression pattern for parsing time strings.
        max_requests (int | None): Maximum number of requests allowed in the time window.
        max_tokens (int | None): Maximum number of tokens allowed in the time window.
        remaining_requests (int): Number of requests remaining in the current window.
        remaining_tokens (int): Number of tokens remaining in the current window.
        reset_time_requests (float): Timestamp when request limit resets.
        reset_time_tokens (float): Timestamp when token limit resets.

    Args:
        max_requests (int | None, optional): Maximum number of requests. Defaults to None.
        max_tokens (int | None, optional): Maximum number of tokens. Defaults to None.
    """

    REGEX_TIME = re.compile(r"(?P<value>\d+)(?P<unit>[smhms]+)")

    def __init__(self, max_sleep_time: int, max_requests: int | None = None, max_tokens: int | None = None):
        self.max_requests = max_requests
        self.max_tokens = max_tokens
        self.remaining_requests = max_requests
        self.remaining_tokens = max_tokens
        self.max_sleep_time = max_sleep_time
        self.reset_time_requests = time.monotonic() + 60
        self.reset_time_tokens = time.monotonic() + 60

    async def wait_for_availability(self, required_tokens: int = 0):
        """Wait until rate limits allow for the requested operation.

        Note: This method only checks availability but doesn't consume resources.
        Resources are consumed only after successful API calls via consume_resources().
        """
        while self.remaining_requests <= 0 or (self.max_tokens is not None and self.remaining_tokens < required_tokens):
            self.update_limits()
            sleep_time = self._get_seconds_to_sleep()
            log.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
            await asyncio.sleep(sleep_time)

    def consume_resources(self, required_tokens: int = 0):
        """Consume the specified resources after a successful API call.

        This method should be called only after a successful API response
        to avoid consuming resources for failed requests that will be retried.

        Args:
            required_tokens (int): Number of tokens to consume. Defaults to 0.
        """
        if self.remaining_requests > 0:
            self.remaining_requests -= 1

        if self.max_tokens is not None and self.remaining_tokens >= required_tokens:
            self.remaining_tokens -= required_tokens

    def update_limits(self):
        """Update rate limits based on current time."""
        current_time = time.monotonic()

        if current_time >= self.reset_time_requests:
            old_remaining = self.remaining_requests
            self.remaining_requests = self.max_requests
            self.reset_time_requests = current_time + 60
            log.debug(f"Request limit reset: {old_remaining} -> {self.remaining_requests}")

        if self.max_tokens is not None and current_time >= self.reset_time_tokens:
            old_remaining = self.remaining_tokens
            self.remaining_tokens = self.max_tokens
            self.reset_time_tokens = current_time + 60
            log.debug(f"Token limit reset: {old_remaining} -> {self.remaining_tokens}")

    def update_from_headers(self, headers: dict[str, str]):
        """Update rate limit information from response headers."""
        old_requests = self.remaining_requests
        old_tokens = self.remaining_tokens

        self.remaining_requests = int(headers.get("x-ratelimit-remaining-requests", self.remaining_requests))

        if self.max_tokens is not None:
            self.remaining_tokens = int(headers.get("x-ratelimit-remaining-tokens", self.remaining_tokens))
            reset_tokens_seconds = self._parse_reset_time(headers.get("x-ratelimit-reset-tokens", "60s"))
            self.reset_time_tokens = time.monotonic() + reset_tokens_seconds

        reset_requests_seconds = self._parse_reset_time(headers.get("x-ratelimit-reset-requests", "60s"))
        self.reset_time_requests = time.monotonic() + reset_requests_seconds

    def get_status(self) -> dict[str, any]:
        """Get current rate limiter status for debugging/monitoring."""
        current_time = time.monotonic()
        return {
            "remaining_requests": self.remaining_requests,
            "remaining_tokens": self.remaining_tokens,
            "seconds_until_request_reset": max(0, self.reset_time_requests - current_time),
            "seconds_until_token_reset": max(0, self.reset_time_tokens - current_time) if self.max_tokens else None,
            "max_requests": self.max_requests,
            "max_tokens": self.max_tokens,
        }

    def _get_seconds_to_sleep(self) -> float:
        """Calculate the number of seconds to sleep before next request."""
        current_time = time.monotonic()

        if self.max_tokens is None:
            sleep_time = self.reset_time_requests - current_time
        else:
            sleep_time = min(
                self.reset_time_requests - current_time,
                self.reset_time_tokens - current_time,
            )

        # Ensure we sleep at least 1 second but no more than max_sleep_time
        return max(min(sleep_time, self.max_sleep_time), 1)

    def _parse_reset_time(self, reset_time_str: str) -> float:
        """Parse a reset time string into seconds."""
        total_seconds = 0
        for match in self.REGEX_TIME.finditer(reset_time_str):
            value = int(match.group("value"))
            unit = match.group("unit")
            if unit == "s":
                total_seconds += value
            elif unit == "m":
                total_seconds += value * 60
            elif unit == "h":
                total_seconds += value * 3600
            elif unit == "ms":
                total_seconds += value / 1000.0
        return total_seconds if total_seconds > 0 else 60

    def can_make_request(self, required_tokens: int = 0) -> bool:
        """Check if a request can be made without waiting.

        Args:
            required_tokens (int): Number of tokens required for the request.

        Returns:
            bool: True if the request can be made immediately, False otherwise.
        """
        self.update_limits()
        return self.remaining_requests > 0 and (self.max_tokens is None or self.remaining_tokens >= required_tokens)

    def reserve_resources(self, required_tokens: int = 0) -> bool:
        """Reserve resources for a request if available.

        This is an alternative to wait_for_availability() + consume_resources()
        for cases where you want to reserve resources immediately.

        Args:
            required_tokens (int): Number of tokens to reserve.

        Returns:
            bool: True if resources were successfully reserved, False otherwise.
        """
        if not self.can_make_request(required_tokens):
            return False

        self.consume_resources(required_tokens)
        return True
