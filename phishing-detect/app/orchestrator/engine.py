from __future__ import annotations
import json
from typing import Any, Callable
from openai import OpenAI
from app.tools import cu03 as cu03_tools
from app.core.logging import trace_id_ctx, user_id_ctx, session_id_ctx, get_logger, log_event
from app.storage.audit_store import write_audit_event
from app.db.session import SessionLocal
from app.core.settings import settings

logger = get_logger("orchestrator.engine")

ToolFn = Callable[..., dict[str, Any]]


def _tool_registry() -> dict[str, Any]:
    return {
        "list_domains": cu03_tools.list_domains,
        "validate_alert_rule_dsl": cu03_tools.validate_alert_rule_dsl,
        "resolve_scope": cu03_tools.resolve_scope,
        "preview_rule_effect": cu03_tools.preview_rule_effect,
        "upsert_alert_rule": cu03_tools.upsert_alert_rule,
        "set_rule_targets": cu03_tools.set_rule_targets,
        "register_rule_schedule": cu03_tools.register_rule_schedule,
    }


def _tools_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": "list_domains",
            "description": "Lista los dominios del usuario (para resolver el alcance/scope)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "query": {"type": "string"}
                },
                "required": ["user_id"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "validate_alert_rule_dsl",
            "description": "Validar AlertRuleDSL (schema + reglas negocio) y normalizar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "rule_dsl": {"type": "object"}
                },
                "required": ["user_id", "rule_dsl"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "resolve_scope",
            "description": "Resolver el scope (all/domains/tags) a ids de dominio concretos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "scope": {"type": "object"}
                },
                "required": ["user_id", "scope"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "preview_rule_effect",
            "description": "Previsualizar impacto de la regla (alcance y triggers estimados).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "rule_dsl": {"type": "object"},
                    "resolved_scope": {"type": "object"}
                },
                "required": ["user_id", "rule_dsl"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "upsert_alert_rule",
            "description": "Crear/actualizar regla (MVP: create).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "rule_dsl": {"type": "object"},
                    "mode": {"type": "string", "enum": ["create", "update", "upsert"]},
                    "rule_id": {"type": "string"}
                },
                "required": ["user_id", "rule_dsl"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "set_rule_targets",
            "description": "Asociar targets (domain_ids) a una regla.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "rule_id": {"type": "string"},
                    "resolved_scope": {"type": "object"}
                },
                "required": ["user_id", "rule_id", "resolved_scope"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "register_rule_schedule",
            "description": "Registrar el schedule (scheduler).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "rule_id": {"type": "string"},
                    "schedule": {"type": "object"}
                },
                "required": ["user_id", "rule_id", "schedule"],
                "additionalProperties": False,
            },
        },
    ]


ORCH_INSTRUCTIONS = """Eres el agente orquestador de un chatbot detector de phishing.
Tarea principal: configurar alertas CU-03 en lenguaje natural.
Reglas:
- Si falta información crítica (scope/canales/frecuencia/umbrales), pregunta al usuario, NO inventes.
- Antes de persistir, SIEMPRE llama validate_alert_rule_dsl.
- Para aplicar la regla a dominios/tags/all, usa resolve_scope y set_rule_targets.
- Registra el schedule con register_rule_schedule.
- Devuelve una confirmación clara al usuario: qué regla, alcance, frecuencia, canal y cooldown.
"""

_DB_TOOLS = {
    "list_domains",
    "resolve_scope",
    "preview_rule_effect",
    "upsert_alert_rule",
    "set_rule_targets",
    "register_rule_schedule",
}

def run_orchestrator(user_id: str, message: str, model: str) -> dict[str, Any]:
    client = OpenAI(api_key=settings.openai_api_key, timeout=30.0, max_retries=1)
    tools = _tools_schema()
    registry = _tool_registry()

    input_list: list[dict[str, Any]] = [{"role": "user", "content": f"[user_id={user_id}] {message}"}]

    log_event(
        logger,
        level=20,
        event="orchestrator_start",
        message="Inicia el orquestador",
        extra={"model": model, "cu": "CU-03"},
    )

    write_audit_event(
        trace_id=trace_id_ctx.get(),
        user_id=user_id_ctx.get(),
        session_id=session_id_ctx.get(),
        event="orchestrator_start",
        payload={"model": model, "cu": "CU-03"},
    )

    db = SessionLocal()

    try:
        response = client.responses.create(
            model=model,
            instructions=ORCH_INSTRUCTIONS,
            tools=tools,
            input=input_list,
        )

        # Loop: ejecutar tool calls hasta que el modelo deje de pedir tools
        while True:
            # Añade TODOS los items output al input (convertidos a dict)
            if getattr(response, "output", None):
                input_list += [item.model_dump() for item in response.output]

            tool_calls = [item for item in getattr(response, "output", [])
                        if item.type == "function_call"]
            
            if not tool_calls:
                break

            log_event(
                logger,
                level=20,
                event="tool_calls_detected",
                message="Detectadas Tool Calls",
                extra={"count": len(tool_calls), "tools": [call.name for call in tool_calls]},
            )

            write_audit_event(
                trace_id=trace_id_ctx.get(),
                user_id=user_id_ctx.get(),
                session_id=session_id_ctx.get(),
                event="tool_calls_detected",
                payload={"count": len(tool_calls), "tools": [call.name for call in tool_calls]},
            )
            
            for call in tool_calls:
                name = call.name
                args = json.loads(call.arguments or {})
                fn = registry.get(name)

                log_event(
                    logger,
                    level=20,
                    event="tool_calls_execute",
                    message="Ejecutando Tool Call",
                    extra={"tool": name, "args": args},
                )

                write_audit_event(
                    trace_id=trace_id_ctx.get(),
                    user_id=user_id_ctx.get(),
                    session_id=session_id_ctx.get(),
                    event="tool_call_execute",
                    payload={"tool": name, "args": args},
                )                

                if fn is None:
                    tool_result = {
                        "error": "tool_not_found",
                        "message": f"Tool '{name}' no registrada"
                    }
                else:
                    try:
                        if name in _DB_TOOLS:
                            tool_result = fn(**args, db=db)
                        else:
                            tool_result = fn(**args)
                    except Exception as e:
                        tool_result = {"error": "tool_exception", "message": str(e)}
                
                log_event(
                    logger,
                    level=20,
                    event="tool_call_result",
                    message="Resultado de la Tool ejecutada",
                    extra={"tool": name, "result": tool_result},
                )

                write_audit_event(
                    trace_id=trace_id_ctx.get(),
                    user_id=user_id_ctx.get(),
                    session_id=session_id_ctx.get(),
                    event="tool_call_result",
                    payload={"tool": name, "result": tool_result},
                )

                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

            response = client.responses.create(
                model=model,
                instructions=ORCH_INSTRUCTIONS,
                tools=tools,
                input=input_list,
            )
        
        final_text = getattr(response, "output_text", "") or "No se ha podido generar respuesta"
        
        log_event(
            logger,
            level=20,
            event="orchestrator_end",
            message="Finalizado el Orquestador",
            extra={"response_id": getattr(response, "id", None)},
        )

        write_audit_event(
            trace_id=trace_id_ctx.get(),
            user_id=user_id_ctx.get(),
            session_id=session_id_ctx.get(),
            event="orchestrator_end",
            payload={"response_id": getattr(response, "id", None), "cu": "CU-03"},
        )

        return {"final_user_message": final_text, "raw_response_id": getattr(response, "id", None)}
    
    finally:
        db.close()