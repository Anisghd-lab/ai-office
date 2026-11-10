"""Application settings and configuration."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "AI Office"
    APP_VERSION: str = "1.2.0"
    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # Security & Owner Identity
    SECRET_KEY: str = Field(default="ai-office-insecure-dev-key-change-in-production-min32chars")
    USER_GATEWAY_DEFAULT_DENY: bool = True
    USER_APPROVAL_TOKEN_TTL_SECONDS: int = 1800
    CEO_APPROVAL_TOKEN_TTL_SECONDS: int = 1800  # Backwards compatibility alias
    ENCRYPTION_KEY_32BYTES_BASE64: Optional[str] = None
    OWNER_API_KEY: str = Field(default="owner-default-dev-token")
    CEO_API_KEY: str = Field(default="owner-default-dev-token")  # Backwards compatibility alias

    # Timezone
    TIMEZONE: str = "Africa/Algiers"

    # Database
    DATABASE_PATH: str = Field(
        default_factory=lambda: str(
            Path(__file__).parent / "database" / "storage" / "ai_office.db"
        )
    )
    DATABASE_WAL_MODE: bool = True

    # Social Integrations
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/social/google/callback"

    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/social/youtube/callback"

    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/social/tiktok/callback"

    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/social/facebook/callback"

    INSTAGRAM_CLIENT_ID: Optional[str] = None
    INSTAGRAM_CLIENT_SECRET: Optional[str] = None
    INSTAGRAM_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/social/instagram/callback"


settings = Settings()
