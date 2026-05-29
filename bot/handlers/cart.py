"""Shopping cart handler — uses Redis to store cart per user."""

import json
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from redis.asyncio import Redis
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.product import Product
from models.promo import PromoCode, PromoUsage
from models.user import User
from utils.i18n import _
from utils.decorators import handle_errors
from utils.helpers import format_price
from keyboards.inline import cart_keyboard, cart_items_keyboard, order_type_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)

_redis_client: Redis | None = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


async def get_cart(user_id: int) -> dict:
    """Load cart from Redis. Returns {product_id_str: {name, price, qty}}."""
    redis = get_redis()
    data = await redis.get(cart_key(user_id))
    if data:
        return json.loads(data)
    return {}


async def save_cart(user_id: int, cart: dict) -> None:
    redis = get_redis()
    await redis.setex(cart_key(user_id), 86400, json.dumps(cart))


async def clear_cart(user_id: int) -> None:
    redis = get_redis()
    await redis.delete(cart_key(user_id))


async def add_to_cart(user_id: int, product_id: int, qty: int = 1) -> None:
    cart = await get_cart(user_id)
    key = str(product_id)
    if key in cart:
        cart[key]["qty"] += qty
    else:
        async with AsyncSessionLocal() as session:
            product = (await session.execute(
                select(Product).where(Product.id == product_id)
            )).scalar_one_or_none()
        if not product:
            return
        cart[key] = {
            "name": product.name_ru,
            "name_uz": product.name_uz,
            "price": product.price,
            "qty": qty,
        }
    await save_cart(user_id, cart)


def cart_total(cart: dict) -> int:
    """Total in kopecks."""
    return sum(item["price"] * item["qty"] for item in cart.values())


class CartStates(StatesGroup):
    entering_promo = State()


