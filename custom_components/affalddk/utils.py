"""Utils for the AffaldDK integration."""

import asyncio
from functools import wraps
from typing import Any
from collections.abc import Callable
import zoneinfo


def run_in_executor(func: Callable) -> Callable:
    """Run a blocking function in an executor using this decorator."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return wrapper


class AsyncSafeZoneInfo:
    """Async-safe wrapper for zoneinfo operations."""

    @staticmethod
    @run_in_executor
    def available_timezones() -> set[str]:
        """Get available timezones in an async-safe way."""
        return zoneinfo.available_timezones()

    @staticmethod
    @run_in_executor
    def get_timezone(key: str) -> zoneinfo.ZoneInfo:
        """Get a timezone in an async-safe way."""
        return zoneinfo.ZoneInfo(key)
