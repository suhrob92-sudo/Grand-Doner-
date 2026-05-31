"""Throttling middleware — limits users to one message per `rate_limit` seconds."""

import logging
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from redis.asyncio import Redis
from config import settings

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self._redis: Redis | None = None

    def _get_redis(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                ssl_cert_reqs=None,
            )
        return self._redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        redis = self._get_redis()
        key = f"throttle:{user.id}"
        try:
            result = await redis.set(key, 1, ex=int(self.rate_limit), nx=True)
            if result is None:
                # Key already existed — user is sending too fast
                if isinstance(event, Message):
                    await event.answer("⏳ Не так быстро! Подождите секунду.")
                return
        except Exception as exc:
            logger.warning("ThrottlingMiddleware Redis error: %s", exc)

        return await handler(event, data)
