"""
Performance optimization utilities and configurations.
"""
from functools import wraps
from typing import Callable, Any
import time
import asyncio
import logging

logger = logging.getLogger(__name__)


def time_it(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on failure with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__} after {current_delay}s")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    logger.error(f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}")

            logger.error(f"All retries exhausted for {func.__name__}")
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__} after {current_delay}s")
                        time.sleep(current_delay)
                        current_delay *= backoff

                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    logger.error(f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}")

            logger.error(f"All retries exhausted for {func.__name__}")
            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def cache_result(ttl: int = 3600):
    """
    Decorator to cache function results.
    Note: This is a simple implementation. For production, use Redis or similar.
    """
    cache = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Create cache key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            if key in cache:
                cached_result, cached_time = cache[key]
                if time.time() - cached_time < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache[key] = (result, time.time())
            logger.debug(f"Cached result for {func.__name__}")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Create cache key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            if key in cache:
                cached_result, cached_time = cache[key]
                if time.time() - cached_time < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache[key] = (result, time.time())
            logger.debug(f"Cached result for {func.__name__}")

            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def rate_limit(max_calls: int = 10, period: float = 60.0):
    """
    Decorator to rate limit function calls.
    """
    calls = []

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            now = time.time()

            # Remove old calls
            calls[:] = [call_time for call_time in calls if now - call_time < period]

            # Check rate limit
            if len(calls) >= max_calls:
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {period} seconds")

            # Add current call
            calls.append(now)

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            now = time.time()

            # Remove old calls
            calls[:] = [call_time for call_time in calls if now - call_time < period]

            # Check rate limit
            if len(calls) >= max_calls:
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {period} seconds")

            # Add current call
            calls.append(now)

            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


async def batch_process(items: list, process_func: Callable, batch_size: int = 10, delay: float = 0.1):
    """
    Process items in batches to avoid overwhelming resources.
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        # Process batch
        batch_results = await asyncio.gather(*[process_func(item) for item in batch])
        results.extend(batch_results)

        # Small delay between batches
        if i + batch_size < len(items):
            await asyncio.sleep(delay)

    return results