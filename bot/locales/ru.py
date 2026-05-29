"""Russian locale — every user-facing string in one dict."""

texts: dict = {
    # Language selection
    "choose_language": "🌐 <b>Выберите язык / Tilni tanlang:</b>",

    # Welcome & registration
    "welcome": "👋 <b>Добро пожаловать в {name}!</b>\n\nМы готовим вкуснейшую шаурму для вас 🥙",
    "request_phone": "📞 <b>Поделитесь вашим номером телефона</b>, чтобы завершить регистрацию:",
    "share_phone_btn": "📱 Поделиться номером",
    "registration_complete": "✅ <b>Регистрация завершена!</b>\nДобро пожаловать, {name}!",
    "phone_already_registered": "Вы уже зарегистрированы!",

    # Main menu
    "main_menu": "🏠 <b>Главное меню</b>\nЧем могу помочь?",
    "catalog_btn": "🍽 Меню",
    "cart_btn": "🛒 Корзина",
    "profile_btn": "👤 Профиль",
    "orders_btn": "📋 Мои заказы",
    "referral_btn": "👥 Реферальная программа",
    "reviews_btn": "⭐ Отзывы",
    "help_btn": "❓ Помощь",
    "language_btn": "🌐 Язык",

    # Catalog
    "choose_category": "🍽 <b>Выберите категорию:</b>",
    "choose_product": "Выберите блюдо из категории <b>{category}</b>:",
    "product_card": "{badges}<b>{name}</b> — <b>{price} ₽</b>\n\n{description}",
    "product_unavailable": "❌ Товар временно недоступен",
    "back_btn": "◀ Назад",
    "add_to_cart_btn": "🛒 В корзину",
    "no_products_in_category": "В этой категории пока нет товаров.",

    # Cart
    "cart_empty": "🛒 Ваша корзина пуста.\n\nПерейдите в меню, чтобы выбрать блюда.",
    "cart_title": "🛒 <b>Ваша корзина:</b>",
    "cart_item_line": "• {name} × {qty} = {subtotal} ₽",
    "cart_total": "\n💰 <b>Итого: {total} ₽</b>",
    "cart_bonus_available": "🎁 Доступно бонусов: {points} (до {max} ₽)",
    "cart_promo_applied": "🏷 Промокод <b>{code}</b> применён: −{discount} ₽",
    "checkout_btn": "✅ Оформить заказ",
    "clear_cart_btn": "🗑 Очистить корзину",
    "cart_cleared": "🗑 Корзина очищена.",
    "apply_promo_btn": "🏷 Промокод",
    "use_bonus_btn": "🎁 Использовать бонусы",
    "enter_promo": "Введите промокод:",
    "promo_valid": "✅ Промокод принят! Скидка: {discount} ₽",
    "promo_invalid": "❌ Промокод недействителен или истёк.",
    "promo_min_order": "❌ Минимальная сумма заказа для этого промокода: {amount} ₽",
    "bonus_applied": "✅ Использовано {points} бонусных баллов = −{amount} ₽",
    "bonus_removed": "Бонусные баллы убраны.",
    "not_enough_bonus": "❌ Недостаточно бонусных баллов.",
    "item_added_to_cart": "✅ <b>{name}</b> добавлен в корзину!",

    # Order type
    "choose_order_type": "🚀 <b>Как вы хотите получить заказ?</b>",
    "pickup_btn": "🏪 Самовывоз",
    "taxi_btn": "🚕 Яндекс.Такси",
    "delivery_btn": "🚚 Доставка курьером",

    # Pickup
    "pickup_info": "🏪 <b>Самовывоз</b>\n\n📍 Адрес: <b>{address}</b>\n📞 Телефон: {phone}\n\nВыберите время:",
    "pickup_now": "⚡ Сейчас",
    "pickup_15min": "⏰ Через 15 мин",
    "pickup_30min": "⏰ Через 30 мин",
    "pickup_custom": "🕐 Указать время",
    "enter_pickup_time": "Введите время самовывоза (например: 14:30):",
    "pickup_confirmed": "✅ Самовывоз в {time}. Переходим к оплате.",

    # Taxi
    "taxi_intro": "🚕 <b>Яндекс.Такси</b>\n\nМы закажем такси к ресторану, пока готовится ваш заказ.\n\nОтправьте геолокацию или введите ваш адрес:",
    "send_location_btn": "📍 Отправить геолокацию",
    "or_type_address": "или введите адрес текстом:",
    "taxi_ordering": "⏳ Заказываем такси...",
    "taxi_ordered": "✅ <b>Такси заказано!</b>\n\n🚗 {car} ({color})\n👤 Водитель: {driver}\n⏱ Ожидание: {eta} мин\n🔢 Номер: <code>{plate}</code>",
    "taxi_driver_en_route": "🚗 Водитель едет к вам!",
    "taxi_driver_arrived": "📍 Водитель прибыл!",
    "taxi_cancelled": "❌ Такси отменено.",
    "taxi_error": "❌ Не удалось заказать такси. Попробуйте ещё раз или выберите другой способ.",

    # Delivery
    "delivery_intro": "🚚 <b>Доставка курьером</b>\n\nОтправьте геолокацию или введите адрес доставки:",
    "delivery_calculating": "📏 Рассчитываем стоимость доставки...",
    "delivery_cost_info": "📍 Адрес: {address}\n📏 Расстояние: {distance} км\n🚚 Стоимость доставки: <b>{cost} ₽</b>\n\n💰 Итого с доставкой: <b>{total} ₽</b>",
    "delivery_too_far": "❌ К сожалению, мы не доставляем на расстояние более 15 км.",
    "confirm_delivery_btn": "✅ Подтвердить",

    # Payment
    "payment_intro": "💳 <b>Оплата заказа</b>\n\nСумма: <b>{amount} ₽</b>\n\nНажмите кнопку ниже для оплаты:",
    "pay_btn": "💳 Оплатить {amount} ₽",
    "payment_pending": "⏳ Ожидаем оплату...",
    "payment_success": (
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        "🧾 Заказ <b>#{order_number}</b>\n"
        "💰 Оплачено: <b>{amount} ₽</b>\n\n"
        "Покажите QR-код кассиру 👇"
    ),
    "payment_failed": "❌ Оплата не прошла. Попробуйте ещё раз.",
    "payment_cancelled": "Оплата отменена.",
    "order_confirmed_admin": (
        "🆕 <b>Новый заказ #{order_number}</b>\n"
        "👤 {customer}\n📞 {phone}\n"
        "📦 Тип: {order_type}\n"
        "📍 {address}\n"
        "🍖 {items}\n"
        "💰 {total} ₽"
    ),

    # Order statuses
    "status_pending": "⏳ Ожидает оплаты",
    "status_paid": "✅ Оплачен",
    "status_preparing": "👨‍🍳 Готовится",
    "status_ready": "🎉 Готов к выдаче!",
    "status_on_the_way": "🚚 Курьер в пути",
    "status_completed": "✅ Выполнен",
    "status_cancelled": "❌ Отменён",

    "order_status_update": "📦 <b>Заказ #{order_number}</b>\nСтатус: {status}",
    "order_preparing_msg": "👨‍🍳 Кухня приступила к приготовлению вашего заказа!",
    "order_ready_msg": "🎉 Ваш заказ готов! Ждём вас 🏃",
    "order_on_way_msg": "🚚 Курьер выехал! Ожидайте.",

    # Profile
    "profile_title": "👤 <b>Ваш профиль</b>",
    "profile_info": (
        "👤 <b>{name}</b>\n"
        "📞 {phone}\n"
        "🎁 Бонусные баллы: <b>{bonus}</b>\n"
        "💰 Всего потрачено: <b>{spent} ₽</b>\n"
        "👥 Приглашено друзей: <b>{referrals}</b>"
    ),
    "order_history_btn": "📋 История заказов",
    "settings_btn": "⚙️ Настройки",
    "my_referral_btn": "🔗 Мой реферальный код",
    "edit_language_btn": "🌐 Сменить язык",
    "notifications_btn": "🔔 Уведомления",
    "no_orders_yet": "У вас ещё нет заказов.",
    "order_history_item": "#{number} — {date} — {amount} ₽ — {status}",

    # Referral
    "referral_title": "👥 <b>Реферальная программа</b>",
    "referral_info": (
        "🔗 Ваша реферальная ссылка:\n{link}\n\n"
        "👥 Приглашено: <b>{count}</b> друзей\n"
        "🎁 Заработано бонусов: <b>{earned}</b> баллов\n\n"
        "За каждого друга, сделавшего первый заказ:\n"
        "• Вам: +150 баллов\n"
        "• Другу: скидка 10%"
    ),
    "referral_leaderboard": "🏆 <b>Топ реферреров:</b>\n{entries}",
    "referral_leaderboard_entry": "{pos}. {name} — {count} друзей",
    "referral_bonus_received": "🎁 Ваш друг сделал первый заказ! +150 бонусных баллов!",
    "new_user_ref_discount": "🎉 Вас пригласил друг! Скидка 10% на первый заказ применена.",

    # Bonus
    "bonus_title": "🎁 <b>Бонусная программа</b>",
    "bonus_info": (
        "💎 Ваши бонусы: <b>{points}</b> баллов\n\n"
        "📈 Правила:\n"
        "• Каждые 100 ₽ = 5 бонусных баллов\n"
        "• 1 балл = 1 ₽ скидки\n"
        "• Можно оплатить до 30% суммы заказа\n"
        "• Баллы сгорают через 90 дней"
    ),
    "bonus_history_btn": "📊 История баллов",
    "bonus_transaction_line": "{date}: {sign}{amount} — {reason}",

    # Promo
    "enter_promo_code": "🏷 Введите промокод:",
    "promo_applied_success": "✅ Промокод <b>{code}</b> применён!\nСкидка: <b>{discount} ₽</b>",

    # Reviews
    "review_request": "⭐ <b>Как вам заказ #{order_number}?</b>\nОцените от 1 до 5:",
    "review_comment_prompt": "Хотите оставить комментарий?",
    "review_yes_btn": "✍️ Да, напишу",
    "review_no_btn": "Нет, спасибо",
    "enter_review_comment": "✍️ Напишите ваш отзыв:",
    "review_saved": "✅ Спасибо за отзыв! Ваше мнение очень важно для нас 🙏",
    "reviews_title": "⭐ <b>Отзывы клиентов:</b>",
    "review_item": "⭐ {rating} — <b>{name}</b>\n{comment}\n<i>{date}</i>",
    "no_reviews": "Пока нет опубликованных отзывов.",
    "review_reply": "💬 <b>Ответ ресторана:</b> {reply}",

    # Courier
    "courier_menu": "🚚 <b>Меню курьера</b>",
    "new_delivery_notification": (
        "📦 <b>Новый заказ #{order_number}</b>\n"
        "📍 <b>{address}</b>\n"
        "📞 Клиент: {phone}\n"
        "🍖 {items}\n"
        "💰 {total} ₽"
    ),
    "accept_order_btn": "✅ Принять заказ",
    "order_accepted_courier": "✅ Вы приняли заказ #{order_number}",
    "order_already_taken": "❌ Заказ уже принят другим курьером.",
    "courier_departed_btn": "🚗 Я выехал",
    "courier_arrived_btn": "📍 Я на месте",
    "courier_delivered_btn": "✅ Доставлено",
    "courier_departed_msg": "🚗 Курьер выехал к вам!",
    "courier_arrived_msg": "📍 Курьер на месте!",
    "order_delivered_msg": "✅ Заказ доставлен! Спасибо, что выбрали нас 🙏",
    "no_active_orders": "У вас нет активных заказов.",
    "courier_accepted_client": "✅ Курьер <b>{name}</b> принял ваш заказ!",

    # Admin
    "admin_welcome": "🔐 <b>Панель администратора</b>",
    "admin_dashboard": (
        "📊 <b>Дашборд</b>\n\n"
        "📦 Заказов сегодня: <b>{orders_today}</b>\n"
        "💰 Выручка сегодня: <b>{revenue_today} ₽</b>\n"
        "📈 Выручка за неделю: <b>{revenue_week} ₽</b>\n"
        "👥 Всего пользователей: <b>{total_users}</b>\n"
        "👤 Новых сегодня: <b>{new_today}</b>\n"
        "🔥 Активных заказов: <b>{active_orders}</b>"
    ),
    "admin_products_btn": "📦 Товары",
    "admin_orders_btn": "📋 Заказы",
    "admin_users_btn": "👥 Пользователи",
    "admin_broadcast_btn": "📢 Рассылка",
    "admin_promo_btn": "🎁 Промокоды",
    "admin_stats_btn": "📊 Статистика",
    "admin_settings_btn": "⚙️ Настройки",
    "admin_couriers_btn": "🚚 Курьеры",
    "admin_reviews_btn": "⭐ Отзывы",
    "back_to_admin": "◀ Главное меню",

    # Admin Products
    "product_list_title": "📦 <b>Список товаров:</b>",
    "add_product_btn": "➕ Добавить товар",
    "product_line": "{status} {badges}{name} — {price} ₽",
    "enter_product_name_ru": "Введите название товара (RU):",
    "enter_product_name_uz": "Введите название товара (UZ):",
    "enter_product_desc_ru": "Введите описание товара (RU):",
    "enter_product_desc_uz": "Введите описание товара (UZ):",
    "enter_product_price": "Введите цену (в рублях):",
    "enter_product_photo": "Отправьте фото товара:",
    "choose_category_for_product": "Выберите категорию:",
    "product_added": "✅ Товар <b>{name}</b> добавлен!",
    "product_updated": "✅ Товар обновлён.",
    "product_deleted": "🗑 Товар удалён.",
    "toggle_available": "Доступность изменена.",
    "toggle_new_badge": "Значок 🆕 изменён.",
    "toggle_hot_badge": "Значок 🔥 изменён.",
    "invalid_price": "❌ Неверная цена. Введите число.",

    # Admin Orders
    "orders_list_title": "📋 <b>Заказы:</b>",
    "order_detail": (
        "📦 <b>Заказ #{number}</b>\n"
        "👤 {customer}\n📞 {phone}\n"
        "📅 {date}\n"
        "📦 Тип: {order_type}\n"
        "📍 {address}\n"
        "🍖 Состав:\n{items}\n"
        "💰 Итого: <b>{total} ₽</b>\n"
        "🏷 Статус: <b>{status}</b>"
    ),
    "change_status_btn": "🔄 Изменить статус",
    "cancel_order_btn": "❌ Отменить заказ",
    "order_cancelled_refund": "✅ Заказ отменён, возврат инициирован.",
    "export_csv_btn": "📥 Экспорт CSV",

    # Admin Users
    "user_detail": (
        "👤 <b>{name}</b> (@{username})\n"
        "📞 {phone}\n"
        "🎁 Бонусов: {bonus}\n"
        "💰 Потрачено: {spent} ₽\n"
        "📦 Заказов: {orders_count}\n"
        "📅 Регистрация: {reg_date}\n"
        "🔒 Статус: {status}"
    ),
    "ban_user_btn": "🚫 Заблокировать",
    "unban_user_btn": "✅ Разблокировать",
    "user_banned": "🚫 Пользователь заблокирован.",
    "user_unbanned": "✅ Пользователь разблокирован.",
    "add_bonus_btn": "🎁 Начислить бонусы",
    "enter_bonus_amount": "Введите количество баллов:",
    "bonus_added_admin": "✅ Начислено {amount} баллов.",
    "send_message_btn": "💬 Отправить сообщение",
    "enter_message_for_user": "Введите сообщение:",
    "message_sent": "✅ Сообщение отправлено.",

    # Admin Broadcast
    "broadcast_title": "📢 <b>Рассылка</b>",
    "broadcast_text_only_btn": "📝 Только текст",
    "broadcast_with_photo_btn": "🖼 Текст + фото",
    "broadcast_with_btn_btn": "🔗 Текст + кнопка",
    "enter_broadcast_text": "Введите текст рассылки:",
    "enter_broadcast_photo": "Отправьте фото:",
    "enter_broadcast_btn_text": "Введите текст кнопки:",
    "enter_broadcast_btn_url": "Введите URL кнопки:",
    "choose_broadcast_audience": "Выберите аудиторию:",
    "audience_all": "👥 Все пользователи",
    "audience_active": "✅ Активные (30 дней)",
    "audience_ordered": "📦 Делали заказ",
    "schedule_or_now": "Отправить сейчас или запланировать?",
    "send_now_btn": "⚡ Сейчас",
    "schedule_btn": "🕐 Запланировать",
    "enter_schedule_time": "Введите дату/время (ДД.ММ.ГГГГ ЧЧ:ММ):",
    "broadcast_scheduled": "✅ Рассылка запланирована на {time}.",
    "broadcast_sent": "✅ Рассылка отправлена!\n📤 Отправлено: {sent}\n❌ Ошибок: {failed}",

    # Admin Promo
    "promo_list_title": "🎁 <b>Промокоды:</b>",
    "promo_line": "{code} — {type} {value} | Использований: {used}/{max}",
    "add_promo_btn": "➕ Создать промокод",
    "enter_promo_code_admin": "Введите код:",
    "choose_promo_type": "Тип скидки:",
    "promo_percent_btn": "% Процент",
    "promo_fixed_btn": "₽ Фиксированная",
    "enter_promo_value": "Введите значение скидки:",
    "enter_promo_min_order": "Минимальная сумма заказа (0 = без ограничений):",
    "enter_promo_max_uses": "Макс. использований (0 = безлимит):",
    "enter_promo_valid_to": "Дата окончания (ДД.ММ.ГГГГ или 0 = без срока):",
    "promo_created": "✅ Промокод <b>{code}</b> создан!",
    "promo_deactivated": "✅ Промокод деактивирован.",

    # Admin Statistics
    "stats_title": "📊 <b>Статистика</b>",
    "stats_detail": (
        "📅 <b>Период: {period}</b>\n\n"
        "💰 Выручка: <b>{revenue} ₽</b>\n"
        "📦 Заказов всего: <b>{orders}</b>\n"
        "✅ Выполнено: <b>{completed}</b>\n"
        "❌ Отменено: <b>{cancelled}</b>\n"
        "📊 Средний чек: <b>{avg_order} ₽</b>\n"
        "🚚 Доставка: <b>{delivery_count}</b>\n"
        "🏪 Самовывоз: <b>{pickup_count}</b>\n"
        "🚕 Такси: <b>{taxi_count}</b>\n"
        "🎁 Бонусов выдано: <b>{bonus_issued}</b>\n"
        "🎁 Бонусов использовано: <b>{bonus_used}</b>"
    ),
    "top_products": "🔥 <b>Топ товаров:</b>\n{entries}",
    "top_customers": "🏆 <b>Топ клиентов:</b>\n{entries}",

    # Admin Settings
    "settings_title": "⚙️ <b>Настройки</b>",
    "working_hours_btn": "🕐 Рабочие часы",
    "min_order_btn": "💰 Мин. сумма заказа",
    "delivery_zones_btn": "📍 Зоны доставки",
    "restaurant_info_btn": "🏪 Информация о ресторане",
    "bonus_rate_btn": "🎁 Курс бонусов",
    "maintenance_btn": "🔧 Режим обслуживания",
    "enter_working_hours": "Введите рабочие часы (например: 10:00-22:00):",
    "working_hours_saved": "✅ Рабочие часы сохранены.",
    "bot_closed": "🔧 Ресторан сейчас закрыт. Приходите в рабочее время!",
    "maintenance_on": "🔧 Бот переведён в режим обслуживания.",
    "maintenance_off": "✅ Режим обслуживания отключён.",
    "setting_saved": "✅ Настройка сохранена.",

    # Admin Couriers
    "couriers_title": "🚚 <b>Курьеры:</b>",
    "courier_line": "{name} — {status} | Заказов: {count}",
    "add_courier_btn": "➕ Добавить курьера",
    "enter_courier_id": "Введите Telegram ID курьера:",
    "courier_added": "✅ Курьер добавлен.",
    "courier_removed": "✅ Курьер удалён.",
    "remove_courier_btn": "🗑 Удалить курьера",

    # Admin Reviews
    "admin_reviews_title": "⭐ <b>Отзывы:</b>",
    "review_admin_line": "⭐{rating} — {name}: {comment}",
    "publish_review_btn": "✅ Опубликовать",
    "hide_review_btn": "🙈 Скрыть",
    "reply_review_btn": "💬 Ответить",
    "enter_review_reply": "Введите ответ на отзыв:",
    "review_reply_sent": "✅ Ответ отправлен клиенту.",
    "review_published": "✅ Отзыв опубликован.",
    "review_hidden": "✅ Отзыв скрыт.",

    # Notifications
    "notif_order_paid": "✅ Ваш заказ <b>#{number}</b> оплачен! Готовим для вас 👨‍🍳",
    "notif_order_preparing": "👨‍🍳 Кухня готовит ваш заказ <b>#{number}</b>",
    "notif_order_ready": "🎉 Заказ <b>#{number}</b> готов! Забирайте 🏃",
    "notif_order_on_way": "🚚 Курьер выехал с вашим заказом <b>#{number}</b>!",
    "notif_order_completed": "✅ Заказ <b>#{number}</b> выполнен. Спасибо!",
    "notif_review_request": "⭐ Как вам заказ <b>#{number}</b>? Оцените нас!",
    "notif_birthday": "🎂 С Днём Рождения, <b>{name}</b>!\n🎁 Промокод на скидку 20%: <b>{code}</b>\nДействует 3 дня!",
    "notif_reengagement": "😴 Соскучились по нашей шаурме?\n🥙 Зайдите, у нас есть кое-что вкусное для вас!",
    "notif_birthday_soon": "🎂 Ваш день рождения скоро! Готовим для вас подарок 🎁",

    # Misc
    "error_occurred": "❌ Произошла ошибка. Попробуйте ещё раз.",
    "cancelled": "❌ Отменено.",
    "cancel_btn": "❌ Отмена",
    "confirm_btn": "✅ Подтвердить",
    "notifications_on": "🔔 Уведомления включены.",
    "notifications_off": "🔕 Уведомления отключены.",
    "user_not_registered": "Сначала зарегистрируйтесь через /start.",
    "banned_message": "🚫 Ваш аккаунт заблокирован. Обратитесь в поддержку.",
    "closed_message": "🔧 Ресторан закрыт. Рабочие часы: {hours}",
    "language_changed": "✅ Язык изменён на русский.",
    "enter_address_text": "Введите адрес доставки:",
}
