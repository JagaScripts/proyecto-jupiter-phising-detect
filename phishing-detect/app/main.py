from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.orchestrator import router as orchestrator_router
from app.core.logging import setup_logging, get_logger
from app.middleware.request_context import request_context_middleware
from app.storage.audit_store import init_audit_db
from app.api.audit import router as audit_router
from app.db.init_db import init_db



def create_app() -> FastAPI:
    setup_logging(app_name="Phishing Detect")
    logger = get_logger("app")

    init_audit_db()
    init_db()

    app = FastAPI(title="Phishing Detect", version="0.1.0")
    app.middleware("http")(request_context_middleware)

    app.include_router(health_router, prefix="/v1", tags=["health"])
    app.include_router(chat_router, prefix="/v1", tags=["chat"])
    app.include_router(orchestrator_router, prefix="/v1", tags=["orchestrator"])
    app.include_router(audit_router, prefix="/v1", tags=["audit"])

    logger.info("App creada", extra={"event": "app_start", "extra": {"version": "0.1.0"}})
    return app

app = create_app()