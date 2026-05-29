"""Promo code user-facing handler (apply from menu command)."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from utils.i18n import _
from utils.decorators import handle_errors

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("promo"))
@handle_errors
async def cmd_promo(message: Message, lang: str, **kwargs) -> None:
    """Inform user to apply promo code via cart."""
    await message.answer(_("enter_promo_code", lang))
