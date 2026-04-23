from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MAD-HUMANIZER"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mad_humanizer"

    # Humanizer (vLLM remote inference)
    HUMANIZER_API_URL: str = ""
    HUMANIZER_MODEL_NAME: str = "humanizer"
    HUMANIZER_API_KEY: str = ""
    MAX_OUTPUT_TOKENS: int = 2048
    TEMPERATURE: float = 0.95

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/callback"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY_MINUTES: int = 60        # 1 hour
    REFRESH_TOKEN_EXPIRY_DAYS: int = 7           # 7 days

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    VERIFICATION_CODE_EXPIRY_MINUTES: int = 10

    # Detector API Keys
    GPTZERO_API_KEY: str = ""
    ORIGINALITY_API_KEY: str = ""
    COPYLEAKS_API_KEY: str = ""
    ZEROGPT_API_KEY: str = ""

    # Humanize retry-loop tuning
    HUMANIZE_DETECTOR_NAME: str = "zerogpt"
    HUMANIZE_AI_SCORE_THRESHOLD: float = 0.35
    HUMANIZE_MAX_ATTEMPTS: int = 3
    HUMANIZE_TEMP_BUMP_PER_RETRY: float = 0.05
    HUMANIZE_DETECTOR_TIMEOUT_SECONDS: float = 30.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
