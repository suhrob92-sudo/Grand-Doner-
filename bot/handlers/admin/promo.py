"""Admin promo code management."""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.promo import PromoCode
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class PromoAdminStates(StatesGroup):
    enter_code = State()
    choose_type = State()
    enter_value = State()
    enter_min_order = State()
    enter_max_uses = State()
    enter_valid_to = State()


@router.callback_query(F.data == "admin:promo")
@handle_errors
async def cb_admin_promo(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        promos = (await session.execute(
            select(PromoCode).where(PromoCode.is_active == True).order_by(PromoCode.id.desc())
        )).scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for p in promos:
        max_str = str(p.max_uses) if p.max_uses else "∞"
        type_str = f"{p.discount_value}%" if p.discount_type == "percent" else f"{p.discount_value // 100}₽"
        label = f"{p.code} — {type_str} | {p.used_count}/{max_str}"
        builder.button(text=label, callback_data=f"admin:promo_detail:{p.id}")
    builder.row(InlineKeyboardButton(text=_("add_promo_btn", lang), callback_data="admin:promo_add"))
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await callback.message.edit_text(_("promo_list_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:promo_detail:"))
@handle_errors
async def cb_promo_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    promo_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        promo = (await session.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        )).scalar_one_or_none()

    if not promo:
        await callback.answer("Промокод не найден", show_alert=True)
        return

    type_str = f"{promo.discount_value}%" if promo.discount_type == "percent" else f"{promo.discount_value // 100} ₽"
    text = (
        f"🎁 <b>{promo.code}</b>\n"
        f"Тип: {type_str}\n"
        f"Мин. заказ: {promo.min_order_amount // 100} ₽\n"
        f"Использований: {promo.used_count} / {promo.max_uses or '∞'}\n"
        f"Истекает: {promo.valid_to.strftime('%d.%m.%Y') if promo.valid_to else '—'}"
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Деактивировать", callback_data=f"admin:promo_deactivate:{promo_id}")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:promo"))
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:promo_deactivate:"))
@handle_errors
async def cb_promo_deactivate(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    promo_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        promo = (await session.execute(
            select(PromoCode).where(PromoCode.id == promo_id)
        )).scalar_one()
        promo.is_active = False
        await session.commit()
    await callback.answer(_("promo_deactivated", lang), show_alert=True)
    await cb_admin_promo(callback, lang)


@router.callback_query(F.data == "admin:promo_add")
@handle_errors
async def cb_promo_add_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(PromoAdminStates.enter_code)
    await callback.message.answer(_("enter_promo_code_admin", lang))
    await callback.answer()


@router.message(PromoAdminStates.enter_code)
@handle_errors
async def promo_admin_code(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(promo_code=message.text.strip().upper())
    await state.set_state(PromoAdminStates.choose_type)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text=_("promo_percent_btn", lang), callback_data="promo_type:percent")
    builder.button(text=_("promo_fixed_btn", lang), callback_data="promo_type:fixed")
    builder.adjust(2)
    await message.answer(_("choose_promo_type", lang), reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("promo_type:"))
@handle_errors
async def promo_choose_type(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    ptype = callback.data.split(":")[1]
    await state.update_data(promo_type=ptype)
    await state.set_state(PromoAdminStates.enter_value)
    await callback.message.answer(_("enter_promo_value", lang))
    await callback.answer()


@router.message(PromoAdminStates.enter_value)
@handle_errors
async def promo_admin_value(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        value = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите число.")
        return
    data = await state.get_data()
    ptype = data.get("promo_type", "percent")
    stored = int(value) if ptype == "percent" else int(value * 100)
    await state.update_data(promo_value=stored)
    await state.set_state(PromoAdminStates.enter_min_order)
    await message.answer(_("enter_promo_min_order", lang))


@router.message(PromoAdminStates.enter_min_order)
@handle_errors
async def promo_admin_min_order(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        val = int(float(message.text) * 100)
    except ValueError:
        val = 0
    await state.update_data(promo_min_order=val)
    await state.set_state(PromoAdminStates.enter_max_uses)
    await message.answer(_("enter_promo_max_uses", lang))


@router.message(PromoAdminStates.enter_max_uses)
@handle_errors
async def promo_admin_max_uses(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        val = int(message.text)
    except ValueError:
        val = 0
    await state.update_data(promo_max_uses=val)
    await state.set_state(PromoAdminStates.enter_valid_to)
    await message.answer(_("enter_promo_valid_to", lang))


@router.message(PromoAdminStates.enter_valid_to)
@handle_errors
async def promo_admin_valid_to(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    valid_to = None
    if message.text.strip() != "0":
        try:
            valid_to = datetime.strptime(message.text.strip(), "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат даты. Пример: 31.12.2025")
            return

    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        promo = PromoCode(
            code=data["promo_code"],
            discount_type=data["promo_type"],
            discount_value=data["promo_value"],
            min_order_amount=data.get("promo_min_order", 0),
            max_uses=data.get("promo_max_uses", 0),
            valid_to=valid_to,
            is_active=True,
        )
        session.add(promo)
        await session.commit()

    await message.answer(_("promo_created", lang, code=data["promo_code"]))
    await state.clear()
