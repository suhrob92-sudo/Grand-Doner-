"""Language change handler — available anytime via /language command."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.user import User
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import language_inline, main_menu_inline

router = Router()
logger = logging.getLogger(__name__)


class LanguageChangeStates(StatesGroup):
    waiting_new_language = State()


@router.message(Command("language"))
@handle_errors
async def cmd_language(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    """Show the language selection keyboard."""
    await state.set_state(LanguageChangeStates.waiting_new_language)
    await message.answer(
        _("choose_language", lang),
        reply_markup=language_inline(),
    )


@router.callback_query(F.data == "profile:language")
@handle_errors
async def cb_profile_language(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    await state.set_state(LanguageChangeStates.waiting_new_language)
    await callback.message.edit_text(
        _("choose_language", lang),
        reply_markup=language_inline(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"), LanguageChangeStates.waiting_new_language)
@handle_errors
async def cb_language_change(callback: CallbackQuery, state: FSMContext, **kwargs) -> None:
    """Persist the new language choice."""
    chosen_lang = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            user.language = chosen_lang
            await session.commit()

    await callback.message.edit_text(
        _("language_changed", chosen_lang),
        reply_markup=main_menu_inline(chosen_lang),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
@handle_errors
async def cb_language_any(callback: CallbackQuery, **kwargs) -> None:
    """Handle language selection outside registration flow (fallback)."""
    chosen_lang = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            user.language = chosen_lang
            await session.commit()

    await callback.message.edit_text(
        _("language_changed", chosen_lang),
        reply_markup=main_menu_inline(chosen_lang),
    )
    await callback.answer()
