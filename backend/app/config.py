import os

class Settings:
    PROJECT_NAME: str = "CRIMSON Intelligence & Investigation Platform"
    VERSION: str = "0.5.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "crimson-secret-key-super-secure-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crimson.db")
    DEMO_MODE: bool = True

settings = Settings()