@router.callback_query(F.data.startswith("cart:add:"))
@handle_errors
async def cb_add_to_cart(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Add a product to cart from product card."""
    if not db_user:
        await callback.answer(_("user_not_registered", lang), show_alert=True)
        return
    parts = callback.data.split(":")
    product_id = int(parts[2])
    qty = int(parts[3]) if len(parts) > 3 else 1

    await add_to_cart(callback.from_user.id, product_id, qty)

    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one_or_none()
    name = product.get_name(lang) if product else str(product_id)
    await callback.answer(_("item_added_to_cart", lang, name=name), show_alert=False)


async def show_cart(callback: CallbackQuery, lang: str) -> None:
    """Display cart contents."""
    user_id = callback.from_user.id
    cart = await get_cart(user_id)

    if not cart:
        await callback.message.edit_text(
            _("cart_empty", lang),
            reply_markup=cart_keyboard(lang),
        )
        await callback.answer()
        return

    lines = [_("cart_title", lang)]
    for key, item in cart.items():
        name = item.get("name_uz", item["name"]) if lang == "uz" else item["name"]
        subtotal = item["price"] * item["qty"] // 100
        lines.append(_("cart_item_line", lang, name=name, qty=item["qty"], subtotal=subtotal))

    total_kopecks = cart_total(cart)
    lines.append(_("cart_total", lang, total=total_kopecks // 100))

    # Bonus info
    redis = get_redis()
    promo_data = await redis.get(f"cart_promo:{user_id}")
    bonus_data = await redis.get(f"cart_bonus:{user_id}")

    has_promo = bool(promo_data)
    if has_promo:
        promo_info = json.loads(promo_data)
        lines.append(_("cart_promo_applied", lang,
                       code=promo_info["code"], discount=promo_info["discount"] // 100))

    # Check if user has bonus points
    async with AsyncSessionLocal() as session:
        db_user = (await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )).scalar_one_or_none()
    has_bonus = db_user and db_user.bonus_points > 0

    if has_bonus:
        max_bonus = min(db_user.bonus_points, int(total_kopecks * settings.MAX_BONUS_PERCENT / 100 / 100))
        lines.append(_("cart_bonus_available", lang, points=db_user.bonus_points, max=max_bonus))

    text = "\n".join(lines)
    items_kb = cart_items_keyboard(list(cart.items()), lang)
    action_kb = cart_keyboard(lang, has_promo=has_promo, has_bonus=has_bonus)

    await callback.message.edit_text(text, reply_markup=action_kb)
    await callback.answer()


@router.callback_query(F.data == "main:cart")
@handle_errors
async def cb_show_cart(callback: CallbackQuery, lang: str, **kwargs) -> None:
    await show_cart(callback, lang)


@router.callback_query(F.data == "cart:clear")
@handle_errors
async def cb_clear_cart(callback: CallbackQuery, lang: str, **kwargs) -> None:
    await clear_cart(callback.from_user.id)
    redis = get_redis()
    await redis.delete(f"cart_promo:{callback.from_user.id}")
    await redis.delete(f"cart_bonus:{callback.from_user.id}")
    await callback.message.edit_text(_("cart_cleared", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("cart:inc:"))
@handle_errors
async def cb_cart_inc(callback: CallbackQuery, lang: str, **kwargs) -> None:
    key = callback.data.split(":")[2]
    user_id = callback.from_user.id
    cart = await get_cart(user_id)
    if key in cart:
        cart[key]["qty"] = min(cart[key]["qty"] + 1, 20)
        await save_cart(user_id, cart)
    await show_cart(callback, lang)


@router.callback_query(F.data.startswith("cart:dec:"))
@handle_errors
async def cb_cart_dec(callback: CallbackQuery, lang: str, **kwargs) -> None:
    key = callback.data.split(":")[2]
    user_id = callback.from_user.id
    cart = await get_cart(user_id)
    if key in cart:
        if cart[key]["qty"] > 1:
            cart[key]["qty"] -= 1
        else:
            del cart[key]
        await save_cart(user_id, cart)
    await show_cart(callback, lang)


@router.callback_query(F.data == "cart:promo")
@handle_errors
async def cb_enter_promo(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    await state.set_state(CartStates.entering_promo)
    await callback.message.answer(_("enter_promo", lang))
    await callback.answer()


@router.message(CartStates.entering_promo)
@handle_errors
async def handle_promo_input(message: Message, state: FSMContext, lang: str, db_user: User | None = None) -> None:
    """Validate and apply promo code."""
    code = message.text.strip().upper()
    user_id = message.from_user.id

    cart = await get_cart(user_id)
    total_kopecks = cart_total(cart)

    async with AsyncSessionLocal() as session:
        from datetime import datetime
        promo = (await session.execute(
            select(PromoCode).where(
                PromoCode.code == code,
                PromoCode.is_active == True,
            )
        )).scalar_one_or_none()

        if not promo:
            await message.answer(_("promo_invalid", lang))
            await state.clear()
            return

        now = datetime.utcnow()
        if promo.valid_from and promo.valid_from > now:
            await message.answer(_("promo_invalid", lang))
            await state.clear()
            return
        if promo.valid_to and promo.valid_to < now:
            await message.answer(_("promo_invalid", lang))
            await state.clear()
            return
        if promo.min_order_amount and total_kopecks < promo.min_order_amount:
            await message.answer(_("promo_min_order", lang, amount=promo.min_order_amount // 100))
            await state.clear()
            return
        if promo.max_uses and promo.used_count >= promo.max_uses:
            await message.answer(_("promo_invalid", lang))
            await state.clear()
            return

        # Check per-user usage
        if db_user:
            user_usage_count = (await session.execute(
                select(PromoUsage).where(
                    PromoUsage.promo_id == promo.id,
                    PromoUsage.user_id == db_user.id,
                )
            )).scalars().all()
            if len(user_usage_count) >= promo.max_uses_per_user:
                await message.answer(_("promo_invalid", lang))
                await state.clear()
                return

        # Calculate discount
        if promo.discount_type == "percent":
            discount = int(total_kopecks * promo.discount_value / 100)
        else:
            discount = min(promo.discount_value, total_kopecks)

    redis = get_redis()
    await redis.setex(
        f"cart_promo:{user_id}",
        86400,
        json.dumps({"code": code, "discount": discount, "promo_id": promo.id}),
    )

    await message.answer(_("promo_valid", lang, discount=discount // 100))
    await state.clear()


@router.callback_query(F.data == "cart:bonus")
@handle_errors
async def cb_use_bonus(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Toggle bonus points usage."""
    if not db_user or db_user.bonus_points <= 0:
        await callback.answer(_("not_enough_bonus", lang), show_alert=True)
        return

    user_id = callback.from_user.id
    redis = get_redis()
    existing = await redis.get(f"cart_bonus:{user_id}")

    if existing:
        await redis.delete(f"cart_bonus:{user_id}")
        await callback.answer(_("bonus_removed", lang))
    else:
        cart = await get_cart(user_id)
        total_kopecks = cart_total(cart)
        max_bonus_kopecks = int(total_kopecks * settings.MAX_BONUS_PERCENT / 100)
        bonus_to_use = min(db_user.bonus_points * 100, max_bonus_kopecks)  # 1 point = 1 rub
        await redis.setex(f"cart_bonus:{user_id}", 86400, str(bonus_to_use))
        points_used = bonus_to_use // 100
        await callback.answer(
            _("bonus_applied", lang, points=points_used, amount=points_used),
            show_alert=True,
        )

    await show_cart(callback, lang)


@router.callback_query(F.data == "cart:checkout")
@handle_errors
async def cb_checkout(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    """Move to order type selection."""
    if not db_user:
        await callback.answer(_("user_not_registered", lang), show_alert=True)
        return
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.answer(_("cart_empty", lang), show_alert=True)
        return

    await callback.message.edit_text(
        _("choose_order_type", lang),
        reply_markup=order_type_keyboard(lang),
    )
    await callback.answer()
