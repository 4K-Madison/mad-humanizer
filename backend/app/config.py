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
    TEMPERATURE: float = 0.7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/callback"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
