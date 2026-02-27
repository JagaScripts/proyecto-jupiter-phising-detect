from __future__ import annotations

import re
from typing import Any
from openai import OpenAI

from app.orchestrator.cu03.extractors import regex_extract
from app.orchestrator.cu03.questions import build_question_for_missing
from app.storage.rule_draft_store import get_rule_draft, upsert_rule_draft, clear_rule_draft
from app.tools.cu03 import (
    validate_alert_rule_dsl,
    resolve_scope,
    upsert_alert_rule,
    set_rule_targets,
    register_rule_schedule,
)
from app.db.session import SessionLocal

FIELD_ORDER = ["rule_type", "condition", "scope", "channels", "schedule", "rule_name"]


def _missing(draft: dict[str, Any]) -> list[str]:
    missing: list[str] = []

    rule_name = draft.get("rule_name")
    if not rule_name:
        missing.append("rule_name")
    
    rule_type = draft.get("rule_type")
    if not rule_type:
        missing.append("rule_type")

    condition = draft.get("condition") or {}
    if rule_type == "expiry":
        if not condition.get("days_before_expiry"):
            missing.append("condition")
    elif rule_type == "risk":
        if not condition.get("risk_level") and not condition.get("risk_score_gte"):
            missing.append("condition")
    else:
        if not condition:
            missing.append("condition")

    scope = draft.get("scope") or {}
    if not scope.get("domains") and not scope.get("domain_ids"):
        missing.append("scope")

    channels = draft.get("channels") or []
    has_email = any(
        isinstance(ch, dict) and ch.get("kind") == "email" and ch.get("to")
        for ch in channels
    )
    if not has_email:
        missing.append("channels")

    schedule = draft.get("schedule") or {}
    if not schedule.get("frequency"):
        missing.append("schedule")

    return [field for field in FIELD_ORDER if field in missing]

def _normalize_text(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def _is_yes(s: str) -> bool:
    s = _normalize_text(s)
    return s in {"si", "sí", "s", "ok", "vale", "confirmar", "confirmo", "crear", "crea", "adelante", "de acuerdo"} or (
        "confirm" in s or "crea" in s
    )


def _is_no(s: str) -> bool:
    s = _normalize_text(s)
    return s in {"no", "cancelar", "cancela", "anular", "anula", "parar"} or ("cancel" in s or "anul" in s)

def _build_confirmation_summary(draft: dict[str, Any]) -> str:
    rule_name = draft.get("rule_name")
    rule_type = draft.get("rule_type")
    condition = draft.get("condition") or {}
    scope = draft.get("scope") or {}
    schedule = draft.get("schedule") or {}
    channels = draft.get("channels") or []

    # Resumen legible sin asumir estructura interna compleja
    domains = scope.get("domains") or []
    freq = schedule.get("frequency")
    return (
        "Antes de crear la alerta, confirma que está todo correcto:\n\n"
        f"- Nombre: '{rule_name}'\n"
        f"- Tipo: {rule_type}\n"
        f"- Condición: {condition}\n"
        f"- Dominios: {domains}\n"
        f"- Frecuencia: {freq}\n"
        f"- Canales: {channels}\n\n"
        "Responde **sí** para crearla o **no** para cancelar."
    )

def handle_cu03(
        user_id: str,
        session_id: str,
        message: str,
        model: str,
        client: OpenAI,
) -> dict[str, Any]:
    #Borrador actual
    draft_entry = get_rule_draft(user_id=user_id, session_id=session_id)
    draft = draft_entry.get("draft", {}) or {}

    if draft.get("_awaiting_confirmation"):
        if _is_yes(message):
            upsert_rule_draft(
                user_id=user_id,
                session_id=session_id,
                patch={"_confirmed": True, "_awaiting_confirmation": False},
            )
            draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        elif _is_no(message):
            clear_rule_draft(user_id=user_id, session_id=session_id)
            return {"final_user_message": "Creación de alerta cancelada.", "cu": "CU-03"}
        else:
            # El usuario puede estar corrigiendo algo en vez de responder sí/no.
            patch = regex_extract(message)
            if patch:
                upsert_rule_draft(user_id=user_id, session_id=session_id, patch=patch)
                draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
                # Mantener confirmación pendiente y mostrar resumen actualizado
                upsert_rule_draft(
                    user_id=user_id,
                    session_id=session_id,
                    patch={"_awaiting_confirmation": True, "_confirmed": False},
                )
                draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
                return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

            return {
                "final_user_message": "¿Confirmas la creación? Responde **sí** para crear o **no** para cancelar.",
                "cu": "CU-03",
            }
    
    # Extracción por regex
    patch = regex_extract(message)
    if patch:
        upsert_rule_draft(user_id=user_id, session_id=session_id, patch=patch)
        draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}

    # si faltan campos preguntamos sin intervención del LLM
    missing = _missing(draft)
    if missing:
        asked = missing[:2]
        question = build_question_for_missing(draft=draft, missing=missing)
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={
                "_active_cu": "CU-03",
                "_pending_fields": asked,
                "_last_question_field": asked[0],
                "_awaiting_confirmation": False,
                "_confirmed": False,
            },
        )

        return {"final_user_message": question, "cu": "CU-03"}

    # Pipeline determinista
    with SessionLocal() as db:
        validated = validate_alert_rule_dsl(user_id=user_id, rule_dsl=draft)

        if not validated.get("valid"):
            issues = validated.get("issues") or []
            return {
                "final_user_message": f"No puedo crear la alerta aún. Problemas: {issues}",
                "cu": "CU-03",
            }
    
    if not draft.get("_confirmed"):
        upsert_rule_draft(
            user_id=user_id,
            session_id=session_id,
            patch={
                "_active_cu": "CU-03",
                "_awaiting_confirmation": True,
                "_confirmed": False,
            },
        )
        # refrescamos por si acaso
        draft = get_rule_draft(user_id=user_id, session_id=session_id).get("draft", {}) or {}
        return {"final_user_message": _build_confirmation_summary(draft), "cu": "CU-03"}

    with SessionLocal() as db:
        # Re-validar (por robustez) y usar normalized_rule
        validated = validate_alert_rule_dsl(user_id=user_id, rule_dsl=draft)
        if not validated.get("valid"):
            issues = validated.get("issues") or []
            return {
                "final_user_message": f"No puedo crear la alerta aún. Problemas: {issues}",
                "cu": "CU-03",
            }
        
        normalized = validated["normalized_rule"]

        rs = resolve_scope(user_id=user_id, scope=draft["scope"], db=db)
        if rs.get("missing_domains"):
            return {
                "final_user_message": f"No encuentro estos dominios en tu inventario: {rs['missing_domains']}. "
                                      f"¿Quieres darlos de alta o corregir el nombre?",
                "cu": "CU-03",
            }

        # se guarda la regla en la base de datos
        normalized["scope"]["domain_ids"] = rs.get("domain_ids", [])
        up = upsert_alert_rule(user_id=user_id, mode="create", rule_dsl=normalized, db=db)
        rule_id = up["rule_id"]

        # se guardan los targets y schedule
        set_rule_targets(user_id=user_id, rule_id=rule_id, session_id=session_id, resolved_scope=rs, db=db)
        register_rule_schedule(user_id=user_id, rule_id=rule_id, session_id=session_id, schedule=normalized["schedule"], db=db)
    
    clear_rule_draft(user_id=user_id, session_id=session_id)

    return {
        "final_user_message": f"Alerta creada (rule_id={rule_id}). Te avisaré según la configuración.",
        "cu": "CU-03",
        "rule_id": rule_id,
    }