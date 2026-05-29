"""Admin statistics panel."""

import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.statistics import get_revenue_and_orders, get_top_products, get_top_customers
from models.base import AsyncSessionLocal
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "admin:stats")
@handle_errors
async def cb_admin_stats(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сегодня", callback_data="stats_period:today")
    builder.button(text="📅 Неделя", callback_data="stats_period:week")
    builder.button(text="📅 Месяц", callback_data="stats_period:month")
    builder.button(text="🔥 Топ товаров", callback_data="stats_period:top_products")
    builder.button(text="🏆 Топ клиентов", callback_data="stats_period:top_customers")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(2)

    await callback.message.edit_text(_("stats_title", lang), reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("stats_period:"))
@handle_errors
async def cb_stats_period(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    period = callback.data.split(":")[1]
    now = datetime.utcnow()

    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Сегодня"
    elif period == "week":
        start = now - timedelta(days=7)
        period_label = "7 дней"
    elif period == "month":
        start = now - timedelta(days=30)
        period_label = "30 дней"
    elif period == "top_products":
        async with AsyncSessionLocal() as session:
            products = await get_top_products(session)
        entries = "\n".join(f"{i+1}. {p['name']} — {p['qty']} шт." for i, p in enumerate(products))
        await callback.message.edit_text(
            _("top_products", lang, entries=entries or "—"),
            reply_markup=admin_back_keyboard(lang),
        )
        await callback.answer()
        return
    elif period == "top_customers":
        async with AsyncSessionLocal() as session:
            customers = await get_top_customers(session)
        entries = "\n".join(
            f"{i+1}. {c['name']} — {c['spent'] // 100} ₽" for i, c in enumerate(customers)
        )
        await callback.message.edit_text(
            _("top_customers", lang, entries=entries or "—"),
            reply_markup=admin_back_keyboard(lang),
        )
        await callback.answer()
        return
    else:
        start = now - timedelta(days=7)
        period_label = "7 дней"

    async with AsyncSessionLocal() as session:
        from services.statistics import get_dashboard_stats
        stats = await get_revenue_and_orders(session, start, now)
        dashboard = await get_dashboard_stats(session)

    text = _("stats_detail", lang,
             period=period_label,
             revenue=stats["revenue"] // 100,
             orders=stats["orders"],
             completed=stats["completed"],
             cancelled=stats["cancelled"],
             avg_order=stats["avg_order"] // 100,
             delivery_count=stats["delivery_count"],
             pickup_count=stats["pickup_count"],
             taxi_count=stats["taxi_count"],
             bonus_issued=dashboard["bonus_issued"],
             bonus_used=dashboard["bonus_used"])

    await callback.message.edit_text(text, reply_markup=admin_back_keyboard(lang))
    await callback.answer()
