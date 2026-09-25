"""Persistent watchlist operations."""

from datetime import datetime
import re

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import WatchlistItem


class WatchlistEntry(BaseModel):
    symbol: str
    added_at: datetime


def _validate_symbol(symbol: str) -> str:
    if not isinstance(symbol, str) or re.fullmatch(r"[03468][0-9]{5}", symbol) is None:
        raise ValueError("symbol must be a six-digit A-share code")
    return symbol


def _entry(item: WatchlistItem) -> WatchlistEntry:
    return WatchlistEntry(symbol=item.symbol, added_at=item.created_at)


class WatchlistService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_entries(self) -> list[WatchlistEntry]:
        with self._session_factory() as session:
            items = session.scalars(select(WatchlistItem).order_by(WatchlistItem.id)).all()
            return [_entry(item) for item in items]

    def add(self, symbol: str) -> WatchlistEntry:
        symbol = _validate_symbol(symbol)
        with self._session_factory.begin() as session:
            item = session.scalar(select(WatchlistItem).where(WatchlistItem.symbol == symbol))
            if item is None:
                item = WatchlistItem(symbol=symbol)
                session.add(item)
                session.flush()
            return _entry(item)

    def remove(self, symbol: str) -> bool:
        symbol = _validate_symbol(symbol)
        with self._session_factory.begin() as session:
            item = session.scalar(select(WatchlistItem).where(WatchlistItem.symbol == symbol))
            if item is None:
                return False
            session.delete(item)
            return True
