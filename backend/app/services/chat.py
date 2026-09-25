"""Store visible Agent conversations; tool traces are handled in a later stage."""

from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import ChatMessage, ChatSession


class ChatNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class ChatService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def messages(self, session_id: str) -> list[ChatTurn]:
        with self._session_factory() as session:
            if session.get(ChatSession, session_id) is None:
                raise ChatNotFoundError(session_id)
            rows = session.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.id)
            ).all()
            return [ChatTurn(role=row.role, content=row.content) for row in rows]

    def save_exchange(self, session_id: str | None, prompt: str, answer: str) -> str:
        with self._session_factory.begin() as session:
            if session_id is None:
                session_id = str(uuid4())
                session.add(ChatSession(id=session_id, title=prompt[:200]))
                session.flush()
            elif session.get(ChatSession, session_id) is None:
                raise ChatNotFoundError(session_id)
            session.add_all([
                ChatMessage(session_id=session_id, role="user", content=prompt),
                ChatMessage(session_id=session_id, role="assistant", content=answer),
            ])
        return session_id
