"""User profile handler — display info, order history, settings."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, func
from models.base import AsyncSessionLocal
from models.order import Order
from models.user import User
from models.referral import Referral
from utils.i18n import _
from utils.helpers import format_datetime
from utils.decorators import handle_errors
from keyboards.inline import profile_keyboard, main_menu_inline, admin_back_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def show_profile(callback: CallbackQuery, lang: str, db_user: User | None) -> None:
    if not db_user:
        await callback.message.edit_text(_("user_not_registered", lang))
        await callback.answer()
        return

    # Count referrals
    async with AsyncSessionLocal() as session:
        ref_count = (await session.execute(
            select(func.count()).where(Referral.referrer_id == db_user.telegram_id)
        )).scalar_one()

    text = _("profile_info", lang,
             name=db_user.full_name,
             phone=db_user.phone or "—",
             bonus=db_user.bonus_points,
             spent=db_user.total_spent // 100,
             referrals=ref_count)

    await callback.message.edit_text(
        f"{_('profile_title', lang)}\n\n{text}",
        reply_markup=profile_keyboard(lang),
    )
    await callback.answer()


@router.message(Command("profile"))
@handle_errors
async def cmd_profile(message: Message, lang: str, db_user: User | None = None, **kwargs) -> None:
    if not db_user:
        await message.answer(_("user_not_registered", lang))
        return

    async with AsyncSessionLocal() as session:
        ref_count = (await session.execute(
            select(func.count()).where(Referral.referrer_id == db_user.telegram_id)
        )).scalar_one()

    text = _("profile_info", lang,
             name=db_user.full_name,
             phone=db_user.phone or "—",
             bonus=db_user.bonus_points,
             spent=db_user.total_spent // 100,
             referrals=ref_count)

    await message.answer(
        f"{_('profile_title', lang)}\n\n{text}",
        reply_markup=profile_keyboard(lang),
    )


@router.callback_query(F.data == "main:profile")
@handle_errors
async def cb_profile(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    await show_profile(callback, lang, db_user)


async def show_order_history(callback: CallbackQuery, lang: str, db_user: User | None) -> None:
    if not db_user:
        await callback.answer(_("user_not_registered", lang), show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        orders_result = await session.execute(
            select(Order)
            .where(Order.user_id == db_user.id)
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        orders = orders_result.scalars().all()

    if not orders:
        await callback.message.edit_text(
            _("no_orders_yet", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        await callback.answer()
        return

    lines = []
    for o in orders:
        status_key = f"status_{o.status}" if o.status in ("pending","paid","preparing","ready","on_the_way","completed","cancelled") else "status_pending"
        lines.append(_("order_history_item", lang,
                       number=o.order_number,
                       date=format_datetime(o.created_at),
                       amount=o.total // 100,
                       status=_(status_key, lang)))

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_back_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "profile:history")
@handle_errors
async def cb_order_history(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    await show_order_history(callback, lang, db_user)


@router.callback_query(F.data == "profile:notifications")
@handle_errors
async def cb_toggle_notifications(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    if not db_user:
        await callback.answer()
        return
    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )).scalar_one()
        user.notifications_enabled = not user.notifications_enabled
        await session.commit()
        enabled = user.notifications_enabled

    key = "notifications_on" if enabled else "notifications_off"
    await callback.answer(_(key, lang), show_alert=True)
