import os
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

# Load .env file explicitly from the backend directory BEFORE creating Settings
Backend_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Backend_DIR / ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Backend_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="mysql+pymysql://siem:siem_password@localhost:3306/siemdb",
        alias="DATABASE_URL"
    )

    # JWT
    jwt_secret_key: str = Field(
        default="change-me-in-production-jwt-secret-key-min-length-32",
        alias="JWT_SECRET"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expires_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRES_MINUTES"
    )
    jwt_refresh_token_expires_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRES_DAYS"
    )

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173",
        alias="CORS_ORIGINS"
    )

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=True, alias="DEBUG")

settings = Settings()