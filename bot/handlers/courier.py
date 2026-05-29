"""Courier-facing handlers — accept, depart, arrive, deliver."""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, and_
from models.base import AsyncSessionLocal
from models.order import Order
from models.user import User
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import courier_new_order_keyboard, courier_active_order_keyboard, admin_back_keyboard
from keyboards.reply import courier_menu_keyboard, main_menu_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)


async def notify_couriers_new_order(bot: Bot, order: Order, customer: User, items: list[dict]) -> None:
    """Broadcast new delivery order to all available couriers."""
    items_text = "\n".join(f"  • {i['name']} × {i['qty']}" for i in items)
    text = _(
        "new_delivery_notification", "ru",
        order_number=order.order_number,
        address=order.delivery_address or "—",
        phone=customer.phone or "—",
        items=items_text,
        total=order.total // 100,
    )
    kb = courier_new_order_keyboard(order.id, "ru")

    for courier_id in settings.courier_ids_list:
        try:
            await bot.send_message(courier_id, text, reply_markup=kb)
        except Exception as exc:
            logger.warning("Failed to notify courier %s: %s", courier_id, exc)

    # Also check couriers stored in DB
    async with AsyncSessionLocal() as session:
        db_couriers_result = await session.execute(
            select(User).where(User.is_courier == True, User.is_active == True)
        )
        db_couriers = db_couriers_result.scalars().all()
        for c in db_couriers:
            if c.telegram_id in settings.courier_ids_list:
                continue  # already notified
            try:
                lang = c.language
                courier_text = _(
                    "new_delivery_notification", lang,
                    order_number=order.order_number,
                    address=order.delivery_address or "—",
                    phone=customer.phone or "—",
                    items=items_text,
                    total=order.total // 100,
                )
                await bot.send_message(
                    c.telegram_id,
                    courier_text,
                    reply_markup=courier_new_order_keyboard(order.id, lang),
                )
            except Exception as exc:
                logger.warning("Failed to notify db courier %s: %s", c.telegram_id, exc)


@router.message(Command("courier_menu"))
@handle_errors
async def cmd_courier_menu(message: Message, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Show courier menu — only available for registered couriers."""
    if not db_user or (not db_user.is_courier and message.from_user.id not in settings.courier_ids_list):
        await message.answer(_("error_occurred", lang))
        return
    await message.answer(
        _("courier_menu", lang),
        reply_markup=courier_menu_keyboard(lang),
    )


@router.callback_query(F.data.startswith("courier:accept:"))
@handle_errors
async def cb_courier_accept(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Courier accepts a delivery order."""
    order_id = int(callback.data.split(":")[2])
    courier_telegram_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).scalar_one_or_none()

        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        if order.courier_id is not None:
            await callback.answer(_("order_already_taken", lang), show_alert=True)
            return
        if order.status not in ("paid", "preparing"):
            await callback.answer(_("order_already_taken", lang), show_alert=True)
            return

        # Find courier user record
        courier = (await session.execute(
            select(User).where(User.telegram_id == courier_telegram_id)
        )).scalar_one_or_none()

        courier_id_in_db = courier.id if courier else None
        order.courier_id = courier_id_in_db
        order.status = "on_the_way"
        await session.commit()
        await session.refresh(order)

        # Get customer
        customer = (await session.execute(
            select(User).where(User.id == order.user_id)
        )).scalar_one()

    # Notify courier
    await callback.message.edit_reply_markup(
        reply_markup=courier_active_order_keyboard(order_id, lang)
    )
    await callback.answer(_("order_accepted_courier", lang, order_number=order.order_number))

    # Notify customer
    courier_name = callback.from_user.full_name
    try:
        await callback.bot.send_message(
            customer.telegram_id,
            _("courier_accepted_client", customer.language, name=courier_name),
        )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(F.data.startswith("courier:departed:"))
@handle_errors
async def cb_courier_departed(callback: CallbackQuery, lang: str, **kwargs) -> None:
    order_id = int(callback.data.split(":")[2])
    await _update_courier_status(callback, order_id, "on_the_way", "courier_departed_msg", lang)


@router.callback_query(F.data.startswith("courier:arrived:"))
@handle_errors
async def cb_courier_arrived(callback: CallbackQuery, lang: str, **kwargs) -> None:
    order_id = int(callback.data.split(":")[2])
    await _update_courier_status(callback, order_id, "on_the_way", "courier_arrived_msg", lang)


@router.callback_query(F.data.startswith("courier:delivered:"))
@handle_errors
async def cb_courier_delivered(callback: CallbackQuery, lang: str, **kwargs) -> None:
    order_id = int(callback.data.split(":")[2])
    await _update_courier_status(callback, order_id, "completed", "order_delivered_msg", lang)

    # Schedule review request 30 minutes later
    import asyncio
    asyncio.create_task(_delayed_review_request(callback.bot, order_id))


async def _update_courier_status(
    callback: CallbackQuery,
    order_id: int,
    new_status: str,
    customer_msg_key: str,
    lang: str,
) -> None:
    async with AsyncSessionLocal() as session:
        order = (await session.execute(
            select(Order).where(Order.id == order_id)
        )).scalar_one_or_none()
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        order.status = new_status
        await session.commit()

        customer = (await session.execute(
            select(User).where(User.id == order.user_id)
        )).scalar_one()

    try:
        await callback.bot.send_message(
            customer.telegram_id,
            _(customer_msg_key, customer.language),
        )
    except Exception:
        pass
    await callback.answer("✅")


async def _delayed_review_request(bot: Bot, order_id: int, delay: int = 1800) -> None:
    """Send review request 30 minutes after order completion."""
    import asyncio
    await asyncio.sleep(delay)
    try:
        async with AsyncSessionLocal() as session:
            order = (await session.execute(
                select(Order).where(Order.id == order_id)
            )).scalar_one_or_none()
            if not order or order.review_sent:
                return
            customer = (await session.execute(
                select(User).where(User.id == order.user_id)
            )).scalar_one()
            order.review_sent = True
            await session.commit()

        from keyboards.inline import rating_keyboard
        await bot.send_message(
            customer.telegram_id,
            _("review_request", customer.language, order_number=order.order_number),
            reply_markup=rating_keyboard(order_id),
        )
    except Exception as exc:
        logger.warning("_delayed_review_request error: %s", exc)
