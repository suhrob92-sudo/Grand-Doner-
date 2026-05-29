"""Admin user management — search, ban/unban, bonus, personal message, CSV export."""

import csv
import io
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, or_, func
from models.base import AsyncSessionLocal
from models.user import User
from models.order import Order
from models.bonus import BonusTransaction
from utils.i18n import _
from utils.helpers import format_datetime
from utils.decorators import handle_errors
from keyboards.inline import admin_user_keyboard, admin_back_keyboard
from handlers.admin.dashboard import is_admin

router = Router()
logger = logging.getLogger(__name__)


class UserAdminStates(StatesGroup):
    searching = State()
    adding_bonus = State()
    sending_message = State()


@router.callback_query(F.data == "admin:users")
@handle_errors
async def cb_admin_users(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    async with AsyncSessionLocal() as session:
        total = (await session.execute(select(func.count(User.id)))).scalar_one()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Поиск", callback_data="admin:user_search")
    builder.button(text="📥 Экспорт CSV", callback_data="admin:users_csv")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:main"))
    builder.adjust(2)

    await callback.message.edit_text(
        f"👥 <b>Пользователи</b>\nВсего: <b>{total}</b>",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:user_search")
@handle_errors
async def cb_user_search_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(UserAdminStates.searching)
    await callback.message.answer("🔍 Введите имя, @username или номер телефона:")
    await callback.answer()


@router.message(UserAdminStates.searching)
@handle_errors
async def handle_user_search(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    query = message.text.strip()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.username.ilike(f"%{query}%"),
                    User.phone.ilike(f"%{query}%"),
                )
            ).limit(10)
        )
        users = result.scalars().all()

    if not users:
        await message.answer("Пользователи не найдены.")
        await state.clear()
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for u in users:
        builder.button(
            text=f"{u.full_name} (@{u.username or '—'})",
            callback_data=f"admin:user_detail:{u.id}",
        )
    builder.adjust(1)
    await message.answer("Результаты:", reply_markup=builder.as_markup())
    await state.clear()


@router.callback_query(F.data.startswith("admin:user_detail:"))
@handle_errors
async def cb_user_detail(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    user_id = int(callback.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            await callback.answer("Не найден", show_alert=True)
            return
        orders_count = (await session.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )).scalar_one()

    status_str = "🚫 Заблокирован" if user.is_banned else "✅ Активен"
    text = _("user_detail", lang,
             name=user.full_name,
             username=user.username or "—",
             phone=user.phone or "—",
             bonus=user.bonus_points,
             spent=user.total_spent // 100,
             orders_count=orders_count,
             reg_date=format_datetime(user.created_at),
             status=status_str)

    await callback.message.edit_text(text, reply_markup=admin_user_keyboard(user_id, user.is_banned, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:ban:"))
@handle_errors
async def cb_ban_user(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    user_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        user.is_banned = True
        await session.commit()
    await callback.answer(_("user_banned", lang), show_alert=True)
    await cb_user_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:unban:"))
@handle_errors
async def cb_unban_user(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    user_id = int(callback.data.split(":")[2])
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        user.is_banned = False
        await session.commit()
    await callback.answer(_("user_unbanned", lang), show_alert=True)
    await cb_user_detail(callback, lang)


@router.callback_query(F.data.startswith("admin:add_bonus:"))
@handle_errors
async def cb_add_bonus_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    user_id = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=user_id)
    await state.set_state(UserAdminStates.adding_bonus)
    await callback.message.answer(_("enter_bonus_amount", lang))
    await callback.answer()


@router.message(UserAdminStates.adding_bonus)
@handle_errors
async def handle_add_bonus(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("Введите целое число.")
        return
    data = await state.get_data()
    user_id = data["target_user_id"]
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        user.bonus_points += amount
        session.add(BonusTransaction(user_id=user_id, amount=amount, reason="admin"))
        await session.commit()
    await message.answer(_("bonus_added_admin", lang, amount=amount))
    await state.clear()


@router.callback_query(F.data.startswith("admin:msg_user:"))
@handle_errors
async def cb_msg_user_start(callback: CallbackQuery, state: FSMContext, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    user_id = int(callback.data.split(":")[2])
    await state.update_data(msg_target_user_id=user_id)
    await state.set_state(UserAdminStates.sending_message)
    await callback.message.answer(_("enter_message_for_user", lang))
    await callback.answer()


@router.message(UserAdminStates.sending_message)
@handle_errors
async def handle_send_msg_to_user(message: Message, state: FSMContext, lang: str, **kwargs) -> None:
    data = await state.get_data()
    user_id = data["msg_target_user_id"]
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
    try:
        await message.bot.send_message(user.telegram_id, message.text)
        await message.answer(_("message_sent", lang))
    except Exception as exc:
        await message.answer(f"Ошибка: {exc}")
    await state.clear()


@router.callback_query(F.data == "admin:users_csv")
@handle_errors
async def cb_users_csv(callback: CallbackQuery, lang: str, **kwargs) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User).order_by(User.created_at.desc()).limit(2000))).scalars().all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Имя", "Username", "Телефон", "Язык", "Бонусы", "Потрачено", "Дата"])
    for u in users:
        writer.writerow([
            u.telegram_id, u.full_name, u.username or "",
            u.phone or "", u.language, u.bonus_points,
            u.total_spent // 100, format_datetime(u.created_at),
        ])
    raw = buf.getvalue().encode("utf-8-sig")
    await callback.message.answer_document(
        document=BufferedInputFile(raw, filename="users.csv"),
        caption="📥 Экспорт пользователей",
    )
    await callback.answer()
