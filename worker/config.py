from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://solid:solid@postgres:5432/solid",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    request_rate_limit_s: float = Field(default=1.0, alias="REQUEST_RATE_LIMIT_S")
    global_concurrency: int = Field(default=4, alias="GLOBAL_CONCURRENCY")


settings = Settings()
