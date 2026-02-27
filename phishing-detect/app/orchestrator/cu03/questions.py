from __future__ import annotations
from typing import Any

def build_question_for_missing(draft: dict[str, Any], missing: list[str]) -> str:
    # pregunta 1-2 cosas máximo para UX
    m=missing[0]

    rule_type = draft.get("rule_type")
    scope = draft.get("scope") or {}
    channels = draft.get("channels") or []
    schedule = draft.get("schedule") or {}

    # helpers
    domains = scope.get("domains") or []
    email = None
    if channels and isinstance(channels, list):
        for ch in channels:
            if isinstance(ch, dict) and ch.get("kind") == "email" and ch.get("to"):
                email = ch["to"]
                break
    
    if m == "rule_name":
        return "Hace falta un nombre para la alerta. Pon el nombre de la alerta entre comillas simples. Ej: 'Alerta Dominio'"

    if m == "rule_type":
        return "¿La alerta es por **caducidad** del dominio o por **riesgo**?"

    if m == "condition":
        if rule_type == "expiry":
            dom_txt = f" para **{domains[0]}**" if domains else ""
            return f"¿Cuántos días antes de la caducidad quieres el aviso{dom_txt}? (ej: 15 días)"
        if rule_type == "risk":
            return "¿Qué condición de riesgo quieres? (ej: 'riesgo alto' o 'score >= 80')"
        return "¿Cuál es la condición exacta? (ej: '15 días antes de caducar' o 'riesgo alto')"

    if m == "channels":
        if email:
            return f"Ya tengo el email **{email}**. ¿Quieres añadir otro canal o confirmo ese?"
        return "¿A qué email debo notificarte? (ej: soc@dominio.com)"

    if m == "scope":
        if domains:
            return f"Ya tengo el dominio **{domains[0]}**. ¿Aplica solo a ese o a más dominios?"
        return "¿Aplica a todos tus dominios o a alguno concreto? (ej: acme.es)"

    if m == "schedule":
        freq = schedule.get("frequency") or schedule.get("frecuency")
        if freq:
            return f"Ya tengo frecuencia **{freq}**. ¿A qué hora quieres el aviso? (ej: 09:00)"
        return "¿Con qué frecuencia quieres el aviso? (diaria/semanal)"

    return "Necesito un dato más para crear la alerta. ¿Puedes indicármelo?"