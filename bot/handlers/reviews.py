"""Customer review submission and public review listing."""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.review import Review
from models.order import Order
from models.user import User
from utils.i18n import _
from utils.helpers import format_datetime, stars
from utils.decorators import handle_errors
from keyboards.inline import review_comment_keyboard, back_to_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


class ReviewStates(StatesGroup):
    entering_comment = State()


async def show_reviews(callback: CallbackQuery, lang: str) -> None:
    """Display published reviews."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Review)
            .where(Review.is_published == True)
            .order_by(Review.created_at.desc())
            .limit(10)
        )
        reviews = result.scalars().all()

    if not reviews:
        await callback.message.edit_text(
            _("no_reviews", lang),
            reply_markup=back_to_main_keyboard(lang),
        )
        await callback.answer()
        return

    lines = [_("reviews_title", lang)]
    for r in reviews:
        async with AsyncSessionLocal() as session:
            user = (await session.execute(
                select(User).where(User.id == r.user_id)
            )).scalar_one_or_none()
        name = user.full_name if user else "—"
        comment = r.comment or "—"
        lines.append(_("review_item", lang,
                       rating=stars(r.rating),
                       name=name,
                       comment=comment,
                       date=format_datetime(r.created_at)))
        if r.admin_reply:
            lines.append(_("review_reply", lang, reply=r.admin_reply))
        lines.append("")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_to_main_keyboard(lang),
    )
    await callback.answer()


@router.message(Command("reviews"))
@handle_errors
async def cmd_reviews(message: Message, lang: str, **kwargs) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Review)
            .where(Review.is_published == True)
            .order_by(Review.created_at.desc())
            .limit(10)
        )
        reviews = result.scalars().all()

    if not reviews:
        await message.answer(_("no_reviews", lang))
        return

    lines = [_("reviews_title", lang)]
    for r in reviews:
        lines.append(f"⭐ {stars(r.rating)} — {r.comment or '—'}")
    await message.answer("\n".join(lines))


@router.callback_query(F.data.startswith("review:rate:"))
@handle_errors
async def cb_review_rate(callback: CallbackQuery, state: FSMContext, lang: str, db_user: User | None = None, **kwargs) -> None:
    """User selected a star rating."""
    parts = callback.data.split(":")
    order_id = int(parts[2])
    rating = int(parts[3])

    await state.update_data(review_order_id=order_id, review_rating=rating)

    await callback.message.edit_text(
        _("review_comment_prompt", lang),
        reply_markup=review_comment_keyboard(order_id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("review:comment:"))
@handle_errors
async def cb_review_want_comment(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    await state.set_state(ReviewStates.entering_comment)
    await callback.message.answer(_("enter_review_comment", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("review:skip:"))
@handle_errors
async def cb_review_skip_comment(callback: CallbackQuery, state: FSMContext, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Save review without a comment."""
    data = await state.get_data()
    order_id = data.get("review_order_id") or int(callback.data.split(":")[2])
    rating = data.get("review_rating", 5)
    await _save_review(callback.from_user.id, order_id, rating, None)
    await callback.message.edit_text(_("review_saved", lang))
    await state.clear()
    await callback.answer()


@router.message(ReviewStates.entering_comment)
@handle_errors
async def handle_review_comment(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    data = await state.get_data()
    order_id = data.get("review_order_id")
    rating = data.get("review_rating", 5)
    comment = message.text.strip()
    await _save_review(message.from_user.id, order_id, rating, comment)
    await message.answer(_("review_saved", lang))
    await state.clear()


async def _save_review(telegram_id: int, order_id: int, rating: int, comment: str | None) -> None:
    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if not user:
            return
        existing = (await session.execute(
            select(Review).where(Review.order_id == order_id, Review.user_id == user.id)
        )).scalar_one_or_none()
        if existing:
            return
        review = Review(
            user_id=user.id,
            order_id=order_id,
            rating=rating,
            comment=comment,
            is_published=False,
        )
        session.add(review)
        await session.commit()
