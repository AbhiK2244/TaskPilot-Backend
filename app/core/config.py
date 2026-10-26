from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskPilot"
    database_url: str = "sqlite:///./taskpilot.db"
    auto_create_tables: bool = True

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    reminder_email: str = ""

    timezone: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
