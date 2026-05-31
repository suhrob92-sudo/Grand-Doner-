"""Central configuration loaded from environment variables via pydantic-settings."""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    COURIER_IDS: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/shaurma_bot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # YooKassa
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    WEBHOOK_URL: str = "https://yourdomain.onrender.com"
    WEBHOOK_PATH: str = "/webhook/bot"

    @field_validator("WEBHOOK_URL", mode="before")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")
    WEBHOOK_PORT: int = 8080  # legacy — use PORT instead on Render

    # Yandex Taxi
    YANDEX_TAXI_API_KEY: str = ""
    YANDEX_TAXI_CLIENT_ID: str = ""
    YANDEX_TAXI_PARK_ID: str = ""

    # Restaurant
    RESTAURANT_NAME: str = "Shaurma House"
    RESTAURANT_ADDRESS: str = "Москва, ул. Примерная, 1"
    RESTAURANT_LAT: float = 55.7558
    RESTAURANT_LON: float = 37.6176
    RESTAURANT_PHONE: str = "+7XXXXXXXXXX"

    # Bonus system
    BONUS_RATE: int = 5          # points per 100 spent
    BONUS_EXPIRE_DAYS: int = 90
    MAX_BONUS_PERCENT: int = 30  # max % of order payable with bonuses

    # Logging
    LOG_LEVEL: str = "INFO"

    # Render — PORT is injected automatically by the platform
    PORT: int = 8080

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def courier_ids_list(self) -> List[int]:
        if not self.COURIER_IDS:
            return []
        return [int(x.strip()) for x in self.COURIER_IDS.split(",") if x.strip()]


settings = Settings()
