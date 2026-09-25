"""FastAPI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.database.session import create_database_engine, create_session_factory, init_db
from app.providers.base import MarketDataProvider
from app.providers.eastmoney import EastMoneyProvider
from app.providers.exceptions import DataSourceError, InvalidSymbolError, ProviderTimeoutError
from app.services.market import MarketService
from app.services.stock import StockService
from app.services.watchlist import WatchlistService


def create_app(
    *, provider: MarketDataProvider | None = None, database_url: str | None = None
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = create_database_engine(database_url)
        owns_provider = provider is None
        data_provider = provider if provider is not None else EastMoneyProvider()
        try:
            init_db(engine)
            application.state.stock_service = StockService(data_provider)
            application.state.market_service = MarketService(data_provider)
            application.state.watchlist_service = WatchlistService(create_session_factory(engine))
            yield
        finally:
            if owns_provider:
                await data_provider.aclose()
            engine.dispose()

    application = FastAPI(title=get_settings().app_name, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )
    application.include_router(router)

    @application.exception_handler(ProviderTimeoutError)
    async def provider_timeout(_request: Request, _exc: ProviderTimeoutError) -> JSONResponse:
        return JSONResponse(status_code=504, content={"detail": "Market data provider timed out"})

    @application.exception_handler(DataSourceError)
    async def data_source_error(_request: Request, _exc: DataSourceError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "Market data temporarily unavailable"})

    @application.exception_handler(InvalidSymbolError)
    async def invalid_symbol(_request: Request, _exc: InvalidSymbolError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": "Invalid stock symbol"})

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
