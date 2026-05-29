"""Admin review moderation — publish, hide, reply."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.review import Review
from models.user import User
from utils.i18n import _
from utils.helpers import stars
from utils.decorators import handle_errors
from keyboards.inline import admin_review_keyboard, admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class ReviewReplyStates(StatesGroup):
    entering_reply = State()


@router.callback_query(F.data == "admin:reviews")
@handle_errors
async def cb_admin_reviews(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Review).order_by(Review.created_at.desc()).limit(30)
        )
        reviews = result.scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for r in reviews:
        status = "✅" if r.is_published else "🙈"
        comment_short = (r.comment or "—")[:30]
        builder.button(
            text=f"{status} ⭐{r.rating} — {comment_short}",
            callback_data=f"admin:review_detail:{r.id}",
        )
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await callback.message.edit_text(_("admin_reviews_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:review_detail:"))
@handle_errors
async def cb_review_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    review_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        review = (await session.execute(
            select(Review).where(Review.id == review_id)
        )).scalar_one_or_none()
        if not review:
            await callback.answer("Не найден", show_alert=True)
            return
        user = (await session.execute(
            select(User).where(User.id == review.user_id)
        )).scalar_one_or_none()

    name = user.full_name if user else "—"
    text = (
        f"⭐ {stars(review.rating)} — <b>{name}</b>\n"
        f"{review.comment or '—'}\n"
        f"{'✅ Опубликован' if review.is_published else '🙈 Скрыт'}"
    )
    if review.admin_reply:
        text += f"\n\n💬 Ответ: {review.admin_reply}"

    await callback.message.edit_text(
        text,
        reply_markup=admin_review_keyboard(review_id, review.is_published, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:review_pub:"))
@handle_errors
async def cb_review_publish(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    review_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        review = (await session.execute(
            select(Review).where(Review.id == review_id)
        )).scalar_one()
        review.is_published = True
        await session.commit()
    await callback.answer(_("review_published", lang), show_alert=True)
    await cb_review_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:review_hide:"))
@handle_errors
async def cb_review_hide(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    review_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        review = (await session.execute(
            select(Review).where(Review.id == review_id)
        )).scalar_one()
        review.is_published = False
        await session.commit()
    await callback.answer(_("review_hidden", lang), show_alert=True)
    await cb_review_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:review_reply:"))
@handle_errors
async def cb_review_reply_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    review_id = int(callback.data.split(":")[2])
    await state.update_data(reply_review_id=review_id)
    await state.set_state(ReviewReplyStates.entering_reply)
    await callback.message.answer(_("enter_review_reply", lang))
    await callback.answer()


@router.message(ReviewReplyStates.entering_reply)
@handle_errors
async def handle_review_reply(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    data = await state.get_data()
    review_id = data["reply_review_id"]
    reply_text = message.text.strip()

    async with AsyncSessionLocal() as session:
        review = (await session.execute(
            select(Review).where(Review.id == review_id)
        )).scalar_one()
        review.admin_reply = reply_text
        await session.commit()

        customer = (await session.execute(
            select(User).where(User.id == review.user_id)
        )).scalar_one()

    try:
        await message.bot.send_message(
            customer.telegram_id,
            _("review_reply", customer.language, reply=reply_text),
        )
    except Exception:
        pass

    await message.answer(_("review_reply_sent", lang))
    await state.clear()
