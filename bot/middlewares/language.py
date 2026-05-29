"""Language middleware — loads the user's preferred language from DB and injects it."""

import logging
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.user import User

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseMiddleware):
    """Attach `lang` to handler data based on the user's DB record."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        lang = "ru"
        if user:
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        select(User).where(User.telegram_id == user.id)
                    )
                    db_user = result.scalar_one_or_none()
                    if db_user:
                        lang = db_user.language
                        data["db_user"] = db_user
            except Exception as exc:
                logger.warning("LanguageMiddleware DB error: %s", exc)
        data["lang"] = lang
        return await handler(event, data)
