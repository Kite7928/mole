"""
Monitoring and metrics collection utilities.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable
from .logger import logger


# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

article_generation_count = Counter(
    'article_generation_total',
    'Total articles generated',
    ['status', 'source']
)

article_generation_duration = Histogram(
    'article_generation_duration_seconds',
    'Article generation duration',
    ['source']
)

news_fetch_count = Counter(
    'news_fetch_total',
    'Total news fetched',
    ['source', 'status']
)

wechat_api_calls = Counter(
    'wechat_api_calls_total',
    'Total WeChat API calls',
    ['endpoint', 'status']
)

active_tasks = Gauge(
    'active_tasks',
    'Number of active tasks'
)

system_info = Info(
    'system_info',
    'System information'
)


def track_requests(func: Callable) -> Callable:
    """
    Decorator to track HTTP requests.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # Record metrics
            request_count.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('path', '/'),
                status='success'
            ).inc()

            duration = time.time() - start_time
            request_duration.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('path', '/')
            ).observe(duration)

            return result

        except Exception as e:
            # Record error
            request_count.labels(
                method=kwargs.get('method', 'GET'),
                endpoint=kwargs.get('path', '/'),
                status='error'
            ).inc()

            logger.error(f"Request failed: {str(e)}")
            raise

    return wrapper


def track_article_generation(func: Callable) -> Callable:
    """
    Decorator to track article generation.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        source = kwargs.get('source', 'unknown')

        try:
            result = await func(*args, **kwargs)

            # Record success
            article_generation_count.labels(
                status='success',
                source=source
            ).inc()

            duration = time.time() - start_time
            article_generation_duration.labels(source=source).observe(duration)

            return result

        except Exception as e:
            # Record error
            article_generation_count.labels(
                status='error',
                source=source
            ).inc()

            logger.error(f"Article generation failed: {str(e)}")
            raise

    return wrapper


def track_news_fetch(func: Callable) -> Callable:
    """
    Decorator to track news fetching.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        source = kwargs.get('source', 'unknown')

        try:
            result = await func(*args, **kwargs)

            # Record success
            news_fetch_count.labels(
                source=source,
                status='success'
            ).inc()

            return result

        except Exception as e:
            # Record error
            news_fetch_count.labels(
                source=source,
                status='error'
            ).inc()

            logger.error(f"News fetch failed: {str(e)}")
            raise

    return wrapper


def track_wechat_api(func: Callable) -> Callable:
    """
    Decorator to track WeChat API calls.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        endpoint = kwargs.get('endpoint', 'unknown')

        try:
            result = await func(*args, **kwargs)

            # Record success
            wechat_api_calls.labels(
                endpoint=endpoint,
                status='success'
            ).inc()

            return result

        except Exception as e:
            # Record error
            wechat_api_calls.labels(
                endpoint=endpoint,
                status='error'
            ).inc()

            logger.error(f"WeChat API call failed: {str(e)}")
            raise

    return wrapper


def update_system_info(version: str, environment: str):
    """
    Update system information metrics.
    """
    system_info.info({
        'version': version,
        'environment': environment
    })


def get_metrics_summary() -> dict:
    """
    Get a summary of current metrics.
    """
    return {
        'total_requests': request_count._value.get(),
        'total_articles_generated': article_generation_count._value.get(),
        'total_news_fetched': news_fetch_count._value.get(),
        'total_wechat_calls': wechat_api_calls._value.get(),
        'active_tasks': active_tasks._value.get(),
    }