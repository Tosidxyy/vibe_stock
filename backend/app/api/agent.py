"""Agent chat endpoints; tool execution traces arrive in TODO phase 7."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, StringConstraints

from app.agent.service import AgentExecutionError, ModelNotConfiguredError, StockAgentService
from app.api.dependencies import get_agent_service
from app.services.chat import ChatNotFoundError

router = APIRouter(prefix="/api/agent", tags=["agent"])
AgentService = Annotated[StockAgentService, Depends(get_agent_service)]
Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class ChatRequest(BaseModel):
    message: Message
    session_id: UUID | None = None


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str


class ChatMessageResponse(BaseModel):
    role: str
    content: str


class ChatSessionResponse(BaseModel):
    session_id: UUID
    messages: list[ChatMessageResponse]


@router.get("/status")
def agent_status(agent: AgentService) -> dict[str, bool]:
    return {"configured": agent.configured}


@router.post("/chat", response_model=ChatResponse)
async def agent_chat(body: ChatRequest, agent: AgentService) -> ChatResponse:
    try:
        session_id, answer = await agent.chat(body.message, str(body.session_id) if body.session_id else None)
    except ModelNotConfiguredError:
        raise HTTPException(status_code=503, detail="Agent model is not configured") from None
    except ChatNotFoundError:
        raise HTTPException(status_code=404, detail="Chat session not found") from None
    except AgentExecutionError:
        raise HTTPException(status_code=502, detail="Agent model request failed") from None
    return ChatResponse(session_id=UUID(session_id), answer=answer)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: UUID, agent: AgentService) -> ChatSessionResponse:
    try:
        messages = await agent.messages(str(session_id))
    except ChatNotFoundError:
        raise HTTPException(status_code=404, detail="Chat session not found") from None
    return ChatSessionResponse(
        session_id=session_id,
        messages=[ChatMessageResponse(role=item.role, content=item.content) for item in messages],
    )
