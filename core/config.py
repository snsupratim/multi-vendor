from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    SENTRY_DSN: str
    ENVIRONMENT: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GROQ_API_KEY: str
    MONGO_URI: str

    REDIS_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str

    GEMINI_API_KEY: str
    
    # PostgreSQL Connection String for actual Payroll Tables
    PAYROLL_DB_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()