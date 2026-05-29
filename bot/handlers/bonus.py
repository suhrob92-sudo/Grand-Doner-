"""Bonus points info and history handler."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.user import User
from models.bonus import BonusTransaction
from utils.i18n import _
from utils.helpers import format_datetime
from utils.decorators import handle_errors
from keyboards.inline import back_to_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("bonus"))
@handle_errors
async def cmd_bonus(message: Message, lang: str, db_user: User | None = None, **kwargs) -> None:
    if not db_user:
        await message.answer(_("user_not_registered", lang))
        return
    text = _("bonus_info", lang, points=db_user.bonus_points)
    await message.answer(f"{_('bonus_title', lang)}\n\n{text}")


@router.callback_query(F.data == "profile:bonus")
@handle_errors
async def cb_bonus_history(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    if not db_user:
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BonusTransaction)
            .where(BonusTransaction.user_id == db_user.id)
            .order_by(BonusTransaction.created_at.desc())
            .limit(20)
        )
        txns = result.scalars().all()

    reason_labels = {
        "order_accrual": "Заказ" if lang == "ru" else "Buyurtma",
        "order_spend": "Оплата" if lang == "ru" else "To'lov",
        "referral": "Реферал" if lang == "ru" else "Referral",
        "birthday": "День рождения" if lang == "ru" else "Tug'ilgan kun",
        "admin": "Администратор" if lang == "ru" else "Administrator",
        "expiry": "Сгорело" if lang == "ru" else "Yondi",
    }

    lines = [f"{_('bonus_title', lang)}\n💎 <b>{db_user.bonus_points}</b> баллов\n"]
    for t in txns:
        sign = "+" if t.amount > 0 else ""
        reason = reason_labels.get(t.reason, t.reason)
        lines.append(_(
            "bonus_transaction_line", lang,
            date=format_datetime(t.created_at),
            sign=sign,
            amount=abs(t.amount),
            reason=reason,
        ))

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main_keyboard(lang),
    )
    await callback.answer()
