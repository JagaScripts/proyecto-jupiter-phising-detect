from __future__ import annotations
import json
from typing import Any
from openai import OpenAI

from app.core.logging import get_logger, log_event
from app.core.settings import settings

from app.orchestrator.router import route_message
from app.orchestrator.cu03.handler import handle_cu03
from app.storage.rule_draft_store import get_rule_draft

logger = get_logger("orchestrator.engine")

def run_orchestrator(user_id: str, session_id: str, message: str, model: str) -> dict[str, Any]:
    """
    Orquestador determinista que usa:
    - La función router para decidir el caso de uso
    - La función handler para ejecutar el flujo
    - El LLM solo se usa como extractor cuando haga falta, no toma decisiones

    Args:
        user_id (str): Identificador del usuario que realiza la petición.
        session_id (str): Identificador de la sesión
        message (str): Mensaje en lenguaje natural del usuario.
        model (str): Modelo de OpenAI a utilizar.

    Returns:
        dict[str, Any]: Resultado con el mensaje final para el usuario y el id bruto de la respuesta.
    """
    # Comprobamos si hay algun borrador activo para el usuario y sesión
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = (draft_entry or {}).get("draft", {}) if isinstance(draft_entry, dict) else {}
    
    decision = route_message(message)

    in_cu03_flow = (
        draft.get("_active_cu") == "CU-03"
        or bool(draft.get("_pending_fields"))
        or bool(draft.get("_awaiting_confirmation")) 
    )

    if in_cu03_flow and decision.cu != "CU-03":
        # Reescribe decision para mantener CU-03
        decision = type(decision)(
            cu="CU-03",
            confidence=1.0,
            reason="sticky_cu03: sesión con draft/pending_fields activo",
        )
    
    log_event(
        logger,
        level=20,
        event="orchestrator_start",
        message="Inicia el orquestador",
        extra={"model": model, "cu": decision.cu},
    )

    log_event(
        logger,
        level=20,
        event="router_decision",
        message="Decisión de routing",
        extra={
            "cu": decision.cu,
            "confidence": decision.confidence,
            "reason": decision.reason,
        },
    )

    client = OpenAI(api_key=settings.openai_api_key, timeout=30.0, max_retries=1)
    
    if decision.cu == "CU-03":
        result = handle_cu03(
            user_id=user_id,
            session_id=session_id,
            message=message,
            model=model,
            client=client,
        )
    else:
        result = {
            "final_user_message": "Caso de uso no implementado:", "cu": decision.cu,
        }
    
    log_event(
        logger,
        level=20,
        event="orchestrator_end",
        message="Finalizado el orquestador",
        extra={"cu": decision.cu},
    )

    return result