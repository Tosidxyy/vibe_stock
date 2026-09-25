"""Request-scoped access to application services."""

from fastapi import Request

from app.services.market import MarketService
from app.services.stock import StockService
from app.services.watchlist import WatchlistService


def get_stock_service(request: Request) -> StockService:
    return request.app.state.stock_service


def get_market_service(request: Request) -> MarketService:
    return request.app.state.market_service


def get_watchlist_service(request: Request) -> WatchlistService:
    return request.app.state.watchlist_service
