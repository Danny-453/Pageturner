from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PageTurners API"
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://pageturners:pageturners@localhost:5432/pageturners"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    seed_admin_email: str = "admin@pageturners.org"
    seed_student_email: str = "student@pageturners.org"
    seed_admin_password: str | None = None
    seed_student_password: str | None = None
    frontend_url: str = "http://localhost:5173"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_sender_email: str | None = None
    smtp_use_ssl: bool = False
    agentrouter_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AGENTROUTER_API_KEY", "OPENROUTER_API_KEY"),
    )
    ai_tutor_base_url: str = "https://agentrouter.org/v1"
    ai_tutor_models: str = "gpt-6-astra,claude-opus-4-8"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
