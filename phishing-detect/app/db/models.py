from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)        # dom_101
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    domain_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")    # active/inactive
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)         # ["marca","es"]

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "domain_name", name="uq_user_domain_name"),
        Index("idx_domains_user_status", "user_id", "status"),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)        
    user_id: Mapped[str] = mapped_column(String(80), index=True)

    name: Mapped[str] = mapped_column(String(80))
    rule_type: Mapped[str] = mapped_column(String(30))                  
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    version: Mapped[int] = mapped_column(Integer, default=1)
    logic_json: Mapped[dict] = mapped_column(JSONB)                     # condición, canales, cooldown, etc.
    schedule_json: Mapped[dict] = mapped_column(JSONB)                  # frequency/at_time/timezone/days_of_week

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    targets: Mapped[list["AlertRuleTarget"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_rules_user_enabled", "user_id", "is_enabled"),
        Index("idx_rules_user_type", "user_id", "rule_type"),
    )


class AlertRuleTarget(Base):
    __tablename__ = "alert_rule_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(80), ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)
    domain_id: Mapped[str] = mapped_column(String(80), ForeignKey("domains.id"), index=True)

    rule: Mapped["AlertRule"] = relationship(back_populates="targets")

    __table_args__ = (
        UniqueConstraint("rule_id", "domain_id", name="uq_rule_domain"),
    )


class ScheduleJob(Base):
    __tablename__ = "schedules"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)        # job_xxx
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    rule_id: Mapped[str] = mapped_column(String(80), ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True)

    schedule_json: Mapped[dict] = mapped_column(JSONB)                  # copia del schedule del DSL
    status: Mapped[str] = mapped_column(String(20), default="active")   # active/paused

    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_sched_user_status", "user_id", "status"),
    )
