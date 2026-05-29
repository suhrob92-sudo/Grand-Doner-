"""Handy async decorator helpers."""

import logging
from functools import wraps
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


def handle_errors(func):
    """Catch all exceptions in a handler and log them without crashing the bot."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            logger.exception("Unhandled error in %s: %s", func.__name__, exc)
            # Try to reply to the user
            for arg in args:
                if isinstance(arg, Message):
                    await arg.answer("❌ Произошла ошибка. Попробуйте ещё раз.")
                    break
                if isinstance(arg, CallbackQuery):
                    await arg.answer("❌ Ошибка", show_alert=True)
                    break
    return wrapper
