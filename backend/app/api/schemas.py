"""REST response and request envelopes."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.models.market import MarketIndex

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    data: T
    stale: bool = False


class MarketOverviewResponse(BaseModel):
    indices: list[MarketIndex]
    watchlist_count: int
    stale: bool = False


class WatchlistAddRequest(BaseModel):
    symbol: str = Field(pattern=r"^[03468][0-9]{5}$")
