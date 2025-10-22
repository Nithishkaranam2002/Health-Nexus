from typing import List, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    # --- app/base ---
    app_name: str = "medassist-ai"
    api_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = ["http://localhost:3000"]
    jwt_secret: str = "devsecret_change_me"

    # --- LLM config (matches your .env names) ---
    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_prefix="",            # read vars exactly as given
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",           # ignore any unrelated env keys
    )

    # Accept JSON array or comma-separated list for CORS
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                import json
                return json.loads(v)
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

settings = Settings()
