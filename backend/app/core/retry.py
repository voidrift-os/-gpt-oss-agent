import asyncio
import logging
from typing import Any, Callable, Type, Union
from tenacity import (
    retry,
    wait_exponential_jitter,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
from aiobreaker import CircuitBreaker
import httpx

logger = logging.getLogger(__name__)


class TransientAPIError(Exception):
    """Exception for transient API errors that should be retried"""
    pass


class APIError(Exception):
    """General API error"""
    pass


# Circuit breaker for external API calls
api_circuit_breaker = CircuitBreaker(
    fail_max=5,  # Open circuit after 5 failures
    reset_timeout=60,  # Try again after 60 seconds
    exclude=[httpx.HTTPStatusError]  # Don't count HTTP errors as circuit failures
)


def create_retry_decorator(
    max_attempts: int = 5,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
    retry_exceptions: tuple = (TransientAPIError, httpx.ConnectError, httpx.TimeoutException)
):
    """Create a retry decorator with exponential backoff and jitter"""
    return retry(
        wait=wait_exponential_jitter(initial=initial_wait, max=max_wait),
        stop=stop_after_attempt(max_attempts),
        retry=retry_if_exception_type(retry_exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO)
    )


# Pre-configured retry decorators
retry_api_call = create_retry_decorator(
    max_attempts=5,
    initial_wait=1.0,
    max_wait=10.0
)

retry_db_operation = create_retry_decorator(
    max_attempts=3,
    initial_wait=0.5,
    max_wait=5.0,
    retry_exceptions=(Exception,)  # Retry on any exception for DB ops
)


@api_circuit_breaker
@retry_api_call
async def make_external_api_call(
    url: str,
    method: str = "GET",
    headers: dict = None,
    json_data: dict = None,
    timeout: float = 10.0
) -> dict:
    """
    Make an external API call with circuit breaker and retry logic
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data
            )
            
            # Check for transient errors that should be retried
            if response.status_code in [429, 500, 502, 503, 504]:
                raise TransientAPIError(f"Transient error: {response.status_code}")
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            return response.json()
            
        except httpx.ConnectError as e:
            logger.warning(f"Connection error: {e}")
            raise TransientAPIError(f"Connection error: {e}")
        
        except httpx.TimeoutException as e:
            logger.warning(f"Timeout error: {e}")
            raise TransientAPIError(f"Timeout error: {e}")
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 400:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise APIError(f"HTTP error {e.response.status_code}")
            raise


async def with_retry_and_circuit_breaker(
    func: Callable,
    *args,
    max_attempts: int = 3,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic and circuit breaker protection
    """
    @create_retry_decorator(max_attempts=max_attempts)
    async def _execute():
        return await func(*args, **kwargs)
    
    return await _execute()
