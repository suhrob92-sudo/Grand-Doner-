"""Broadcast service — sends messages to lists of users with error counting."""

import asyncio
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

logger = logging.getLogger(__name__)


async def send_broadcast(
    bot: Bot,
    user_ids: list[int],
    text: str,
    photo: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> dict:
    """
    Send a broadcast message to all given telegram user IDs.
    Returns {"sent": N, "failed": M}.
    """
    sent = 0
    failed = 0
    for uid in user_ids:
        try:
            if photo:
                await bot.send_photo(uid, photo=photo, caption=text, reply_markup=reply_markup)
            else:
                await bot.send_message(uid, text=text, reply_markup=reply_markup)
            sent += 1
        except Exception as exc:
            logger.warning("Broadcast failed for user %s: %s", uid, exc)
            failed += 1
        # Respect Telegram rate limits
        await asyncio.sleep(0.05)
    logger.info("Broadcast complete: sent=%s failed=%s", sent, failed)
    return {"sent": sent, "failed": failed}
