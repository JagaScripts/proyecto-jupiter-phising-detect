from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.storage.audit_store import read_audit_trace

router = APIRouter()

class AuditItem(BaseModel):
    """ Campos que va a tener cada elemento de la auditoría """
    ts_utc: int
    trace_id: str
    user_id: str | None = None
    session_id: str | None = None
    event: str
    payload: dict = Field(default_factory=dict)

class AuditResponse(BaseModel):
    """ Campos de respuesta cuando se requiere un elemento """
    trace_id: str
    items: list[dict] = Field(default_factory=list)

@router.get("/audit/{trace_id}", response_model=AuditResponse)
def get_audit(trace_id: str) -> AuditResponse:
    """
    Obtiene los eventos relacionados con una petición (trace_id)

    Args:
        trace_id: Identificador creado al realizar la petición

    Return:
        Elementos relacionados con la petición
    """
    items = read_audit_trace(trace_id=trace_id, limit=500)
    
    return AuditResponse(trace_id=trace_id, items=items)
