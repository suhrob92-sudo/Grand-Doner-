"""Admin order management — list, view, status change, cancel+refund, CSV export."""

import csv
import io
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from services.yookassa import cancel_payment
from utils.i18n import _
from utils.helpers import format_datetime
from utils.decorators import handle_errors
from keyboards.inline import admin_order_keyboard, admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)

ORDER_STATUS_LABELS = {
    "pending": "⏳ Ожидает",
    "paid": "✅ Оплачен",
    "preparing": "👨‍🍳 Готовится",
    "ready": "🎉 Готов",
    "on_the_way": "🚚 В пути",
    "completed": "✅ Выполнен",
    "cancelled": "❌ Отменён",
}


@router.callback_query(F.data == "admin:orders")
@handle_errors
async def cb_admin_orders(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .where(Order.status.not_in(["completed", "cancelled"]))
            .order_by(Order.created_at.desc())
            .limit(20)
        )
        orders = result.scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for o in orders:
        status_label = ORDER_STATUS_LABELS.get(o.status, o.status)
        builder.button(
            text=f"{status_label} #{o.order_number} — {o.total // 100} ₽",
            callback_data=f"admin:order_detail:{o.id}",
        )
    builder.row(InlineKeyboardButton(text="📥 Экспорт CSV", callback_data="admin:orders_csv"))
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await callback.message.edit_text(
        _("orders_list_title", lang),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:order_detail:"))
@handle_errors
async def cb_order_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    order_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).scalar_one_or_none()
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        customer = (await session.execute(
            select(User).where(User.id == order.user_id)
        )).scalar_one()
        items_result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = items_result.scalars().all()

    items_text = "\n".join(f"  • {i.name_snapshot} × {i.quantity} = {i.subtotal // 100} ₽" for i in items)
    text = _("order_detail", lang,
             number=order.order_number,
             customer=customer.full_name,
             phone=customer.phone or "—",
             date=format_datetime(order.created_at),
             order_type=order.order_type,
             address=order.delivery_address or "Самовывоз",
             items=items_text,
             total=order.total // 100,
             status=ORDER_STATUS_LABELS.get(order.status, order.status))

    await callback.message.edit_text(text, reply_markup=admin_order_keyboard(order_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:order_status:"))
@handle_errors
async def cb_change_order_status(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    parts = callback.data.split(":")
    order_id = int(parts[2])
    new_status = parts[3]

    async with AsyncSessionLocal() as session:
        order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).scalar_one()
        order.status = new_status
        await session.commit()
        customer = (await session.execute(
            select(User).where(User.id == order.user_id)
        )).scalar_one()

    # Notify customer
    status_key = f"status_{new_status}" if f"status_{new_status}" in ["status_paid","status_preparing","status_ready","status_on_the_way","status_completed","status_cancelled"] else "status_paid"
    try:
        await callback.bot.send_message(
            customer.telegram_id,
            _("order_status_update", customer.language,
              order_number=order.order_number,
              status=_(status_key, customer.language)),
        )
    except Exception:
        pass

    await callback.answer(f"Статус изменён → {new_status}", show_alert=True)
    await cb_order_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:order_cancel:"))
@handle_errors
async def cb_cancel_order(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    order_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).scalar_one()
        order.status = "cancelled"
        payment_id = order.payment_id
        await session.commit()
        customer = (await session.execute(
            select(User).where(User.id == order.user_id)
        )).scalar_one()

    if payment_id:
        await cancel_payment(payment_id)

    try:
        await callback.bot.send_message(
            customer.telegram_id,
            _("status_cancelled", customer.language),
        )
    except Exception:
        pass

    await callback.answer(_("order_cancelled_refund", lang), show_alert=True)
    await cb_admin_orders(callback, lang)


@router.callback_query(F.data == "admin:orders_csv")
@handle_errors
async def cb_export_csv(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        orders = (await session.execute(
            select(Order).order_by(Order.created_at.desc()).limit(500)
        )).scalars().all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["#", "Номер", "Дата", "Тип", "Итого", "Статус", "Адрес"])
    for o in orders:
        writer.writerow([
            o.id, o.order_number,
            format_datetime(o.created_at),
            o.order_type,
            o.total // 100,
            o.status,
            o.delivery_address or "Самовывоз",
        ])

    raw = buf.getvalue().encode("utf-8-sig")
    await callback.message.answer_document(
        document=BufferedInputFile(raw, filename="orders.csv"),
        caption="📥 Экспорт заказов",
    )
    await callback.answer()
