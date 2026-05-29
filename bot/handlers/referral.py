"""Referral program handler."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, func
from models.base import AsyncSessionLocal
from models.user import User
from models.referral import Referral
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import back_to_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def show_referral(callback: CallbackQuery, lang: str, db_user: User | None) -> None:
    if not db_user:
        await callback.answer(_("user_not_registered", lang), show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        refs = (await session.execute(
            select(Referral).where(Referral.referrer_id == db_user.telegram_id)
        )).scalars().all()
        earned = sum(r.bonus_amount for r in refs if r.bonus_paid)
        count = len(refs)

    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{db_user.telegram_id}"

    text = _("referral_info", lang,
             link=ref_link,
             count=count,
             earned=earned)

    await callback.message.edit_text(
        f"{_('referral_title', lang)}\n\n{text}",
        reply_markup=back_to_main_keyboard(lang),
    )
    await callback.answer()


@router.message(Command("referral"))
@handle_errors
async def cmd_referral(message: Message, lang: str, db_user: User | None = None, **kwargs) -> None:
    if not db_user:
        await message.answer(_("user_not_registered", lang))
        return

    async with AsyncSessionLocal() as session:
        refs = (await session.execute(
            select(Referral).where(Referral.referrer_id == db_user.telegram_id)
        )).scalars().all()
        earned = sum(r.bonus_amount for r in refs if r.bonus_paid)
        count = len(refs)

    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{db_user.telegram_id}"

    text = _("referral_info", lang,
             link=ref_link,
             count=count,
             earned=earned)

    await message.answer(f"{_('referral_title', lang)}\n\n{text}")


@router.callback_query(F.data == "profile:referral")
@handle_errors
async def cb_profile_referral(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    await show_referral(callback, lang, db_user)


@router.message(Command("leaderboard"))
@handle_errors
async def cmd_leaderboard(message: Message, lang: str, **kwargs) -> None:
    """Show top 10 referrers."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(
                Referral.referrer_id,
                func.count(Referral.id).label("count"),
            )
            .where(Referral.bonus_paid == True)
            .group_by(Referral.referrer_id)
            .order_by(func.count(Referral.id).desc())
            .limit(10)
        )
        rows = result.all()

        entries = []
        for pos, row in enumerate(rows, start=1):
            user = (await session.execute(
                select(User).where(User.telegram_id == row.referrer_id)
            )).scalar_one_or_none()
            name = user.full_name if user else str(row.referrer_id)
            entries.append(_(
                "referral_leaderboard_entry", lang,
                pos=pos, name=name, count=row.count
            ))

    text = _("referral_leaderboard", lang, entries="\n".join(entries) if entries else "—")
    await message.answer(text)
