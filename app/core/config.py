from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://user:pass@localhost:5432/pos"

    jwt_access_algorithm: str = "RS256"
    jwt_private_key: str
    jwt_public_key: str

    jwt_refresh_algorithm: str = "HS256"
    jwt_secret_key: str

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    login_rate_limit: str = "5/minute"
    default_rate_limit: str = "100/minute"

    tax_rate: float = 0.0

    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()