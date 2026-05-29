"""Yandex Taxi flow — request location, order taxi, poll status."""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models.user import User
from services.yandex_taxi import create_taxi_order, get_order_status, cancel_order, TAXI_STATUS_MAP
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.reply import location_keyboard, main_menu_keyboard
from keyboards.inline import main_menu_inline
from config import settings
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.order import Order
from handlers.cart import get_cart, get_redis

router = Router()
logger = logging.getLogger(__name__)


class TaxiStates(StatesGroup):
    waiting_location = State()
    taxi_in_progress = State()


@router.callback_query(F.data == "order_type:taxi")
@handle_errors
async def cb_order_taxi(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """Ask user for pickup location."""
    await state.set_state(TaxiStates.waiting_location)
    await state.update_data(order_type="taxi")
    await callback.message.answer(
        _("taxi_intro", lang),
        reply_markup=location_keyboard(lang),
    )
    await callback.answer()


@router.message(TaxiStates.waiting_location, F.location)
@handle_errors
async def handle_taxi_location(message: Message, state: FSMContext, lang: str, db_user: User | None = None) -> None:
    """User sent geolocation — order a taxi to the restaurant."""
    if not db_user:
        await message.answer(_("user_not_registered", lang))
        return

    lat = message.location.latitude
    lon = message.location.longitude
    address = f"{lat:.6f},{lon:.6f}"
    await _order_taxi(message, state, lang, db_user, lat, lon, address)


@router.message(TaxiStates.waiting_location, F.text)
@handle_errors
async def handle_taxi_address_text(message: Message, state: FSMContext, lang: str, db_user: User | None = None) -> None:
    """User typed their address as text."""
    if not db_user:
        await message.answer(_("user_not_registered", lang))
        return
    if message.text and message.text.startswith("/"):
        return  # ignore commands in this state
    address = message.text.strip()
    # Use restaurant coords as "from" placeholder when only address text is given
    await _order_taxi(message, state, lang, db_user,
                      lat=settings.RESTAURANT_LAT, lon=settings.RESTAURANT_LON,
                      address=address)


async def _order_taxi(
    message: Message,
    state: FSMContext,
    lang: str,
    user: User,
    lat: float,
    lon: float,
    address: str,
) -> None:
    """Call Yandex Taxi API and start polling for status updates."""
    from keyboards.reply import remove_keyboard
    await message.answer(_("taxi_ordering", lang), reply_markup=remove_keyboard())

    try:
        taxi_info = await create_taxi_order(
            from_lat=lat,
            from_lon=lon,
            from_address=address,
            user_phone=user.phone or "",
        )
    except Exception as exc:
        logger.warning("Taxi order failed: %s", exc)
        await message.answer(_("taxi_error", lang))
        await state.clear()
        return

    # Create order in DB (taxi orders go straight to preparing after taxi confirmed)
    cart = await get_cart(message.from_user.id)
    redis = get_redis()
    import json
    promo_raw = await redis.get(f"cart_promo:{message.from_user.id}")
    bonus_raw = await redis.get(f"cart_bonus:{message.from_user.id}")
    promo_info = json.loads(promo_raw) if promo_raw else None
    bonus_kopecks = int(bonus_raw) if bonus_raw else 0

    async with AsyncSessionLocal() as session:
        db_user = (await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )).scalar_one()

        from handlers.order import create_order_in_db
        order = await create_order_in_db(
            session=session,
            user=db_user,
            cart=cart,
            order_type="taxi",
            promo_info=promo_info,
            bonus_kopecks=bonus_kopecks,
            delivery_address=address,
            delivery_lat=lat,
            delivery_lon=lon,
        )
        order.yandex_taxi_order_id = taxi_info["order_id"]
        order.taxi_status = taxi_info["status"]
        order.status = "paid"
        order.is_paid = True
        await session.commit()
        order_id = order.id
        order_number = order.order_number

    from handlers.cart import clear_cart
    await clear_cart(message.from_user.id)

    text = _("taxi_ordered", lang,
             car=taxi_info["car_model"],
             color=taxi_info["car_color"],
             driver=taxi_info["driver_name"],
             eta=taxi_info["eta_minutes"],
             plate=taxi_info["car_plate"])
    await message.answer(text)

    # Send to kitchen notification to admin
    for admin_id in settings.admin_ids_list:
        try:
            await message.bot.send_message(
                admin_id,
                f"🚕 Заказ такси #{order_number}\n👤 {db_user.full_name}\n📞 {db_user.phone}\n💰 {order.total // 100} ₽",
            )
        except Exception:
            pass

    await state.clear()

    # Start background polling for taxi status
    asyncio.create_task(
        _poll_taxi_status(
            bot=message.bot,
            user_telegram_id=message.from_user.id,
            order_id=order_id,
            taxi_order_id=taxi_info["order_id"],
            lang=lang,
        )
    )


async def _poll_taxi_status(
    bot: Bot,
    user_telegram_id: int,
    order_id: int,
    taxi_order_id: str,
    lang: str,
    max_polls: int = 60,
) -> None:
    """Poll Yandex Taxi every 60 seconds and push status updates to the user."""
    prev_status = None
    for _ in range(max_polls):
        await asyncio.sleep(60)
        try:
            status = await get_order_status(taxi_order_id)
            if status != prev_status:
                prev_status = status
                human_status = TAXI_STATUS_MAP.get(status, status)
                try:
                    await bot.send_message(user_telegram_id, human_status)
                except Exception:
                    pass

                # Update DB
                async with AsyncSessionLocal() as session:
                    order = (await session.execute(
                        select(Order).where(Order.id == order_id)
                    )).scalar_one_or_none()
                    if order:
                        order.taxi_status = status
                        await session.commit()

                if status in ("complete", "cancelled", "failed"):
                    break
        except Exception as exc:
            logger.warning("_poll_taxi_status error: %s", exc)
            break
