from __future__ import annotations

import asyncio
import time
from typing import Any

import aiohttp
import tiktoken
from aiohttp import ClientResponseError
from loguru import logger as log
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm

from .configs import Configs, Request
from .rate_limiter import RateLimiter


class OpenAIClient:
    """
    Asynchronous client for making requests to the OpenAI API with built-in rate limiting and concurrency control.

    Attributes:
        config (Configs): Configuration settings for the client
        headers (dict): HTTP headers for API requests
        rate_limiter (RateLimiter): Rate limiting controller
        semaphore (asyncio.Semaphore): Concurrency control mechanism
        base_url (str): Base URL for the OpenAI API
    """

    def __init__(
        self,
        api_key: str,
        **kwargs: Any,
    ):
        """
        Initialize the AsyncClient.

        Args:
            api_key (str): OpenAI API key
            **kwargs: Additional configuration parameters including:
                - max_requests_per_min (int): Maximum requests per minute
                - max_tokens_per_min (int): Maximum tokens per minute
                - max_concurrent_requests (int): Maximum concurrent requests
                - max_retries (int): Maximum number of retry attempts
                - max_sleep_time (int): Maximum sleep time between retries
        """
        self.config = Configs(**{"api_key": api_key, **self._get_config_params(kwargs)})
        self.headers = {"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}
        self.rate_limiter = RateLimiter(
            self.config.max_sleep_time, self.config.max_requests_per_min, self.config.max_tokens_per_min
        )
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self.base_url = "https://api.openai.com"

    @staticmethod
    def _get_config_params(kwargs):
        """Extracts and returns a dictionary of valid configuration parameters from the provided keyword arguments."""
        valid_params = {
            "max_requests_per_min",
            "max_tokens_per_min",
            "max_concurrent_requests",
            "max_retries",
            "max_sleep_time",
        }

        return {key: value for key, value in kwargs.items() if key in valid_params and value is not None}

    @staticmethod
    def count_tokens(messages: list | str, model: str) -> int:
        """Counts the number of tokens required for a given list of messages and model."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            log.warning(f"Model {model} not found in tiktoken. Using cl100k_base as fallback.")
            encoding = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        if isinstance(messages, str):
            num_tokens += len(encoding.encode(messages))
            return num_tokens

        for message in messages:
            num_tokens += 4
            for value in message.values():
                num_tokens += len(encoding.encode(value))

        num_tokens += 2
        return num_tokens

    def _create_error_dict(self, request: Request, error: Exception) -> dict:
        """Create a standardized error dictionary."""
        error_info = {
            "custom_id": request.custom_id,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
            }
        }
        
        # Add specific ClientResponseError details
        if isinstance(error, ClientResponseError):
            error_info["error"].update({
                "status": error.status,
                "url": str(error.request_info.url) if error.request_info else None,
                "headers": dict(error.headers) if error.headers else None,
            })
        
        return error_info

    async def _make_request(self, request: Request, required_tokens: int) -> dict:
        """Make an HTTP POST request to the OpenAI API with retry mechanism."""

        # Create retry decorator with config-based parameters - only retry on specific exceptions
        retry_decorator = retry(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_random_exponential(multiplier=1, max=self.config.max_sleep_time),
            reraise=True,
            
        )

        @retry_decorator
        async def _do_request():
            # Wait for rate limit availability but don't consume resources yet
            await self.rate_limiter.wait_for_availability(required_tokens)

            url = f"{self.base_url}{request.url}"

            # Move semaphore inside retry logic to avoid holding it during retry delays
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=self.headers, json=request.body) as response:
                        response.raise_for_status()
                        # Only consume resources after successful response
                        self.rate_limiter.consume_resources(required_tokens)
                        self.rate_limiter.update_from_headers(response.headers)
                        return {"custom_id": request.custom_id, "response": await response.json()}

        try:
            return await _do_request()
        except Exception as e:
            # Return error dict instead of raising
            return self._create_error_dict(request, e)

    async def process_request(self, request_data: dict) -> dict:
        """Process a single API request."""
        try:
            request = Request(**request_data)
            model = request.body.get("model")
            text = request.body.get("messages") or request.body.get("input")
            required_tokens = self.count_tokens(text, model)

            response = await self._make_request(request, required_tokens)

            # Check if the response is an error dict
            if "error" in response:
                return response

            if "response" not in response:
                error_msg = f"Invalid response format: {response}"
                return {
                    "custom_id": request.custom_id,
                    "error": {
                        "type": "ValueError",
                        "message": error_msg,
                    }
                }

            api_response = response["response"]
            if "/embeddings" in request.url and "data" not in api_response:
                error_msg = f"Invalid embedding response format: {response}"
                return {
                    "custom_id": request.custom_id,
                    "error": {
                        "type": "ValueError",
                        "message": error_msg,
                    }
                }
            if "/completions" in request.url and "choices" not in api_response:
                error_msg = f"Invalid completion response format: {response}"
                return {
                    "custom_id": request.custom_id,
                    "error": {
                        "type": "ValueError",
                        "message": error_msg,
                    }
                }

            return response
            
        except Exception as e:
            # Handle any other exceptions at the top level
            return {
                "custom_id": request_data.get("custom_id", "unknown"),
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                }
            }

    async def process_batch(self, requests: list[dict]) -> list[dict]:
        """
        Process multiple API requests concurrently.

        Note:
            Uses tqdm for progress tracking and logs processing time
        """
        t0 = time.monotonic()
        log.info(f"Processing {len(requests)} requests")

        with tqdm(total=len(requests), desc="Processing requests") as pbar:
            tasks = []
            for req in requests:
                task = asyncio.create_task(self.process_request(req))
                task.add_done_callback(lambda _: pbar.update(1))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        processing_time = (time.monotonic() - t0) / 60
        log.info(f"Batch processed in {processing_time:.2f} minutes")
        return results