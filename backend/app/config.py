from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MAD-HUMANIZER"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mad_humanizer"

    # Model
    BASE_MODEL_NAME: str = "meta-llama/Llama-3.2-1B"
    LORA_ADAPTER_PATH: str = "./model/lora_adapter"
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

    # Detector API Keys
    GPTZERO_API_KEY: str = ""
    ORIGINALITY_API_KEY: str = ""
    COPYLEAKS_API_KEY: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
