from __future__ import annotations
from typing import Any
from pydantic import ValidationError
from app.models.dsl import AlertRuleDSL
from app.storage.memory import MEM_DB

def list_domains(
        user_id: str,
        query: str | None = None
) -> dict[str, Any]:

    domains = [
        {"domain_id": "dom_101", "domain_name": "prueba1.com", "tags": ["marca"], "status": "active"},
        {"domain_id": "dom_205", "domain_name": "prueba2.es", "tags": ["marca", "es"], "status": "active"},
        {"domain_id": "dom_777", "domain_name": "prueba3-dev.com", "tags": ["dev"], "status": "inactive"},
    ]

    if query:
        q = query.lower().strip()
        domains = [domain for domain in domains if q in domain["domain_name"]]
    
    return {"domains": domains}


def validate_alert_rule_dsl(
        user_id: str,
        rule_dsl: dict[str, Any]
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    try:
        parsed = AlertRuleDSL.model_validate(rule_dsl)
    except ValidationError as e:
        for error in e.errors():
            issues.append(
                {
                    "field": ".".join(str(err) for err in error.get("loc", [])),
                    "code": error.get("type", "validation_error"),
                    "message": error.get("msg", "invalid"),
                    "severity": "error",
                }
            )
        return {"valid": False, "issues": issues, "requires_confirmation": False, "reason": "",}
    
    requires_confirmation = False
    reason = ""

    scope_all = parsed.scope.targets_type == "all"
    external = any(channel.kind in ("email", "webhook") for channel in parsed.channels)
    very_frecuent = parsed.schedule.frecuency == "hourly"
    if scope_all and external and very_frecuent:
        requires_confirmation = True
        reason = "Impacto alto: scope=all + canal externo + evaluación hourly"

    normalized = parsed.model_dump()
    if parsed.schedule.frecuency in ("daily", "weekly") and not parsed.schedule.at_time:
        normalized["schedule"]["at_time"] = "09:00"

    return {
        "valid": True,
        "normalized_rule": normalized,
        "issues": [],
        "requires_confirmation": requires_confirmation,
        "reason": reason,
    }


def resolve_scope(
        user_id: str,
        scope: dict[str, Any]
) -> dict[str, Any]:
    target_type = scope.get("target_type")

    domains = list_domains(user_id)["domains"]

    if target_type == "all":
        domain_ids = [domain["domain_id"] for domain in domains if domain["status"] == "active"]
        return {
            "resolved_scope": {
                "target_type": "domains",
                "domain_ids": domain_ids,
                "stats":{"marched_domains": len(domain_ids)},
            }
        }
    
    if target_type == "domains":
        domain_ids = scope.get("domain_ids") or []
        return {
            "resolved_scope": {
                "target_type": "domains",
                "domain_ids": domain_ids,
                "stats":{"marched_domains": len(domain_ids)},
            }
        }
    
    if target_type == "tags":
        tags = set(scope.get("tags") or [])
        matched = [domain["domain_id"] for domain in domains if tags.intersection(set(domain.get("tags", []))) and domain["status"] == "active"]
        return {
            "resolved_scope": {
                "target_type": "domains",
                "domain_ids": matched,
                "stats":{"marched_domains": len(matched)},
            }
        }
    
    return {"error": "validation_failed", "message": "scope.target_type inválido",}


def preview_rule_effect(
        user_id: str,
        rule_dsl: dict[str, Any],
        resolved_scope: dict[str, Any] | None = None
) -> dict[str, Any]:
    # estimación simple (no hay domain_state real todavía)
    if not resolved_scope:
        resolved_scope = resolve_scope(user_id, rule_dsl.get("scope", {"target_type": "all"})).get("resolved_scope", [])
    
    domain_ids = resolved_scope.get("domain_ids", [])

    return {
        "impact":{
            "domains_in_scope": len(domain_ids),
            "estimated_triggers_now": 0
        },
        "examples": [],
        "notes": ["Sin estado real, previsualización solo de alcance"],
    }


def upsert_alert_rule(
        user_id: str,
        rule_dsl: dict[str, Any],
        mode: str = "create",
        rule_id: str | None = None
) -> dict[str, Any]:
    new_rule_id = MEM_DB.create_rule(user_id, rule_dsl)
    return {"rule_id": new_rule_id, "version": 1, "created": True,}


def set_rule_targets(
        user_id: str,
        rule_id: str,
        resolved_scope: dict[str, Any]
) -> dict[str, Any]:
    domain_ids = resolved_scope.get("domain_ids", [])
    MEM_DB.set_targets(rule_id, domain_ids)
    return {"attached": {"target_type": "domains", "domain_ids_count": len(domain_ids)},}


def register_rule_schedule(
        user_id: str,
        rule_id: str,
        schedule: dict[str, Any]
) -> dict[str, Any]:
    job_id = MEM_DB.register_schedule(rule_id, schedule)
    return {"job_id": job_id, "next_run_at": "mock_next_run",}

