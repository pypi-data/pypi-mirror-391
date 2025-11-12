from __future__ import annotations

import collections.abc
import logging
import typing

from structlog import DropEvent
from structlog.typing import EventDict

from .throttlers import CountThrottler, ThrottlerProtocol, TimeThrottler

__all__ = [
    "LogThrottler",
    "LogTimeThrottler",
    "CountThrottler",
]


class LogThrottlerProtocol(typing.Protocol):
    key: tuple[str, ...]
    throttler: ThrottlerProtocol

    def __call__(self, _: logging.Logger, __: str, event_dict: EventDict) -> EventDict:
        key = tuple(event_dict[k] for k in self.key)

        if self.throttler.is_throttled(key):
            raise DropEvent

        return event_dict


class LogThrottler(LogThrottlerProtocol):
    """Drop logs when throttled based on *throttler*.

    This should generally be close to the top of your processor chain so that a log that
    will ultimately be throttled is not processed further.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        throttler:
            A ``ThrottlerProtocol`` implementation to decide if *key should be
            throttled.
    """

    def __init__(
        self,
        key: str | collections.abc.Iterable[str],
        throttler: ThrottlerProtocol,
    ):
        self.key = (key,) if isinstance(key, str) else tuple(key)
        self.throttler = throttler


class LogTimeThrottler(LogThrottlerProtocol):
    """Drop logs when throttled based on time in between calls.

    This is a convinience class to initialize a ``LogThrottler`` with a
    ``TimeThrottler``.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        every_seconds: How long to throttle logs for, in seconds.
    """

    def __init__(
        self, key: str | collections.abc.Iterable[str], every_seconds: int | float
    ) -> None:
        self.key = (key,) if isinstance(key, str) else tuple(key)
        self.throttler = TimeThrottler(every_seconds)


class LogCountThrottler(LogThrottlerProtocol):
    """Drop logs when throttled based on the number of times *key* was in a log call.

    This is a convinience class to initialize a ``LogThrottler`` with a
    ``CountThrottler``.

    Args:
        key: Unique key in the *event_dict* to determine if log should be throttled.
        every_calls: Only allow logging every *every* times.
    """

    def __init__(self, key: str | collections.abc.Iterable[str], every: int) -> None:
        self.key = (key,) if isinstance(key, str) else tuple(key)
        self.throttler = CountThrottler(every)
