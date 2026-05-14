from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = Field(default="dev", alias="ENV")
    port: int = Field(default=8000, alias="PORT")
    database_url: str = Field(default="sqlite:///./quiz_agent.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    hmac_client_id: str = Field(default="agent", alias="HMAC_CLIENT_ID")
    hmac_shared_secret: str = Field(default="dev-secret", alias="HMAC_SHARED_SECRET")
    quiz_push_url: str | None = Field(default=None, alias="QUIZ_PUSH_URL")
    results_webhook_url: str | None = Field(default=None, alias="RESULTS_WEBHOOK_URL")
    tesseract_path: str | None = Field(default=None, alias="TESSERACT_PATH")
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    vertex_project: str | None = Field(default=None, alias="VERTEX_PROJECT")
    vertex_region: str | None = Field(default=None, alias="VERTEX_REGION")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
