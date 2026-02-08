from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from typing import Any

# Esta base de datos se guarda en SQLite para separarla de PostgreSQL, pudiendo registrar los fallos aunque falle el sistema
# Se usa getenv y no settings para que registre los eventos antes de que cargue settings.py
AUDIT_DB_PATH = os.getenv("AUDIT_DB_PATH", "./audit.db")
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() in ("1", "true", "yes", "y")

# bloqueo de sincronizacion para que varios hilos accedan al mismo tiempo a la base de datos
_lock = threading.Lock()

DDL = """
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc INTEGER NOT NULL,
  trace_id TEXT NOT NULL,
  user_id TEXT,
  session_id TEXT,
  event TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_trace_id ON audit_log(trace_id);
CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_log(event);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts_utc);
"""


def _connect() -> sqlite3.Connection:
    """Crea y devuelve una conexión a la base de datos SQLite de auditoría."""

    conn = sqlite3.connect(AUDIT_DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;") # Activa el modo de escritura eficiente
    conn.execute("PRAGMA synchronous=NORMAL;") # Reduce las esperas de escritura en disco para ganar rendimiento
    return conn


def init_audit_db() -> None:
    """
    Inicializa la base de datos de auditoría creando las tablas e índices si no existen.
    """

    if not AUDIT_ENABLED:
        return
    with _lock:
        conn = _connect()
        try:
            for sentencias in DDL.strip().split(";"):
                s = sentencias.strip()
                if s:
                    conn.execute(s + ";")
            conn.commit()
        finally:
            conn.close()

def write_audit_event(
    *,
    trace_id: str,
    event: str,
    payload: dict[str, Any],
    user_id: str | None = None,
    session_id: str | None = None,
) -> None:
    """
    Registra un evento de auditoría asociado a un trace_id.

    Args:
        trace_id (str): Identificador de traza de la petición.
        event (str): Nombre del evento.
        payload (dict[str, Any]): Datos adicionales del evento.
        user_id (str | None): Identificador del usuario.
        session_id (str | None): Identificador de la sesión.
    """

    if not AUDIT_ENABLED:
        return

    ts_utc = int(time.time())
    row = (ts_utc, trace_id, user_id, session_id, event, json.dumps(payload, ensure_ascii=False))

    with _lock:
        conn = _connect()
        try:
            conn.execute(
                "INSERT INTO audit_log (ts_utc, trace_id, user_id, session_id, event, payload_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                row,
            )
            conn.commit()
        finally:
            conn.close()

def read_audit_trace(trace_id: str, limit: int = 200) -> list[dict[str, Any]]:
    """
    Recupera los eventos de auditoría asociados a un trace_id.

    Args:
        trace_id (str): Identificador de traza.
        limit (int): Número máximo de registros a devolver (por defecto 200).

    Returns:
        list[dict[str, Any]]: Lista de eventos de auditoría ordenados cronológicamente.
    """

    if not AUDIT_ENABLED:
        return []

    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(
                "SELECT ts_utc, trace_id, user_id, session_id, event, payload_json "
                "FROM audit_log WHERE trace_id = ? ORDER BY id ASC LIMIT ?",
                (trace_id, limit),
            )
            out: list[dict[str, Any]] = []
            for ts_utc, tr, user_id, session_id, event, payload_json in cur.fetchall():
                out.append(
                    {
                        "ts_utc": ts_utc,
                        "trace_id": tr,
                        "user_id": user_id,
                        "session_id": session_id,
                        "event": event,
                        "payload": json.loads(payload_json),
                    }
                )
            return out
        finally:
            conn.close()
