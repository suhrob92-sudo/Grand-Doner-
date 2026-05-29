"""Courier delivery flow — location, distance calculation, payment initiation."""

import json
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.i18n import _
from utils.helpers import calculate_distance_km, delivery_cost_from_distance
from utils.decorators import handle_errors
from keyboards.reply import location_keyboard, remove_keyboard
from keyboards.inline import confirm_keyboard, main_menu_inline, order_type_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)


class DeliveryStates(StatesGroup):
    waiting_location = State()
    confirming_delivery = State()


@router.callback_query(F.data == "order_type:delivery")
@handle_errors
async def cb_order_delivery(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """Start delivery flow — ask for address."""
    await state.set_state(DeliveryStates.waiting_location)
    await state.update_data(order_type="delivery")
    await callback.message.answer(
        _("delivery_intro", lang),
        reply_markup=location_keyboard(lang),
    )
    await callback.answer()


@router.message(DeliveryStates.waiting_location, F.location)
@handle_errors
async def handle_delivery_location(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    """User sent geolocation for delivery."""
    lat = message.location.latitude
    lon = message.location.longitude

    distance_km = calculate_distance_km(
        lat, lon,
        settings.RESTAURANT_LAT,
        settings.RESTAURANT_LON,
    )
    address = f"{lat:.6f}, {lon:.6f}"
    await _process_delivery_address(message, state, lang, address, lat, lon, distance_km)


@router.message(DeliveryStates.waiting_location, F.text)
@handle_errors
async def handle_delivery_text_address(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    """User typed delivery address as text — use restaurant centre as fallback distance."""
    if message.text and message.text.startswith("/"):
        return
    address = message.text.strip()
    # Without geocoding, we assume 3 km (first zone) for text addresses
    # In production, integrate a geocoding API here
    distance_km = 3.0
    await _process_delivery_address(message, state, lang, address, None, None, distance_km)


async def _process_delivery_address(
    message: Message,
    state: FSMContext,
    lang: str,
    address: str,
    lat: float | None,
    lon: float | None,
    distance_km: float,
) -> None:
    """Calculate delivery cost and ask user to confirm."""
    await message.answer(_("delivery_calculating", lang), reply_markup=remove_keyboard())

    delivery_cost = delivery_cost_from_distance(distance_km)
    if delivery_cost is None:
        await message.answer(_("delivery_too_far", lang), reply_markup=main_menu_inline(lang))
        await state.clear()
        return

    from handlers.cart import get_cart, cart_total
    cart = await get_cart(message.from_user.id)
    subtotal = cart_total(cart)
    total_with_delivery = subtotal + delivery_cost

    await state.update_data(
        delivery_address=address,
        delivery_lat=lat,
        delivery_lon=lon,
        delivery_distance=distance_km,
        delivery_cost=delivery_cost,
    )
    await state.set_state(DeliveryStates.confirming_delivery)

    text = _("delivery_cost_info", lang,
             address=address,
             distance=round(distance_km, 1),
             cost=delivery_cost // 100,
             total=total_with_delivery // 100)
    kb = confirm_keyboard("delivery:confirm", "delivery:cancel", lang)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "delivery:confirm", DeliveryStates.confirming_delivery)
@handle_errors
async def cb_delivery_confirm(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    """User confirmed delivery address — proceed to payment."""
    await callback.message.edit_text(_("payment_intro", lang, amount=0))  # placeholder
    from handlers.payment import initiate_payment
    await initiate_payment(callback, state, lang)
    await callback.answer()


@router.callback_query(F.data == "delivery:cancel")
@handle_errors
async def cb_delivery_cancel(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    await state.clear()
    await callback.message.edit_text(
        _("choose_order_type", lang),
        reply_markup=order_type_keyboard(lang),
    )
    await callback.answer()
