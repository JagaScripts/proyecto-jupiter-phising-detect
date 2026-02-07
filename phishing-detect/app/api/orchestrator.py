from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.orchestrator.engine import run_orchestrator

class Settings(BaseModel):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")
    openai_model: str = "gpt-4.1"


settings = Settings()
router = APIRouter()


class OrchestrateRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=30)
    message: str = Field(..., min_length=1, max_length=4000)
    context: dict = Field(default_factory=dict)


class OrchestrateResponse(BaseModel):
    final_user_message: str
    response_id: str | None = None


@router.post("/orchestrate", response_model=OrchestrateResponse)
def orchestrate(req: OrchestrateRequest) -> OrchestrateResponse:
    out = run_orchestrator(user_id=req.user_id, message=req.message, model=settings.openai_model)
    return OrchestrateResponse(final_user_message=out["final_user_message"], response_id=out["raw_response_id"])