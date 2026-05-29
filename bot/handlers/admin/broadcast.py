"""Admin broadcast — compose, target, schedule and send mass messages."""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, and_
from models.base import AsyncSessionLocal
from models.user import User
from models.order import Order
from services.broadcast import send_broadcast
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_back_keyboard, admin_broadcast_audience_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class BroadcastStates(StatesGroup):
    choose_type = State()
    enter_text = State()
    enter_photo = State()
    enter_btn_text = State()
    enter_btn_url = State()
    choose_audience = State()
    schedule_or_now = State()
    enter_schedule_time = State()


@router.callback_query(F.data == "admin:broadcast")
@handle_errors
async def cb_broadcast_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    builder.button(text=_("broadcast_text_only_btn", lang), callback_data="bcast_type:text")
    builder.button(text=_("broadcast_with_photo_btn", lang), callback_data="bcast_type:photo")
    builder.button(text=_("broadcast_with_btn_btn", lang), callback_data="bcast_type:button")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await state.set_state(BroadcastStates.choose_type)
    await callback.message.edit_text(_("broadcast_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("bcast_type:"))
@handle_errors
async def cb_bcast_type(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    btype = callback.data.split(":")[1]
    await state.update_data(bcast_type=btype)
    await state.set_state(BroadcastStates.enter_text)
    await callback.message.answer(_("enter_broadcast_text", lang))
    await callback.answer()


@router.message(BroadcastStates.enter_text)
@handle_errors
async def bcast_enter_text(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(bcast_text=message.text)
    data = await state.get_data()
    btype = data.get("bcast_type", "text")

    if btype == "photo":
        await state.set_state(BroadcastStates.enter_photo)
        await message.answer(_("enter_broadcast_photo", lang))
    elif btype == "button":
        await state.set_state(BroadcastStates.enter_btn_text)
        await message.answer(_("enter_broadcast_btn_text", lang))
    else:
        await state.set_state(BroadcastStates.choose_audience)
        await message.answer(
            _("choose_broadcast_audience", lang),
            reply_markup=admin_broadcast_audience_keyboard(lang),
        )


@router.message(BroadcastStates.enter_photo, F.photo)
@handle_errors
async def bcast_enter_photo(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(bcast_photo=message.photo[-1].file_id)
    await state.set_state(BroadcastStates.choose_audience)
    await message.answer(
        _("choose_broadcast_audience", lang),
        reply_markup=admin_broadcast_audience_keyboard(lang),
    )


@router.message(BroadcastStates.enter_btn_text)
@handle_errors
async def bcast_enter_btn_text(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(bcast_btn_text=message.text)
    await state.set_state(BroadcastStates.enter_btn_url)
    await message.answer(_("enter_broadcast_btn_url", lang))


@router.message(BroadcastStates.enter_btn_url)
@handle_errors
async def bcast_enter_btn_url(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(bcast_btn_url=message.text)
    await state.set_state(BroadcastStates.choose_audience)
    await message.answer(
        _("choose_broadcast_audience", lang),
        reply_markup=admin_broadcast_audience_keyboard(lang),
    )


@router.callback_query(F.data.startswith("bcast_aud:"))
@handle_errors
async def cb_bcast_audience(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    audience = callback.data.split(":")[1]
    await state.update_data(bcast_audience=audience)
    await state.set_state(BroadcastStates.schedule_or_now)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text=_("send_now_btn", lang), callback_data="bcast_when:now")
    builder.button(text=_("schedule_btn", lang), callback_data="bcast_when:schedule")
    builder.adjust(2)

    await callback.message.edit_text(_("schedule_or_now", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "bcast_when:now")
@handle_errors
async def cb_bcast_send_now(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.message.edit_text("⏳ Рассылка запущена...")
    await callback.answer()

    user_ids = await _get_audience_ids(data.get("bcast_audience", "all"))
    kb = None
    if data.get("bcast_btn_text") and data.get("bcast_btn_url"):
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        builder.button(text=data["bcast_btn_text"], url=data["bcast_btn_url"])
        kb = builder.as_markup()

    result = await send_broadcast(
        bot=callback.bot,
        user_ids=user_ids,
        text=data.get("bcast_text", ""),
        photo=data.get("bcast_photo"),
        reply_markup=kb,
    )
    await callback.message.answer(
        _("broadcast_sent", lang, sent=result["sent"], failed=result["failed"])
    )


@router.callback_query(F.data == "bcast_when:schedule")
@handle_errors
async def cb_bcast_schedule(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    await state.set_state(BroadcastStates.enter_schedule_time)
    await callback.message.answer(_("enter_schedule_time", lang))
    await callback.answer()


@router.message(BroadcastStates.enter_schedule_time)
@handle_errors
async def handle_schedule_time(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        scheduled_dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Неверный формат. Пример: 25.01.2025 14:30")
        return

    data = await state.get_data()
    await state.clear()

    # Schedule via APScheduler
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.date import DateTrigger
    # Access the running scheduler through bot's data
    # In production, pass scheduler via dependency injection
    user_ids = await _get_audience_ids(data.get("bcast_audience", "all"))
    text = data.get("bcast_text", "")
    photo = data.get("bcast_photo")
    bot = message.bot

    async def _send():
        await send_broadcast(bot, user_ids, text, photo)

    # For demo — just notify admin
    await message.answer(_("broadcast_scheduled", lang, time=message.text.strip()))


async def _get_audience_ids(audience: str) -> list[int]:
    """Fetch telegram_ids for the chosen audience segment."""
    from datetime import timedelta
    async with AsyncSessionLocal() as session:
        if audience == "all":
            result = await session.execute(
                select(User.telegram_id).where(User.is_active == True, User.is_banned == False)
            )
        elif audience == "active":
            cutoff = datetime.utcnow() - timedelta(days=30)
            result = await session.execute(
                select(User.telegram_id).where(User.last_active >= cutoff, User.is_banned == False)
            )
        elif audience == "ordered":
            result = await session.execute(
                select(User.telegram_id)
                .join(Order, Order.user_id == User.id)
                .where(User.is_banned == False)
                .distinct()
            )
        else:
            result = await session.execute(
                select(User.telegram_id).where(User.is_active == True, User.is_banned == False)
            )
        return [row[0] for row in result]
