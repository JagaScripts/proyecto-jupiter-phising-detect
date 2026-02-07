from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.orchestrator import router as orchestrator_router
from dotenv import load_dotenv

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Phishing Detect", version="0.1.0")
    app.include_router(health_router, prefix="/v1", tags=["health"])
    app.include_router(chat_router, prefix="/v1", tags=["chat"])
    app.include_router(orchestrator_router, prefix="/v1", tags=["orchestrator"])

    return app

app = create_app()