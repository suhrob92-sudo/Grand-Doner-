"""Admin product management — CRUD with FSM multi-step form."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.product import Product
from models.category import Category
from utils.i18n import _
from utils.decorators import handle_errors
from utils.validators import is_valid_price, parse_price_to_kopecks
from keyboards.inline import (
    admin_back_keyboard, admin_main_keyboard, admin_product_keyboard,
    categories_keyboard,
)
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class AddProductStates(StatesGroup):
    name_ru = State()
    name_uz = State()
    desc_ru = State()
    desc_uz = State()
    price = State()
    photo = State()
    category = State()


class EditProductStates(StatesGroup):
    field = State()
    value = State()


@router.callback_query(F.data == "admin:products")
@handle_errors
async def cb_admin_products(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).order_by(Product.sort_order))
        products = result.scalars().all()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    for p in products:
        status = "✅" if p.is_available else "❌"
        badges = p.get_badges()
        label = f"{status} {badges}{p.name_ru} — {p.price // 100} ₽"
        builder.button(text=label, callback_data=f"admin:prod_detail:{p.id}")
    builder.row(InlineKeyboardButton(text=_("add_product_btn", lang), callback_data="admin:prod_add"))
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(1)

    await callback.message.edit_text(
        _("product_list_title", lang),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:prod_detail:"))
@handle_errors
async def cb_product_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    product_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one_or_none()

    if not product:
        await callback.answer("Not found", show_alert=True)
        return

    status = "✅ Доступен" if product.is_available else "❌ Недоступен"
    badges = product.get_badges()
    text = (
        f"📦 <b>{product.name_ru}</b> ({product.name_uz})\n"
        f"💰 {product.price // 100} ₽\n"
        f"🏷 {badges or '—'}\n"
        f"🔒 {status}\n"
        f"📝 {product.description_ru}"
    )
    await callback.message.edit_text(text, reply_markup=admin_product_keyboard(product_id, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:prod_toggle:"))
@handle_errors
async def cb_prod_toggle(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    product_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one()
        product.is_available = not product.is_available
        await session.commit()
    await callback.answer(_("toggle_available", lang), show_alert=True)
    await cb_product_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:prod_new:"))
@handle_errors
async def cb_prod_toggle_new(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    product_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one()
        product.is_new = not product.is_new
        await session.commit()
    await callback.answer(_("toggle_new_badge", lang), show_alert=True)


@router.callback_query(F.data.startswith("admin:prod_hot:"))
@handle_errors
async def cb_prod_toggle_hot(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    product_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one()
        product.is_hot = not product.is_hot
        await session.commit()
    await callback.answer(_("toggle_hot_badge", lang), show_alert=True)


@router.callback_query(F.data.startswith("admin:prod_delete:"))
@handle_errors
async def cb_prod_delete(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    product_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        product = (await session.execute(
            select(Product).where(Product.id == product_id)
        )).scalar_one_or_none()
        if product:
            await session.delete(product)
            await session.commit()
    await callback.answer(_("product_deleted", lang), show_alert=True)
    await cb_admin_products(callback, lang)


@router.callback_query(F.data == "admin:prod_add")
@handle_errors
async def cb_prod_add_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AddProductStates.name_ru)
    await callback.message.answer(_("enter_product_name_ru", lang))
    await callback.answer()


@router.message(AddProductStates.name_ru)
@handle_errors
async def add_prod_name_ru(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(name_ru=message.text.strip())
    await state.set_state(AddProductStates.name_uz)
    await message.answer(_("enter_product_name_uz", lang))


@router.message(AddProductStates.name_uz)
@handle_errors
async def add_prod_name_uz(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(name_uz=message.text.strip())
    await state.set_state(AddProductStates.desc_ru)
    await message.answer(_("enter_product_desc_ru", lang))


@router.message(AddProductStates.desc_ru)
@handle_errors
async def add_prod_desc_ru(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(desc_ru=message.text.strip())
    await state.set_state(AddProductStates.desc_uz)
    await message.answer(_("enter_product_desc_uz", lang))


@router.message(AddProductStates.desc_uz)
@handle_errors
async def add_prod_desc_uz(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    await state.update_data(desc_uz=message.text.strip())
    await state.set_state(AddProductStates.price)
    await message.answer(_("enter_product_price", lang))


@router.message(AddProductStates.price)
@handle_errors
async def add_prod_price(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_valid_price(message.text):
        await message.answer(_("invalid_price", lang))
        return
    price_kopecks = parse_price_to_kopecks(message.text)
    await state.update_data(price=price_kopecks)
    await state.set_state(AddProductStates.photo)
    await message.answer(_("enter_product_photo", lang))


@router.message(AddProductStates.photo, F.photo)
@handle_errors
async def add_prod_photo(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    await state.set_state(AddProductStates.category)
    async with AsyncSessionLocal() as session:
        cats = (await session.execute(select(Category).where(Category.is_active == True))).scalars().all()
    await message.answer(
        _("choose_category_for_product", lang),
        reply_markup=categories_keyboard(cats, lang),
    )


@router.message(AddProductStates.photo)
@handle_errors
async def add_prod_photo_skip(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    """Allow skipping photo with any non-photo message."""
    await state.update_data(photo=None)
    await state.set_state(AddProductStates.category)
    async with AsyncSessionLocal() as session:
        cats = (await session.execute(select(Category).where(Category.is_active == True))).scalars().all()
    await message.answer(
        _("choose_category_for_product", lang),
        reply_markup=categories_keyboard(cats, lang),
    )


@router.callback_query(F.data.startswith("cat:"), AddProductStates.category)
@handle_errors
async def add_prod_category(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    cat_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    async with AsyncSessionLocal() as session:
        product = Product(
            name_ru=data["name_ru"],
            name_uz=data["name_uz"],
            description_ru=data.get("desc_ru", ""),
            description_uz=data.get("desc_uz", ""),
            price=data["price"],
            photo=data.get("photo"),
            category_id=cat_id,
        )
        session.add(product)
        await session.commit()
    await callback.message.answer(_("product_added", lang, name=data["name_ru"]))
    await state.clear()
    await callback.answer()
