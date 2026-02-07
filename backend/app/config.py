from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://solid:solid@postgres:5432/solid",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    single_user_mode: bool = Field(default=True, alias="SINGLE_USER_MODE")
    auth_secret: str = Field(default="dev-secret", alias="AUTH_SECRET")
    alert_email_sender: str = Field(default="alerts@i7scanner.local", alias="ALERT_EMAIL_SENDER")
    alert_email_host: str = Field(default="localhost", alias="ALERT_EMAIL_HOST")

    southeast_states: list[str] = [
        "FL",
        "GA",
        "AL",
        "MS",
        "TN",
        "NC",
        "SC",
        "KY",
        "LA",
        "AR",
        "VA",
        "WV",
    ]


settings = Settings()
