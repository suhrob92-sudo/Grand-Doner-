"""Start handler — language selection, registration, main menu entry."""

import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.user import User
from utils.i18n import _
from utils.helpers import generate_referral_code
from utils.decorators import handle_errors
from utils.validators import normalize_phone
from keyboards.inline import language_inline, main_menu_inline
from keyboards.reply import phone_keyboard, main_menu_keyboard, remove_keyboard
from config import settings

router = Router()
logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    waiting_language = State()
    waiting_phone = State()


@router.message(CommandStart())
@handle_errors
async def cmd_start(message: Message, state: FSMContext, lang: str, db_user: User | None = None) -> None:
    """Entry point — show language selection if user is new, main menu if returning."""
    # Parse referral code from start payload
    args = message.text.split(maxsplit=1)
    referral_code = None
    if len(args) > 1 and args[1].startswith("ref_"):
        referral_code = args[1][4:]  # strip "ref_"
        await state.update_data(referral_code=referral_code)

    if db_user:
        # Returning user — go straight to main menu
        await message.answer(
            _("main_menu", db_user.language),
            reply_markup=main_menu_inline(db_user.language),
        )
        return

    # New user — show language picker
    await state.set_state(RegistrationStates.waiting_language)
    await message.answer(
        _("choose_language", "ru"),
        reply_markup=language_inline(),
    )


@router.callback_query(F.data.startswith("lang:"), RegistrationStates.waiting_language)
@handle_errors
async def cb_language_select(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    """Handle language selection during registration."""
    chosen_lang = callback.data.split(":")[1]
    await state.update_data(language=chosen_lang)
    await callback.message.edit_text(
        _("welcome", chosen_lang, name=settings.RESTAURANT_NAME)
    )
    await callback.message.answer(
        _("request_phone", chosen_lang),
        reply_markup=phone_keyboard(chosen_lang),
    )
    await state.set_state(RegistrationStates.waiting_phone)
    await callback.answer()


@router.message(RegistrationStates.waiting_phone, F.contact)
@handle_errors
async def handle_phone_contact(message: Message, state: FSMContext) -> None:
    """Register a new user after they share their phone contact."""
    data = await state.get_data()
    chosen_lang = data.get("language", "ru")
    referral_code_from_start = data.get("referral_code")

    phone = normalize_phone(message.contact.phone_number)
    telegram_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        # Double-check user doesn't already exist
        existing = (await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )).scalar_one_or_none()

        if existing:
            await message.answer(
                _("phone_already_registered", chosen_lang),
                reply_markup=main_menu_keyboard(chosen_lang),
            )
            await state.clear()
            return

        # Find referrer if referral code was passed
        referrer_telegram_id = None
        if referral_code_from_start:
            ref_result = await session.execute(
                select(User).where(User.referral_code == f"REF{referral_code_from_start}")
            )
            referrer = ref_result.scalar_one_or_none()
            if referrer:
                referrer_telegram_id = referrer.telegram_id

        new_user = User(
            telegram_id=telegram_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            phone=phone,
            language=chosen_lang,
            referral_code=generate_referral_code(telegram_id),
            referred_by=referrer_telegram_id,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

    # Notify about referral discount
    if referrer_telegram_id:
        await message.answer(_("new_user_ref_discount", chosen_lang))

    await message.answer(
        _("registration_complete", chosen_lang, name=message.from_user.first_name),
        reply_markup=remove_keyboard(),
    )
    await message.answer(
        _("main_menu", chosen_lang),
        reply_markup=main_menu_inline(chosen_lang),
    )
    await state.clear()


@router.message(RegistrationStates.waiting_phone)
@handle_errors
async def handle_phone_text_fallback(message: Message, state: FSMContext) -> None:
    """Remind the user to use the contact button."""
    data = await state.get_data()
    lang = data.get("language", "ru")
    await message.answer(
        _("request_phone", lang),
        reply_markup=phone_keyboard(lang),
    )


@router.callback_query(F.data == "main:catalog")
@handle_errors
async def cb_main_catalog(callback: CallbackQuery, lang: str, **kwargs) -> None:
    from handlers.menu import show_categories
    await show_categories(callback, lang)


@router.callback_query(F.data == "main:cart")
@handle_errors
async def cb_main_cart(callback: CallbackQuery, lang: str, **kwargs) -> None:
    from handlers.cart import show_cart
    await show_cart(callback, lang)


@router.callback_query(F.data == "main:orders")
@handle_errors
async def cb_main_orders(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    from handlers.profile import show_order_history
    await show_order_history(callback, lang, db_user)


@router.callback_query(F.data == "main:profile")
@handle_errors
async def cb_main_profile(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    from handlers.profile import show_profile
    await show_profile(callback, lang, db_user)


@router.callback_query(F.data == "main:referral")
@handle_errors
async def cb_main_referral(callback: CallbackQuery, lang: str, db_user: User | None = None, **kwargs) -> None:
    from handlers.referral import show_referral
    await show_referral(callback, lang, db_user)


@router.callback_query(F.data == "main:reviews")
@handle_errors
async def cb_main_reviews(callback: CallbackQuery, lang: str, **kwargs) -> None:
    from handlers.reviews import show_reviews
    await show_reviews(callback, lang)


@router.callback_query(F.data == "goto:main")
@handle_errors
async def cb_goto_main(callback: CallbackQuery, lang: str, **kwargs) -> None:
    """Universal 'back to main menu' for regular user pages."""
    from keyboards.inline import main_menu_inline
    await callback.message.edit_text(
        _("main_menu", lang),
        reply_markup=main_menu_inline(lang),
    )
    await callback.answer()
