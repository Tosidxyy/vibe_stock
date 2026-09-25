from uuid import uuid4

import pytest
from sqlalchemy import inspect, select

from app.database.models import AgentTrace, ChatMessage, ChatSession
from app.database.session import create_database_engine, create_session_factory, init_db
from app.services.watchlist import WatchlistService


def _database(tmp_path):
    engine = create_database_engine(f"sqlite:///{(tmp_path / 'stockpilot.db').as_posix()}")
    init_db(engine)
    return engine, create_session_factory(engine)


def test_watchlist_add_list_remove_and_persistence(tmp_path) -> None:
    engine, factory = _database(tmp_path)
    service = WatchlistService(factory)
    try:
        assert service.list_entries() == []
        first = service.add("600519")
        assert first.symbol == "600519"
        assert first.added_at is not None
        assert service.add("600519").symbol == "600519"
        service.add("000001")
        assert [item.symbol for item in service.list_entries()] == ["600519", "000001"]
        assert WatchlistService(create_session_factory(engine)).list_entries()[0].symbol == "600519"
        assert service.remove("600519")
        assert not service.remove("600519")
        assert [item.symbol for item in service.list_entries()] == ["000001"]
        for invalid in ("60051", "900901", "１２３４５６"):
            with pytest.raises(ValueError):
                service.add(invalid)
    finally:
        engine.dispose()


def test_v01_tables_and_chat_foreign_key_cascade(tmp_path) -> None:
    engine, factory = _database(tmp_path)
    try:
        assert {"watchlist", "chat_session", "chat_message", "agent_trace"} <= set(inspect(engine).get_table_names())
        session_id = str(uuid4())
        with factory.begin() as session:
            session.add(ChatSession(id=session_id, title="测试"))
            session.flush()
            session.add(ChatMessage(session_id=session_id, role="user", content="你好"))
            session.add(AgentTrace(
                session_id=session_id, step_index=0, tool_name="get_watchlist",
                tool_input={}, tool_output_summary="1 item", status="ok", latency_ms=12,
            ))
        with factory.begin() as session:
            assert len(session.scalars(select(ChatMessage)).all()) == 1
            assert len(session.scalars(select(AgentTrace)).all()) == 1
            session.delete(session.get(ChatSession, session_id))
        with factory() as session:
            assert session.scalars(select(ChatMessage)).all() == []
            assert session.scalars(select(AgentTrace)).all() == []
    finally:
        engine.dispose()
