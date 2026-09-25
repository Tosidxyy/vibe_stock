"""The provider contract consumed by future services."""

from abc import ABC, abstractmethod
from typing import Literal, Sequence

from app.models.market import KlineItem, MarketIndex, StockQuote, SymbolSearchResult


class MarketDataProvider(ABC):
    @abstractmethod
    async def search_stocks(self, query: str, limit: int = 20) -> list[SymbolSearchResult]: ...

    @abstractmethod
    async def get_quotes(self, symbols: Sequence[str]) -> list[StockQuote]: ...

    @abstractmethod
    async def get_indices(self) -> list[MarketIndex]: ...

    @abstractmethod
    async def get_kline(
        self, symbol: str, period: Literal["daily", "weekly"] = "daily", limit: int = 120
    ) -> list[KlineItem]: ...
