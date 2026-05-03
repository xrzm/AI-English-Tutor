from functools import cached_property
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "教育服务系统"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = "development"
    ENABLE_DOCS: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    HOST: str = "127.0.0.1"
    PORT: int = 8001

    SECRET_KEY: str = "change-me-in-production"
    ALLOW_ORIGINS: str = "*"
    ENABLE_STATIC_INDEX: bool = True

    DATABASE_URL: str = "sqlite:///./app.db"

    DASHSCOPE_API_KEY: str = ""
    QWEN_CHAT_MODEL: str = "qwen-plus"
    QWEN_OCR_MODEL: str = "qwen-plus"
    QWEN_AUDIO_MODEL: str = "qwen-audio-turbo"
    QWEN_TTS_MODEL: str = "sambert-zhichu-v1"

    FFMPEG_PATH: str = "/usr/bin/ffmpeg"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    TEMP_DIR: Path = BASE_DIR / "temp"
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    MAX_UPLOAD_MB: int = 20

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @cached_property
    def allow_origins_list(self) -> List[str]:
        if self.ALLOW_ORIGINS.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.ALLOW_ORIGINS.split(",") if item.strip()]


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
