from __future__ import annotations
from typing import Literal, Union
from pydantic import BaseModel, Field

# Alcance/objetivos
class Scope(BaseModel):
    targets_type: Literal["all", "domains", "tags"]
    domain_ids: list[str] | None = None
    tags: list[str] | None = None


# Condiciones
class RiskCondition(BaseModel):
    kind: Literal["risk"] = "risk"
    risk_level_gte: Literal["low", "medium", "high", "critical"] | None = None
    risk_score_gte: int | None = Field(default=None, ge=0, le=100)
    risk_delta_gte: int | None = Field(default=None, ge=0, le=100)
    windows_hours: int = Field(default=24, ge=1, le=720)


class ExpiryCondition(BaseModel):
    kind: Literal["expiry"] = "expiry"
    days_before: int = Field(..., ge=1, le=3650)
    only_if_auto_renew_off: bool = False

Condition = Union[RiskCondition, ExpiryCondition]


# Frecuencia
class Schedule(BaseModel):
    frecuency: Literal["hourly", "daily", "weekly"]
    at_time: str | None = Field(default=None, description="HH:MM (requerido para daily/weekly)")
    timezone: str = "Europe/Madrid"
    days_of_week: list[Literal["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]] | None = None


# Canal de comunicacion
class Channel(BaseModel):
    king: Literal["email", "webhook", "in_app"]
    to: str | None = None
    template: Literal["default", "executive", "technical"] = "default"

# Tiempo espera entre comunicaciones
class Cooldown(BaseModel):
    hours: int = Field(default=24, ge=0, le=720)
    per_domain: bool = True


# Reglas
class AlertRuleDSL(BaseModel):
    dsl_version: str = Field(default="v1.0")
    name: str = Field(..., min_length=3, max_length=80)
    description: str | None = Field(default=None, max_length=240)

    rule_type: Literal["risk", "expiry"]
    enabled: bool = True
    severity: Literal["low", "medium", "high"] = "medium"

    scope: Scope
    condition: Condition
    schedule: Schedule
    channels: list[Channel] = Field(..., min_length=1, max_length=5)
    cooldown: Cooldown = Field(default_factory=Cooldown)


