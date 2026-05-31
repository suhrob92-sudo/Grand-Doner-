"""Menu/catalog browsing handler."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.category import Category
from models.product import Product
from models.settings import BotSetting
from utils.i18n import _
from utils.decorators import handle_errors
from keyboards.inline import categories_keyboard, products_keyboard, product_card_keyboard, admin_back_keyboard

router = Router()
logger = logging.getLogger(__name__)

# In-memory page cache per user (product_id → current_page)
_page_cache: dict[int, int] = {}
# Temp qty state: user_id → {product_id: qty}
_qty_cache: dict[int, dict[int, int]] = {}


async def show_categories(callback: CallbackQuery, lang: str) -> None:
    """Display all active categories."""
    async with AsyncSessionLocal() as session:
        # Check maintenance mode
        setting = (await session.execute(
            select(BotSetting).where(BotSetting.key == "maintenance_mode")
        )).scalar_one_or_none()
        if setting and setting.value == "1":
            hours_setting = (await session.execute(
                select(BotSetting).where(BotSetting.key == "working_hours")
            )).scalar_one_or_none()
            hours = hours_setting.value if hours_setting else "10:00-22:00"
            await callback.message.edit_text(_("closed_message", lang, hours=hours))
            await callback.answer()
            return

        result = await session.execute(
            select(Category).where(Category.is_active == True).order_by(Category.sort_order)
        )
        categories = result.scalars().all()

    if not categories:
        await callback.message.edit_text(_("choose_category", lang))
        await callback.answer()
        return

    await callback.message.edit_text(
        _("choose_category", lang),
        reply_markup=categories_keyboard(categories, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
@handle_errors
async def cb_category(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show products in chosen category."""
    cat_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .where(Product.category_id == cat_id)
            .order_by(Product.sort_order)
        )
        products = result.scalars().all()
        cat = (await session.execute(
            select(Category).where(Category.id == cat_id)
        )).scalar_one_or_none()

    cat_name = cat.name_uz if lang == "uz" else cat.name_ru if cat else ""
    if not products:
        await callback.message.edit_text(
            _("no_products_in_category", lang),
            reply_markup=admin_back_keyboard(lang),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        _("choose_product", lang, category=cat_name),
        reply_markup=products_keyboard(products, lang, page=0, cat_id=cat_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod_page:"))
@handle_errors
async def cb_product_page(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Paginate through product list — cat_id encoded in callback data."""
    parts = callback.data.split(":")
    cat_id = int(parts[1])
    page = int(parts[2])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .where(Product.category_id == cat_id)
            .order_by(Product.sort_order)
        )
        products = result.scalars().all()
        cat = (await session.execute(
            select(Category).where(Category.id == cat_id)
        )).scalar_one_or_none()

    cat_name = cat.name_uz if lang == "uz" else cat.name_ru if cat else ""
    await callback.message.edit_text(
        _("choose_product", lang, category=cat_name),
        reply_markup=products_keyboard(products, lang, page=page, cat_id=cat_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod:"))
@handle_errors
async def cb_product_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Show product card with qty controls."""
    product_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one_or_none()

    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return

    if not product.is_available:
        await callback.answer(_("product_unavailable", lang), show_alert=True)
        return

    qty = _qty_cache.get(user_id, {}).get(product_id, 1)
    badges = product.get_badges()
    text = _("product_card", lang,
             badges=badges + " " if badges else "",
             name=product.get_name(lang),
             price=product.price // 100,
             description=product.get_description(lang))

    kb = product_card_keyboard(product_id, qty, lang)

    if product.photo:
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=product.photo,
                caption=text,
                reply_markup=kb,
            )
        except Exception:
            await callback.message.edit_text(text, reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data.startswith("qty:"))
@handle_errors
async def cb_qty_change(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Adjust the quantity on the product card."""
    parts = callback.data.split(":")
    action = parts[1]
    product_id = int(parts[2])
    user_id = callback.from_user.id

    if user_id not in _qty_cache:
        _qty_cache[user_id] = {}
    current_qty = _qty_cache[user_id].get(product_id, 1)

    if action == "inc":
        current_qty = min(current_qty + 1, 20)
    elif action == "dec":
        current_qty = max(current_qty - 1, 1)

    _qty_cache[user_id][product_id] = current_qty

    kb = product_card_keyboard(product_id, current_qty, lang)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "noop")
@handle_errors
async def cb_noop(callback: CallbackQuery, **kwargs) -> None:
    await callback.answer()


@router.callback_query(F.data == "back:products")
@handle_errors
async def cb_back_products(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Return to category list."""
    await show_categories(callback, lang)
