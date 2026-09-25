"""Persist and query Tool execution summaries."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.agent.trace import ToolStep
from app.database.models import AgentTrace, ChatSession
from app.services.chat import ChatNotFoundError


class TraceEntry(BaseModel):
    session_id: str
    step_index: int
    tool_name: str
    tool_input: dict[str, Any]
    tool_output_summary: str
    status: str
    latency_ms: int
    created_at: datetime


def _entry(row: AgentTrace) -> TraceEntry:
    return TraceEntry(
        session_id=row.session_id,
        step_index=row.step_index,
        tool_name=row.tool_name,
        tool_input=row.tool_input,
        tool_output_summary=row.tool_output_summary,
        status=row.status,
        latency_ms=row.latency_ms,
        created_at=row.created_at,
    )


class TraceService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save_steps(self, session_id: str, steps: list[ToolStep]) -> None:
        if not steps:
            return
        with self._session_factory.begin() as session:
            offset = session.scalar(
                select(func.coalesce(func.max(AgentTrace.step_index), 0))
                .where(AgentTrace.session_id == session_id)
            ) or 0
            session.add_all([
                AgentTrace(
                    session_id=session_id,
                    step_index=offset + step.step_index,
                    tool_name=step.tool_name,
                    tool_input=step.tool_input,
                    tool_output_summary=step.tool_output_summary,
                    status=step.status,
                    latency_ms=step.latency_ms,
                )
                for step in steps
            ])

    def for_session(self, session_id: str) -> list[TraceEntry]:
        with self._session_factory() as session:
            if session.get(ChatSession, session_id) is None:
                raise ChatNotFoundError(session_id)
            rows = session.scalars(
                select(AgentTrace)
                .where(AgentTrace.session_id == session_id)
                .order_by(AgentTrace.step_index, AgentTrace.id)
            ).all()
            return [_entry(row) for row in rows]

    def recent(self, limit: int = 5) -> list[TraceEntry]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(AgentTrace).order_by(AgentTrace.id.desc()).limit(limit)
            ).all()
            return [_entry(row) for row in rows]
