"""Reply keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from utils.i18n import _


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("share_phone_btn", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("catalog_btn", lang)), KeyboardButton(text=_("cart_btn", lang))],
            [KeyboardButton(text=_("orders_btn", lang)), KeyboardButton(text=_("profile_btn", lang))],
            [KeyboardButton(text=_("referral_btn", lang)), KeyboardButton(text=_("reviews_btn", lang))],
        ],
        resize_keyboard=True,
    )


def location_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("send_location_btn", lang), request_location=True)],
            [KeyboardButton(text=_("cancel_btn", lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def courier_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Мои заказы / Buyurtmalarim")],
            [KeyboardButton(text="🏠 Главное меню / Asosiy menyu")],
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
