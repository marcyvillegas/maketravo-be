from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

from src.shared.constants import EnviromnentEnums


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    ENVIRONMENT: EnviromnentEnums
    FIREBASE_PROJECT_ID: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_PRIVATE_KEY: SecretStr
    FIREBASE_APP_NAME: str
    APP_DOMAIN: str

    # Comma-separated in .env, e.g. "http://localhost:3000,https://maketravo.com"
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- database ---
    MONGODB_URI: SecretStr
    MONGODB_DB_NAME: str

    MONGODB_MAX_POOL_SIZE: int = 30
    MONGODB_MIN_POOL_SIZE: int = 0
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5_000
    MONGODB_CONNECT_TIMEOUT_MS: int = 10_000
    MONGODB_SOCKET_TIMEOUT_MS: int = 20_000

    MONGODB_AUTO_CREATE_INDEXES: bool = True

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
