from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time
import uuid

@dataclass
class MemoryDB:
    rules: dict[str, dict[str, Any]] = field(default_factory=dict)
    rule_targets: dict[str, list[str]] = field(default_factory=dict)
    schedules: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create_rule(
            self, 
            user_id: str,
            rule: dict[str, Any]
    ) -> str:
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        self.rules[rule_id] = {
            "rule_id": rule_id,
            "user_id": user_id,
            "rule": rule,
            "created_at": int(time.time()),
            "version": 1,
        }
        
        return rule_id
    
    def set_targets(
            self,
            rule_id: str,
            domain_ids: list[str]
    ) -> None:
        self.rule_targets[rule_id] = list(domain_ids)

    def register_schedule(
            self,
            rule_id: str,
            schedule: dict[str, Any]
    ) -> str:
        job_id = F"job_{uuid.uuid4().hex[:8]}"
        self.schedules[job_id] = {
            "job_id": job_id,
            "rule_id": rule_id,
            "schedule": schedule
        }

        return job_id
    
MEM_DB = MemoryDB()