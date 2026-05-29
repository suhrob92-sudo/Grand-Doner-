"""Inline keyboard builders for all bot flows."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.i18n import _


# ── Language ──────────────────────────────────────────────────────────────────

def language_inline() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang:ru")
    builder.adjust(2)
    return builder.as_markup()


# ── Main Menu ─────────────────────────────────────────────────────────────────

def main_menu_inline(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("catalog_btn", lang), callback_data="main:catalog")
    builder.button(text=_("cart_btn", lang), callback_data="main:cart")
    builder.button(text=_("orders_btn", lang), callback_data="main:orders")
    builder.button(text=_("profile_btn", lang), callback_data="main:profile")
    builder.button(text=_("referral_btn", lang), callback_data="main:referral")
    builder.button(text=_("reviews_btn", lang), callback_data="main:reviews")
    builder.adjust(2)
    return builder.as_markup()


# ── Categories ────────────────────────────────────────────────────────────────

def categories_keyboard(categories: list, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        name = cat.name_uz if lang == "uz" else cat.name_ru
        builder.button(text=f"{cat.emoji} {name}", callback_data=f"cat:{cat.id}")
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(products: list, lang: str, page: int = 0) -> InlineKeyboardMarkup:
    """Paginated product list within a category."""
    PAGE_SIZE = 8
    start = page * PAGE_SIZE
    page_items = products[start : start + PAGE_SIZE]
    builder = InlineKeyboardBuilder()
    for p in page_items:
        name = p.get_name(lang)
        badge = p.get_badges()
        label = f"{badge} {name} — {p.price // 100} ₽".strip()
        builder.button(text=label, callback_data=f"prod:{p.id}")
    builder.adjust(1)
    # Pagination row
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀", callback_data=f"prod_page:{page - 1}"))
    if start + PAGE_SIZE < len(products):
        nav.append(InlineKeyboardButton(text="▶", callback_data=f"prod_page:{page + 1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="◀ Назад / Orqaga", callback_data="main:catalog"))
    return builder.as_markup()


def product_card_keyboard(product_id: int, qty: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➖", callback_data=f"qty:dec:{product_id}")
    builder.button(text=f" {qty} ", callback_data="noop")
    builder.button(text="➕", callback_data=f"qty:inc:{product_id}")
    builder.row(
        InlineKeyboardButton(text=_("add_to_cart_btn", lang), callback_data=f"cart:add:{product_id}:{qty}")
    )
    builder.row(
        InlineKeyboardButton(text=_("back_btn", lang), callback_data="back:products")
    )
    return builder.as_markup()


# ── Cart ──────────────────────────────────────────────────────────────────────

def cart_keyboard(lang: str, has_promo: bool = False, has_bonus: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("checkout_btn", lang), callback_data="cart:checkout")
    if not has_promo:
        builder.button(text=_("apply_promo_btn", lang), callback_data="cart:promo")
    if has_bonus:
        builder.button(text=_("use_bonus_btn", lang), callback_data="cart:bonus")
    builder.button(text=_("clear_cart_btn", lang), callback_data="cart:clear")
    builder.button(text=_("catalog_btn", lang), callback_data="main:catalog")
    builder.adjust(1)
    return builder.as_markup()


def cart_items_keyboard(cart_items: list, lang: str) -> InlineKeyboardMarkup:
    """Per-item quantity controls inside cart view."""
    builder = InlineKeyboardBuilder()
    for item_key, item in cart_items:
        builder.row(
            InlineKeyboardButton(text=f"➖ {item['name']}", callback_data=f"cart:dec:{item_key}"),
            InlineKeyboardButton(text=str(item["qty"]), callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cart:inc:{item_key}"),
        )
    return builder.as_markup()


# ── Order type ────────────────────────────────────────────────────────────────

def order_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("pickup_btn", lang), callback_data="order_type:pickup")
    builder.button(text=_("taxi_btn", lang), callback_data="order_type:taxi")
    builder.button(text=_("delivery_btn", lang), callback_data="order_type:delivery")
    builder.adjust(1)
    return builder.as_markup()


def pickup_time_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("pickup_now", lang), callback_data="pickup_time:now")
    builder.button(text=_("pickup_15min", lang), callback_data="pickup_time:15")
    builder.button(text=_("pickup_30min", lang), callback_data="pickup_time:30")
    builder.button(text=_("pickup_custom", lang), callback_data="pickup_time:custom")
    builder.adjust(2)
    return builder.as_markup()


# ── Payment ───────────────────────────────────────────────────────────────────

def payment_keyboard(lang: str, payment_url: str, amount_rub: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("pay_btn", lang, amount=amount_rub), url=payment_url)
    builder.button(text=_("cancel_btn", lang), callback_data="payment:cancel")
    builder.adjust(1)
    return builder.as_markup()


# ── Order status ──────────────────────────────────────────────────────────────

def order_status_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Обновить статус", callback_data=f"order_status:{order_id}")
    return builder.as_markup()


# ── Courier ───────────────────────────────────────────────────────────────────

def courier_new_order_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("accept_order_btn", lang), callback_data=f"courier:accept:{order_id}")
    return builder.as_markup()


def courier_active_order_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("courier_departed_btn", lang), callback_data=f"courier:departed:{order_id}")
    builder.button(text=_("courier_arrived_btn", lang), callback_data=f"courier:arrived:{order_id}")
    builder.button(text=_("courier_delivered_btn", lang), callback_data=f"courier:delivered:{order_id}")
    builder.adjust(1)
    return builder.as_markup()


# ── Profile ───────────────────────────────────────────────────────────────────

def profile_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("order_history_btn", lang), callback_data="profile:history")
    builder.button(text=_("my_referral_btn", lang), callback_data="profile:referral")
    builder.button(text=_("bonus_history_btn", lang), callback_data="profile:bonus")
    builder.button(text=_("edit_language_btn", lang), callback_data="profile:language")
    builder.button(text=_("notifications_btn", lang), callback_data="profile:notifications")
    builder.adjust(2)
    return builder.as_markup()


# ── Reviews ───────────────────────────────────────────────────────────────────

def rating_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text=f"{'⭐' * i}", callback_data=f"review:rate:{order_id}:{i}")
    builder.adjust(5)
    return builder.as_markup()


def review_comment_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("review_yes_btn", lang), callback_data=f"review:comment:{order_id}")
    builder.button(text=_("review_no_btn", lang), callback_data=f"review:skip:{order_id}")
    builder.adjust(2)
    return builder.as_markup()


# ── Admin ─────────────────────────────────────────────────────────────────────

def admin_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("admin_products_btn", lang), callback_data="admin:products")
    builder.button(text=_("admin_orders_btn", lang), callback_data="admin:orders")
    builder.button(text=_("admin_users_btn", lang), callback_data="admin:users")
    builder.button(text=_("admin_broadcast_btn", lang), callback_data="admin:broadcast")
    builder.button(text=_("admin_promo_btn", lang), callback_data="admin:promo")
    builder.button(text=_("admin_stats_btn", lang), callback_data="admin:stats")
    builder.button(text=_("admin_settings_btn", lang), callback_data="admin:settings")
    builder.button(text=_("admin_couriers_btn", lang), callback_data="admin:couriers")
    builder.button(text=_("admin_reviews_btn", lang), callback_data="admin:reviews")
    builder.adjust(2)
    return builder.as_markup()


def admin_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("back_to_admin", lang), callback_data="admin:main")
    return builder.as_markup()


def back_to_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Back button for regular (non-admin) user pages — returns to main menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text=_("back_btn", lang), callback_data="goto:main")
    return builder.as_markup()


def admin_order_keyboard(order_id: int, lang: str) -> InlineKeyboardMarkup:
    statuses = ["paid", "preparing", "ready", "on_the_way", "completed", "cancelled"]
    status_labels = {
        "paid": "✅ Paid",
        "preparing": "👨‍🍳 Preparing",
        "ready": "🎉 Ready",
        "on_the_way": "🚚 On the way",
        "completed": "✅ Completed",
        "cancelled": "❌ Cancelled",
    }
    builder = InlineKeyboardBuilder()
    for s in statuses:
        builder.button(text=status_labels[s], callback_data=f"admin:order_status:{order_id}:{s}")
    builder.row(
        InlineKeyboardButton(text=_("cancel_order_btn", lang), callback_data=f"admin:order_cancel:{order_id}")
    )
    builder.row(
        InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:orders")
    )
    builder.adjust(2)
    return builder.as_markup()


def admin_product_keyboard(product_id: int, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить", callback_data=f"admin:prod_edit:{product_id}")
    builder.button(text="🔄 Доступность", callback_data=f"admin:prod_toggle:{product_id}")
    builder.button(text="🆕 New", callback_data=f"admin:prod_new:{product_id}")
    builder.button(text="🔥 Hot", callback_data=f"admin:prod_hot:{product_id}")
    builder.button(text="🗑 Удалить", callback_data=f"admin:prod_delete:{product_id}")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:products"))
    builder.adjust(2)
    return builder.as_markup()


def admin_user_keyboard(user_id: int, is_banned: bool, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_banned:
        builder.button(text=_("unban_user_btn", lang), callback_data=f"admin:unban:{user_id}")
    else:
        builder.button(text=_("ban_user_btn", lang), callback_data=f"admin:ban:{user_id}")
    builder.button(text=_("add_bonus_btn", lang), callback_data=f"admin:add_bonus:{user_id}")
    builder.button(text=_("send_message_btn", lang), callback_data=f"admin:msg_user:{user_id}")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:users"))
    builder.adjust(2)
    return builder.as_markup()


def admin_review_keyboard(review_id: int, is_published: bool, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_published:
        builder.button(text=_("hide_review_btn", lang), callback_data=f"admin:review_hide:{review_id}")
    else:
        builder.button(text=_("publish_review_btn", lang), callback_data=f"admin:review_pub:{review_id}")
    builder.button(text=_("reply_review_btn", lang), callback_data=f"admin:review_reply:{review_id}")
    builder.row(InlineKeyboardButton(text=_("back_to_admin", lang), callback_data="admin:reviews"))
    builder.adjust(2)
    return builder.as_markup()


def admin_broadcast_audience_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("audience_all", lang), callback_data="bcast_aud:all")
    builder.button(text=_("audience_active", lang), callback_data="bcast_aud:active")
    builder.button(text=_("audience_ordered", lang), callback_data="bcast_aud:ordered")
    builder.adjust(1)
    return builder.as_markup()


def confirm_keyboard(confirm_cb: str, cancel_cb: str, lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=_("confirm_btn", lang), callback_data=confirm_cb)
    builder.button(text=_("cancel_btn", lang), callback_data=cancel_cb)
    builder.adjust(2)
    return builder.as_markup()
