"""Payment handler — YooKassa invoice creation and webhook processing."""

import json
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiohttp import web
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.order import Order
from models.user import User
from services.yookassa import create_payment, cancel_payment, parse_webhook_event
from services.qr_generator import generate_order_qr
from handlers.cart import get_cart, clear_cart, get_redis
from utils.i18n import _
from utils.helpers import format_price
from utils.decorators import handle_errors
from keyboards.inline import payment_keyboard, main_menu_inline
from config import settings

router = Router()
logger = logging.getLogger(__name__)

# Bot instance injected at startup (set from main.py)
_bot: Bot | None = None


def set_bot(bot: Bot) -> None:
    global _bot
    _bot = bot


async def initiate_payment(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    """Build and persist the order then send the YooKassa payment link."""
    data = await state.get_data()
    user_id = callback.from_user.id
    cart = await get_cart(user_id)
    if not cart:
        await callback.message.answer(_("cart_empty", lang))
        return

    redis = get_redis()
    promo_raw = await redis.get(f"cart_promo:{user_id}")
    bonus_raw = await redis.get(f"cart_bonus:{user_id}")
    promo_info = json.loads(promo_raw) if promo_raw else None
    bonus_kopecks = int(bonus_raw) if bonus_raw else 0

    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == user_id)
        )).scalar_one()

        from handlers.order import create_order_in_db
        order = await create_order_in_db(
            session=session,
            user=user,
            cart=cart,
            order_type=data.get("order_type", "pickup"),
            promo_info=promo_info,
            bonus_kopecks=bonus_kopecks,
            delivery_cost=data.get("delivery_cost", 0),
            delivery_address=data.get("delivery_address"),
            delivery_lat=data.get("delivery_lat"),
            delivery_lon=data.get("delivery_lon"),
            delivery_distance_km=data.get("delivery_distance"),
            pickup_time=data.get("pickup_time"),
        )

    await _send_payment_link(callback.message, order, user, lang)
    await state.clear()


async def initiate_payment_msg(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    user_id = message.from_user.id
    cart = await get_cart(user_id)
    if not cart:
        await message.answer(_("cart_empty", lang))
        return

    redis = get_redis()
    promo_raw = await redis.get(f"cart_promo:{user_id}")
    bonus_raw = await redis.get(f"cart_bonus:{user_id}")
    promo_info = json.loads(promo_raw) if promo_raw else None
    bonus_kopecks = int(bonus_raw) if bonus_raw else 0

    async with AsyncSessionLocal() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == user_id)
        )).scalar_one()

        from handlers.order import create_order_in_db
        order = await create_order_in_db(
            session=session,
            user=user,
            cart=cart,
            order_type=data.get("order_type", "pickup"),
            promo_info=promo_info,
            bonus_kopecks=bonus_kopecks,
            delivery_cost=data.get("delivery_cost", 0),
            delivery_address=data.get("delivery_address"),
            delivery_lat=data.get("delivery_lat"),
            delivery_lon=data.get("delivery_lon"),
            delivery_distance_km=data.get("delivery_distance"),
            pickup_time=data.get("pickup_time"),
        )

    await _send_payment_link(message, order, user, lang)
    await state.clear()


async def _send_payment_link(target, order: Order, user: User, lang: str) -> None:
    """Create YooKassa invoice and send payment link to user."""
    try:
        return_url = f"{settings.WEBHOOK_URL}/payment/return"
        payment_data = await create_payment(
            amount_kopecks=order.total,
            order_number=order.order_number,
            description=f"Заказ {order.order_number} — {settings.RESTAURANT_NAME}",
            return_url=return_url,
            customer_phone=user.phone,
        )
        async with AsyncSessionLocal() as session:
            db_order = (await session.execute(
                select(Order).where(Order.id == order.id)
            )).scalar_one()
            db_order.payment_id = payment_data["payment_id"]
            db_order.payment_url = payment_data["confirmation_url"]
            await session.commit()

        amount_rub = order.total // 100
        text = _("payment_intro", lang, amount=amount_rub)
        kb = payment_keyboard(lang, payment_data["confirmation_url"], amount_rub)
        await target.answer(text, reply_markup=kb)
    except Exception as exc:
        logger.exception("_send_payment_link error: %s", exc)
        await target.answer(_("error_occurred", lang))


@router.callback_query(F.data == "payment:cancel")
@handle_errors
async def cb_payment_cancel(callback: CallbackQuery, lang: str, **kwargs) -> None:
    await callback.message.edit_text(_("payment_cancelled", lang))
    await callback.answer()


async def yookassa_webhook(request: web.Request) -> web.Response:
    """aiohttp handler for YooKassa payment webhook."""
    try:
        body = await request.json()
        event = parse_webhook_event(body)
        logger.info("YooKassa webhook: %s", event)

        if event["event"] == "payment.succeeded" and event["order_number"]:
            await _process_payment_success(event["payment_id"], event["order_number"])
    except Exception as exc:
        logger.exception("YooKassa webhook error: %s", exc)

    return web.Response(text="ok")


async def _process_payment_success(payment_id: str, order_number: str) -> None:
    """Handle confirmed payment — update order, send QR, notify admin."""
    global _bot
    try:
        async with AsyncSessionLocal() as session:
            order = (await session.execute(
                select(Order).where(Order.order_number == order_number)
            )).scalar_one_or_none()
            if not order or order.is_paid:
                return

            user = (await session.execute(
                select(User).where(User.id == order.user_id)
            )).scalar_one()

            from handlers.order import finalize_paid_order
            await finalize_paid_order(session, order, _bot)

            await session.refresh(order)

        lang = user.language

        # Generate QR code
        async with AsyncSessionLocal() as session:
            from models.order_item import OrderItem
            items_result = await session.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            items = items_result.scalars().all()
            items_for_qr = [
                {"name": i.name_snapshot, "qty": i.quantity, "price": i.price_snapshot // 100}
                for i in items
            ]

        qr_buf = generate_order_qr(
            order_id=order.id,
            order_number=order.order_number,
            restaurant_name=settings.RESTAURANT_NAME,
            items=items_for_qr,
            total_kopecks=order.total,
            delivery_type=order.order_type,
            customer_phone=user.phone or "",
        )

        if _bot:
            # Send QR to customer
            text = _("payment_success", lang,
                     order_number=order.order_number,
                     amount=order.total // 100)
            from aiogram.types import BufferedInputFile
            await _bot.send_photo(
                user.telegram_id,
                photo=BufferedInputFile(qr_buf.read(), filename="qr.png"),
                caption=text,
            )

            # Clear cart
            await clear_cart(user.telegram_id)

            # Notify admin(s)
            items_text = "\n".join(f"  • {i['name']} × {i['qty']}" for i in items_for_qr)
            admin_text = _("order_confirmed_admin", "ru",
                           order_number=order.order_number,
                           customer=user.full_name,
                           phone=user.phone or "—",
                           order_type=order.order_type,
                           address=order.delivery_address or "Самовывоз",
                           items=items_text,
                           total=order.total // 100)
            for admin_id in settings.admin_ids_list:
                try:
                    await _bot.send_message(admin_id, admin_text)
                except Exception:
                    pass

            # If delivery order — notify couriers
            if order.order_type == "delivery":
                from handlers.courier import notify_couriers_new_order
                await notify_couriers_new_order(_bot, order, user, items_for_qr)

    except Exception as exc:
        logger.exception("_process_payment_success error: %s", exc)
