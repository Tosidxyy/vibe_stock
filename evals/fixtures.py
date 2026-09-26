"""Deterministic market data for model evaluations, not live market quotes."""

from datetime import date
from typing import Literal, Sequence

from app.models.market import IntradayPoint, KlineItem, MarketIndex, StockQuote, SymbolSearchResult
from app.providers.base import MarketDataProvider


STOCKS = {
    "300750": ("宁德时代", 251.30, 1.72),
    "002594": ("比亚迪", 108.60, -0.80),
    "300059": ("东方财富", 24.60, 2.40),
    "600519": ("贵州茅台", 1680.00, 0.60),
    "000001": ("平安银行", 12.30, -0.40),
}


class EvalProvider(MarketDataProvider):
    async def search_stocks(self, query: str, limit: int = 20) -> list[SymbolSearchResult]:
        return [
            SymbolSearchResult(symbol=symbol, name=name, market="SH" if symbol.startswith("6") else "SZ")
            for symbol, (name, _, _) in STOCKS.items()
            if query in name or query in symbol
        ][:limit]

    async def get_quotes(self, symbols: Sequence[str]) -> list[StockQuote]:
        return [
            StockQuote(
                symbol=symbol, name=STOCKS[symbol][0], price=STOCKS[symbol][1],
                change_percent=STOCKS[symbol][2], change_amount=1.0, volume=100000,
                turnover=1000000.0, high=STOCKS[symbol][1] + 2,
                low=STOCKS[symbol][1] - 2, open=STOCKS[symbol][1] - 1,
                previous_close=STOCKS[symbol][1] - 1, turnover_rate=1.0, pe_ratio=20.0,
            )
            for symbol in symbols if symbol in STOCKS
        ]

    async def get_indices(self) -> list[MarketIndex]:
        return [
            MarketIndex(symbol="000001", name="上证指数", value=3000.0,
                        change_percent=1.0, change_amount=30.0, volume=100000,
                        turnover=2000000.0),
            MarketIndex(symbol="399001", name="深证成指", value=10000.0,
                        change_percent=-0.5, change_amount=-50.0, volume=100000,
                        turnover=2000000.0),
            MarketIndex(symbol="399006", name="创业板指", value=2000.0,
                        change_percent=0.8, change_amount=16.0, volume=100000,
                        turnover=2000000.0),
        ]

    async def get_index_intraday(self, index_code: str = "000001") -> list[IntradayPoint]:
        return []

    async def get_kline(
        self, symbol: str, period: Literal["daily", "weekly"] = "daily", limit: int = 120
    ) -> list[KlineItem]:
        if symbol not in STOCKS:
            return []
        price = STOCKS[symbol][1]
        return [
            KlineItem(date=date(2026, 9, 25 - index), open=price - 1,
                      close=price, high=price + 2, low=price - 2,
                      volume=100000, turnover=1000000.0)
            for index in range(min(limit, 5))
        ]
