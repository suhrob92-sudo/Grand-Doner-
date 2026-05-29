"""Admin dashboard — entry point and stats overview."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from models.user import User
from services.statistics import get_dashboard_stats
from models.base import AsyncSessionLocal
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_main_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)


def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids_list


@router.message(Command("admin"))
@handle_errors
async def cmd_admin(message: Message, lang: str, **kwargs) -> None:
    if not is_admin(message.from_user.id):
        return
    async with AsyncSessionLocal() as session:
        stats = await get_dashboard_stats(session)
    text = _("admin_dashboard", lang, **stats)
    await message.answer(
        f"{_('admin_welcome', lang)}\n\n{text}",
        reply_markup=admin_main_keyboard(lang),
    )


@router.callback_query(F.data == "admin:main")
@handle_errors
async def cb_admin_main(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    async with AsyncSessionLocal() as session:
        stats = await get_dashboard_stats(session)
    text = _("admin_dashboard", lang, **stats)
    await callback.message.edit_text(
        f"{_('admin_welcome', lang)}\n\n{text}",
        reply_markup=admin_main_keyboard(lang),
    )
    await callback.answer()
