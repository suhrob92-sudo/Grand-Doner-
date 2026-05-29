"""Admin bot settings management."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.settings import BotSetting
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class SettingsStates(StatesGroup):
    entering_value = State()


async def _get_setting(key: str, default: str = "") -> str:
    async with AsyncSessionLocal() as session:
        row = (await session.execute(
            select(BotSetting).where(BotSetting.key == key)
        )).scalar_one_or_none()
        return row.value if row else default


async def _set_setting(key: str, value: str) -> None:
    async with AsyncSessionLocal() as session:
        row = (await session.execute(
            select(BotSetting).where(BotSetting.key == key)
        )).scalar_one_or_none()
        if row:
            row.value = value
        else:
            session.add(BotSetting(key=key, value=value))
        await session.commit()


@router.callback_query(F.data == "admin:settings")
@handle_errors
async def cb_admin_settings(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    maintenance = await _get_setting("maintenance_mode", "0")
    maint_label = "🔧 Обслуживание: ВКЛ" if maintenance == "1" else "✅ Обслуживание: ВЫКЛ"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.button(text=_("working_hours_btn", lang), callback_data="setting:working_hours")
    builder.button(text=_("min_order_btn", lang), callback_data="setting:min_order")
    builder.button(text=_("restaurant_info_btn", lang), callback_data="setting:restaurant_name")
    builder.button(text=_("bonus_rate_btn", lang), callback_data="setting:bonus_rate")
    builder.button(text=maint_label, callback_data="setting:toggle_maintenance")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(2)

    await callback.message.edit_text(_("settings_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "setting:toggle_maintenance")
@handle_errors
async def cb_toggle_maintenance(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    current = await _get_setting("maintenance_mode", "0")
    new_val = "0" if current == "1" else "1"
    await _set_setting("maintenance_mode", new_val)
    key = "maintenance_on" if new_val == "1" else "maintenance_off"
    await callback.answer(_(key, lang), show_alert=True)
    await cb_admin_settings(callback, lang)


@router.callback_query(F.data.startswith("setting:"))
@handle_errors
async def cb_setting_enter_value(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    setting_key = callback.data.split(":")[1]
    if setting_key == "toggle_maintenance":
        return  # handled separately

    prompts = {
        "working_hours": _("enter_working_hours", lang),
        "min_order": "Введите минимальную сумму заказа для доставки (₽):",
        "restaurant_name": "Введите название ресторана:",
        "bonus_rate": "Введите количество баллов за каждые 100 ₽ (например: 5):",
    }
    prompt = prompts.get(setting_key, "Введите значение:")
    await state.update_data(setting_key=setting_key)
    await state.set_state(SettingsStates.entering_value)
    await callback.message.answer(prompt)
    await callback.answer()


@router.message(SettingsStates.entering_value)
@handle_errors
async def handle_setting_value(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    data = await state.get_data()
    key = data.get("setting_key")
    if key:
        await _set_setting(key, message.text.strip())
    await message.answer(_("setting_saved", lang))
    await state.clear()
