"""Bounded fresh and stale caches for provider results."""

from collections.abc import Awaitable, Callable, Hashable
from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, TypeVar

from cachetools import TTLCache

from app.providers.exceptions import DataSourceError

T = TypeVar("T")


@dataclass(frozen=True)
class CachedResult(Generic[T]):
    data: T
    stale: bool = False


class AsyncTTLStore(Generic[T]):
    def __init__(
        self,
        *,
        ttl: float,
        stale_ttl: float = 3600,
        maxsize: int = 256,
        timer: Callable[[], float] | None = None,
    ) -> None:
        if ttl <= 0 or stale_ttl <= ttl or maxsize <= 0:
            raise ValueError("cache TTL and capacity must be positive; stale_ttl must exceed ttl")
        kwargs = {"timer": timer} if timer is not None else {}
        self._fresh: TTLCache[Hashable, T] = TTLCache(maxsize=maxsize, ttl=ttl, **kwargs)
        self._stale: TTLCache[Hashable, T] = TTLCache(maxsize=maxsize, ttl=stale_ttl, **kwargs)

    async def get(self, key: Hashable, loader: Callable[[], Awaitable[T]]) -> CachedResult[T]:
        if key in self._fresh:
            return CachedResult(deepcopy(self._fresh[key]))
        try:
            data = await loader()
        except DataSourceError:
            if key in self._stale:
                return CachedResult(deepcopy(self._stale[key]), stale=True)
            raise
        self._fresh[key] = deepcopy(data)
        self._stale[key] = deepcopy(data)
        return CachedResult(deepcopy(data))
