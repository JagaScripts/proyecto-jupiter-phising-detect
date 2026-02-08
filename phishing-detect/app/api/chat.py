from __future__ import annotations
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.orchestrator.engine import run_orchestrator
from app.api.orchestrator import settings as orch_settings

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=80)
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=120)


class ChatResponse(BaseModel):
    session_id: str
    trace_id: str
    assistant_message: str


# Endpoint para interactuar con el chat
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Funcion para interactuar con el agente orquestador

    Args:
        req: Elemento de la clase ChatRequest que lleva el user_id, el mensaje del usuario y el session_id

    Return:
        Devuelve la contestación del agente orquestador, el session_id y trace_id
    """
    trace_id = "trace_dummy_001"
    session_id = req.session_id or "sess_dummy_001"

    out = run_orchestrator(user_id=req.user_id, message=req.message, model=orch_settings.openai_model)

    return ChatResponse(
        session_id=session_id,
        trace_id = trace_id,
        assistant_message=out["final_user_message"],
    )

