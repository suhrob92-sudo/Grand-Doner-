"""Admin courier management."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from models.base import AsyncSessionLocal
from models.user import User
from models.order import Order
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class CourierAdminStates(StatesGroup):
    entering_id = State()


@router.callback_query(F.data == "admin:couriers")
@handle_errors
async def cb_admin_couriers(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        couriers = (await session.execute(
            select(User).where(User.is_courier == True)
        )).scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for c in couriers:
        status = "🟢" if c.is_active else "🔴"
        builder.button(
            text=f"{status} {c.full_name}",
            callback_data=f"admin:courier_detail:{c.id}",
        )
    builder.row(InlineKeyboardButton(text=_("add_courier_btn", lang), callback_data="admin:courier_add"))
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await callback.message.edit_text(_("couriers_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:courier_detail:"))
@handle_errors
async def cb_courier_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    courier_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        courier = (await session.execute(
            select(User).where(User.id == courier_id)
        )).scalar_one_or_none()
        if not courier:
            await callback.answer("Не найден", show_alert=True)
            return
        completed_count = (await session.execute(
            select(func.count(Order.id)).where(
                Order.courier_id == courier_id,
                Order.status == "completed",
            )
        )).scalar_one()

    text = (
        f"🚚 <b>{courier.full_name}</b>\n"
        f"📞 {courier.phone or '—'}\n"
        f"✅ Завершено заказов: {completed_count}"
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.button(text=_("remove_courier_btn", lang), callback_data=f"admin:courier_remove:{courier_id}")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:couriers"))
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin:courier_add")
@handle_errors
async def cb_courier_add_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(CourierAdminStates.entering_id)
    await callback.message.answer(_("enter_courier_id", lang))
    await callback.answer()


@router.message(CourierAdminStates.entering_id)
@handle_errors
async def handle_courier_add(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        telegram_id = int(message.text.strip())
    except ValueError:
        await message.answer("Введите числовой Telegram ID.")
        return

    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if user:
            user.is_courier = True
            await session.commit()
            await message.answer(_("courier_added", lang))
        else:
            await message.answer("Пользователь не найден в системе. Пусть сначала запустит бота.")
    await state.clear()


@router.callback_query(F.data.startswith("admin:courier_remove:"))
@handle_errors
async def cb_courier_remove(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    courier_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.id == courier_id)
        )).scalar_one_or_none()
        if user:
            user.is_courier = False
            await session.commit()
    await callback.answer(_("courier_removed", lang), show_alert=True)
    await cb_admin_couriers(callback, lang)
