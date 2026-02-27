from __future__ import annotations

import re
from dataclasses import dataclass

@dataclass
class RouteDecision:
    cu: str
    confidence: float
    reason: str

def route_message(text: str) -> RouteDecision:
    key = (text or "").lower()

    # CU-03 alertas caducidad/riesgo
    pattern = r"\b(alerta|avis(?:a|ame)|notific\w*|caduc\w*|expir\w*|riesgo)\b"
    if re.search(pattern, key, re.IGNORECASE):
        return RouteDecision(cu="CU-03", confidence=0.9, reason="keyword_match")
    
    # Default: soporte
    return RouteDecision(cu="CU-07", confidence=0.3, reason="default_fallback")