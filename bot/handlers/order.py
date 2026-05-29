"""Order creation — pickup flow and shared order finalization logic."""

import json
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from models.bonus import BonusTransaction
from models.referral import Referral
from models.promo import PromoCode, PromoUsage
from utils.i18n import _
from utils.helpers import generate_order_number
from utils.decorators import handle_errors
from keyboards.inline import pickup_time_keyboard, order_type_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)


class PickupStates(StatesGroup):
    entering_custom_time = State()


@router.callback_query(F.data == "order_type:pickup")
@handle_errors
async def cb_order_pickup(callback: CallbackQuery, lang: str, **kwargs) -> None:
    await callback.message.edit_text(
        _("pickup_info", lang,
          address=settings.RESTAURANT_ADDRESS,
          phone=settings.RESTAURANT_PHONE),
        reply_markup=pickup_time_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pickup_time:"))
@handle_errors
async def cb_pickup_time(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    choice = callback.data.split(":")[1]
    if choice == "custom":
        await state.set_state(PickupStates.entering_custom_time)
        await callback.message.answer(_("enter_pickup_time", lang))
        await callback.answer()
        return

    time_labels = {"now": "сейчас", "15": "через 15 мин", "30": "через 30 мин"}
    pickup_time = time_labels.get(choice, "сейчас")
    await state.update_data(pickup_time=pickup_time, order_type="pickup")
    await callback.message.edit_text(_("pickup_confirmed", lang, time=pickup_time))
    await callback.answer()
    await _proceed_to_payment(callback, state, lang)


@router.message(PickupStates.entering_custom_time)
@handle_errors
async def handle_custom_pickup_time(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    from utils.validators import is_valid_time
    time_str = message.text.strip()
    if not is_valid_time(time_str):
        await message.answer(_("enter_pickup_time", lang))
        return
    await state.update_data(pickup_time=time_str, order_type="pickup")
    await message.answer(_("pickup_confirmed", lang, time=time_str))
    await _proceed_to_payment_msg(message, state, lang)


async def _proceed_to_payment(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    """Trigger payment handler after order type is confirmed."""
    from handlers.payment import initiate_payment
    await initiate_payment(callback, state, lang)


async def _proceed_to_payment_msg(message: Message, state: FSMContext, lang: str) -> None:
    from handlers.payment import initiate_payment_msg
    await initiate_payment_msg(message, state, lang)


async def create_order_in_db(
    session,
    user: User,
    cart: dict,
    order_type: str,
    promo_info: dict | None,
    bonus_kopecks: int,
    delivery_cost: int = 0,
    delivery_address: str | None = None,
    delivery_lat: float | None = None,
    delivery_lon: float | None = None,
    delivery_distance_km: float | None = None,
    pickup_time: str | None = None,
) -> Order:
    """Create an Order + OrderItems in the database and return the Order."""
    subtotal = sum(item["price"] * item["qty"] for item in cart.values())
    discount = promo_info["discount"] if promo_info else 0
    total = max(0, subtotal + delivery_cost - discount - bonus_kopecks)

    order = Order(
        order_number="TMP",
        user_id=user.id,
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        discount_amount=discount,
        bonus_used=bonus_kopecks // 100,
        total=total,
        order_type=order_type,
        delivery_address=delivery_address,
        delivery_lat=delivery_lat,
        delivery_lon=delivery_lon,
        delivery_distance_km=delivery_distance_km,
        pickup_time=pickup_time,
        promo_code=promo_info["code"] if promo_info else None,
        status="pending",
    )
    session.add(order)
    await session.flush()  # get order.id

    order.order_number = generate_order_number(order.id)

    for product_id_str, item in cart.items():
        oi = OrderItem(
            order_id=order.id,
            product_id=int(product_id_str),
            name_snapshot=item["name"],
            price_snapshot=item["price"],
            quantity=item["qty"],
        )
        session.add(oi)

    # Record promo usage
    if promo_info and "promo_id" in promo_info:
        usage = PromoUsage(
            promo_id=promo_info["promo_id"],
            user_id=user.id,
            order_id=order.id,
        )
        session.add(usage)
        promo = (await session.execute(
            select(PromoCode).where(PromoCode.id == promo_info["promo_id"])
        )).scalar_one_or_none()
        if promo:
            promo.used_count += 1

    await session.commit()
    await session.refresh(order)
    return order


async def finalize_paid_order(session, order: Order, bot) -> None:
    """Called after payment confirmed — accrue bonuses, pay referral, notify."""
    user_result = await session.execute(select(User).where(User.id == order.user_id))
    user = user_result.scalar_one()

    # Update order status
    order.status = "paid"
    order.is_paid = True
    order.paid_at = datetime.utcnow()

    # Accrue bonus points: 5 per 100 ₽
    bonus_earned = (order.total // 100) // 100 * settings.BONUS_RATE
    if bonus_earned > 0:
        user.bonus_points += bonus_earned
        user.total_spent += order.total
        txn = BonusTransaction(
            user_id=user.id,
            amount=bonus_earned,
            reason="order_accrual",
            order_id=order.id,
        )
        session.add(txn)
        order.bonus_accrued = bonus_earned

    # Deduct used bonus points
    if order.bonus_used > 0:
        user.bonus_points = max(0, user.bonus_points - order.bonus_used)
        session.add(BonusTransaction(
            user_id=user.id,
            amount=-order.bonus_used,
            reason="order_spend",
            order_id=order.id,
        ))

    # Handle referral bonus for referrer (only on first order of referred user)
    if user.referred_by and not user.referral_bonus_received:
        # Check if this is user's first completed order
        all_paid_orders_count = (await session.execute(
            select(Order).where(Order.user_id == user.id, Order.is_paid == True)
        )).scalars().all()
        if len(all_paid_orders_count) == 1:  # this is the first one
            referrer_result = await session.execute(
                select(User).where(User.telegram_id == user.referred_by)
            )
            referrer = referrer_result.scalar_one_or_none()
            if referrer:
                referrer.bonus_points += 150
                session.add(BonusTransaction(
                    user_id=referrer.id,
                    amount=150,
                    reason="referral",
                    order_id=order.id,
                ))
                user.referral_bonus_received = True
                # Notify referrer
                try:
                    await bot.send_message(
                        referrer.telegram_id,
                        _("referral_bonus_received", referrer.language),
                    )
                except Exception:
                    pass

    await session.commit()
    await session.refresh(order)
