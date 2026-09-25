"""FastAPI entry point."""

from fastapi import FastAPI

from app.core.config import get_settings

app = FastAPI(title=get_settings().app_name)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
