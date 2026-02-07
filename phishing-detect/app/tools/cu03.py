from __future__ import annotations
import uuid
from typing import Any
from pydantic import ValidationError
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.dsl import AlertRuleDSL
from app.db.models import Domain, AlertRule, AlertRuleTarget, ScheduleJob

def list_domains(
        user_id: str,
        query: str | None = None,
        *,
        db: Session
) -> dict[str, Any]:
    sentencia = select(Domain).where(Domain.user_id == user_id)
    
    if query:
        q = query.lower().strip()
        sentencia = sentencia.where(Domain.domain_name.ilike(f"%{q}%"))
    
    rows = db.execute(sentencia).scalar().all()
    
    return {
        "domains": [
            {
                "domain_id": row.id,
                "domain_name": row.domain_name,
                "tags": row.tags or [],
                "status": row.status
            } for row in rows
        ]
    }


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
        return {"valid": False, "issues": issues, "requires_confirmation": False, "reason": ""}
    
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
        scope: dict[str, Any],
        *,
        db: Session,
) -> dict[str, Any]:
    target_type = scope.get("target_type")

    domains = list_domains(user_id, db=db)["domains"]

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
        resolved_scope: dict[str, Any] | None = None,
        *,
        db: Session,
) -> dict[str, Any]:
    # estimación simple (no hay domain_state real todavía)
    if not resolved_scope:
        resolved_scope = resolve_scope(user_id, rule_dsl.get("scope", {"target_type": "all"}), db=db).get("resolved_scope", {})
    
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
        rule_id: str | None = None,
        *,
        db: Session,
) -> dict[str, Any]:
    new_id = f"rule_{uuid.uuid4().hex[:8]}"
    name = rule_dsl.get("name", "Regla")
    rule_type = rule_dsl.get("rule_type", "risk")
    severity = rule_dsl.get("severity", "medium")
    enabled = bool(rule_dsl.get("enabled", True))

    logic_json = {
        "dsl_version": rule_dsl.get("dsl_version", "v1.0"),
        "rule_type": rule_type,
        "scope": rule_dsl.get("scope", {}),
        "condition": rule_dsl.get("condition", {}),
        "channels": rule_dsl.get("channels", []),
        "cooldown": rule_dsl.get("cooldown", {}),
        "dedup": rule_dsl.get("dedup", {}),
        "metadata": rule_dsl.get("metadata", {}),
    }

    schedule_json = rule_dsl.get("schedule", {})

    row = AlertRule(
        id=new_id,
        user_id=user_id,
        name=name,
        rule_type=rule_type,
        severity=severity,
        is_enabled=enabled,
        version=1,
        logic_json=logic_json,
        schedule_json=schedule_json,
    )

    db.add(row)
    db.commit()

    return {"rule_id": new_id, "version": 1, "created": True,}


def set_rule_targets(
        user_id: str,
        rule_id: str,
        resolved_scope: dict[str, Any],
        *,
        db: Session,
) -> dict[str, Any]:
    domain_ids = resolved_scope.get("domain_ids", [])

    # limpia targets previos
    db.execute(delete(AlertRuleTarget).where(AlertRuleTarget.rule_id == rule_id))

    for dom_id in domain_ids:
        db.add(AlertRuleTarget(rule_id=rule_id, domain_id=dom_id))
    
    db.commit()

    return {"attached": {"target_type": "domains", "domain_ids_count": len(domain_ids)},}


def register_rule_schedule(
        user_id: str,
        rule_id: str,
        schedule: dict[str, Any],
        *,
        db: Session,
) -> dict[str, Any]:
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    row = ScheduleJob(
        id=job_id,
        user_id=user_id,
        rule_id=rule_id,
        schedule_json=schedule,
        status="active",
        next_run_at=None,
    )

    db.add(row)
    db.commit()
    
    return {"job_id": job_id, "next_run_at": "mock_next_run",}

