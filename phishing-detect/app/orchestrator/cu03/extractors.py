from __future__ import annotations
import re
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
DOMAIN_RE = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", re.I)
DAYS_RE = re.compile(r"\b(\d{1,3})\s*d[ií]as?\b", re.I)

def regex_extract(message: str) -> dict[str, Any]:
    key = (message or "").lower()
    patch: dict[str, Any] = {}

    rule_name = re.findall(r"'([^']*)'", key)
    if rule_name:
        patch["rule_name"] = rule_name[0]

    if "caduc" in key or "expir" in key:
        patch["rule_type"] = "expiry"
        patch["severity"] = "medium"
    elif "riesg" in key or "risk" in key:
        patch["rule_type"] = "risk"
    
    msg = DAYS_RE.search(message or "")
    if msg:
        patch["condition"] = {"days_before_expiry": int(msg.group(1))}

    em = EMAIL_RE.search(message or "")
    if em:
        patch["channels"] = [{"kind": "email", "to": em.group(0)}]

    doms = DOMAIN_RE.findall(message or "")
    if doms:
        patch["scope"] = {"target_type": "domains", "domains": sorted({d.lower() for d in doms})}

    if "diar" in key or "cada dia" in key or "todos los días" in key:
        patch["schedule"] = {"frequency": "daily"}
    elif "seman" in key:
        patch["schedule"] = {"frequency": "weekly"}

    if "no quiero cooldown" in key or "sin cooldown" in key:
        patch["cooldown"] = {"seconds": 0}

    return patch
