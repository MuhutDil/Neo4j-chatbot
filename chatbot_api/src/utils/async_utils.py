"""Async utility functions for the Hospital Chatbot.

This module provides asynchronous helper utilities, including retry logic
for handling transient failures in async operations.
"""

import asyncio


def async_retry(max_retries: int=3, delay: int=1):
    """Decorator that adds async retry logic to a function.

    When an async function decorated with this decorator raises an exception,
    it will be retried up to `max_retries` times with `delay` seconds between
    attempts. If all retries fail, the last exception is raised.

    Args:
        max_retries (int): Maximum number of retry attempts. Defaults to 3.
        delay (int): Delay in seconds between retry attempts. Defaults to 1.

    Returns:
        callable: A decorator function that wraps the target async function
            with retry logic.

    Raises:
        ValueError: If all retry attempts fail, raises ValueError with the
            message 'Failed after {max_retries} attempts'.

    Example:
        @async_retry(max_retries=5, delay=2)
        async def fetch_data():
            # async operation that may fail
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except ConnectionError:
                    print(f"Attempt {attempt} failed")
                    await asyncio.sleep(delay)

            raise ValueError(f"Failed after {max_retries} attempts")

        return wrapper

    return decorator
