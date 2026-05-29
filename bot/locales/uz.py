"""Uzbek locale — every user-facing string in one dict."""

texts: dict = {
    # Language selection
    "choose_language": "🌐 <b>Tilni tanlang / Выберите язык:</b>",

    # Welcome & registration
    "welcome": "👋 <b>{name} ga xush kelibsiz!</b>\n\nSiz uchun eng mazali shaurma tayyorlaymiz 🥙",
    "request_phone": "📞 <b>Ro'yxatdan o'tish uchun telefon raqamingizni ulashing:</b>",
    "share_phone_btn": "📱 Raqamni ulashish",
    "registration_complete": "✅ <b>Ro'yxatdan o'tish tugallandi!</b>\nXush kelibsiz, {name}!",
    "phone_already_registered": "Siz allaqachon ro'yxatdan o'tgansiz!",

    # Main menu
    "main_menu": "🏠 <b>Asosiy menyu</b>\nQanday yordam bera olaman?",
    "catalog_btn": "🍽 Menyu",
    "cart_btn": "🛒 Savat",
    "profile_btn": "👤 Profil",
    "orders_btn": "📋 Buyurtmalarim",
    "referral_btn": "👥 Referral dastur",
    "reviews_btn": "⭐ Sharhlar",
    "help_btn": "❓ Yordam",
    "language_btn": "🌐 Til",

    # Catalog
    "choose_category": "🍽 <b>Kategoriyani tanlang:</b>",
    "choose_product": "<b>{category}</b> kategoriyasidan taom tanlang:",
    "product_card": "{badges}<b>{name}</b> — <b>{price} ₽</b>\n\n{description}",
    "product_unavailable": "❌ Mahsulot vaqtincha mavjud emas",
    "back_btn": "◀ Orqaga",
    "add_to_cart_btn": "🛒 Savatga",
    "no_products_in_category": "Bu kategoriyada hozircha mahsulotlar yo'q.",

    # Cart
    "cart_empty": "🛒 Savatingiz bo'sh.\n\nTaom tanlash uchun menyuga o'ting.",
    "cart_title": "🛒 <b>Savatingiz:</b>",
    "cart_item_line": "• {name} × {qty} = {subtotal} ₽",
    "cart_total": "\n💰 <b>Jami: {total} ₽</b>",
    "cart_bonus_available": "🎁 Mavjud bonuslar: {points} (maksimal {max} ₽)",
    "cart_promo_applied": "🏷 <b>{code}</b> promokod qo'llandi: −{discount} ₽",
    "checkout_btn": "✅ Buyurtma berish",
    "clear_cart_btn": "🗑 Savatni tozalash",
    "cart_cleared": "🗑 Savat tozalandi.",
    "apply_promo_btn": "🏷 Promokod",
    "use_bonus_btn": "🎁 Bonuslardan foydalanish",
    "enter_promo": "Promokodni kiriting:",
    "promo_valid": "✅ Promokod qabul qilindi! Chegirma: {discount} ₽",
    "promo_invalid": "❌ Promokod yaroqsiz yoki muddati o'tgan.",
    "promo_min_order": "❌ Ushbu promokod uchun minimal buyurtma summasi: {amount} ₽",
    "bonus_applied": "✅ {points} bonus ball ishlatildi = −{amount} ₽",
    "bonus_removed": "Bonus ballar olib tashlandi.",
    "not_enough_bonus": "❌ Bonus ballar yetarli emas.",
    "item_added_to_cart": "✅ <b>{name}</b> savatga qo'shildi!",

    # Order type
    "choose_order_type": "🚀 <b>Buyurtmani qanday olmoqchisiz?</b>",
    "pickup_btn": "🏪 Olib ketish",
    "taxi_btn": "🚕 Yandex Taxi",
    "delivery_btn": "🚚 Kuryer yetkazish",

    # Pickup
    "pickup_info": "🏪 <b>Olib ketish</b>\n\n📍 Manzil: <b>{address}</b>\n📞 Telefon: {phone}\n\nVaqtni tanlang:",
    "pickup_now": "⚡ Hozir",
    "pickup_15min": "⏰ 15 daqiqadan so'ng",
    "pickup_30min": "⏰ 30 daqiqadan so'ng",
    "pickup_custom": "🕐 Vaqtni ko'rsatish",
    "enter_pickup_time": "Olib ketish vaqtini kiriting (masalan: 14:30):",
    "pickup_confirmed": "✅ {time} da olib ketish. To'lovga o'tamiz.",

    # Taxi
    "taxi_intro": "🚕 <b>Yandex Taxi</b>\n\nBuyurtmangiz tayyorlanayotganda restoranga taksi chaqiramiz.\n\nGeolokatsiyangizni yuboring yoki manzilingizni kiriting:",
    "send_location_btn": "📍 Geolokatsiya yuborish",
    "or_type_address": "yoki manzilni matnga kiriting:",
    "taxi_ordering": "⏳ Taksi buyurtma qilinmoqda...",
    "taxi_ordered": "✅ <b>Taksi buyurtma qilindi!</b>\n\n🚗 {car} ({color})\n👤 Haydovchi: {driver}\n⏱ Kutish: {eta} daqiqa\n🔢 Raqam: <code>{plate}</code>",
    "taxi_driver_en_route": "🚗 Haydovchi sizga ketmoqda!",
    "taxi_driver_arrived": "📍 Haydovchi yetib keldi!",
    "taxi_cancelled": "❌ Taksi bekor qilindi.",
    "taxi_error": "❌ Taksi buyurtma qilib bo'lmadi. Qayta urinib ko'ring yoki boshqa usul tanlang.",

    # Delivery
    "delivery_intro": "🚚 <b>Kuryer yetkazish</b>\n\nGeolokatsiyangizni yuboring yoki yetkazish manzilini kiriting:",
    "delivery_calculating": "📏 Yetkazish narxi hisoblanmoqda...",
    "delivery_cost_info": "📍 Manzil: {address}\n📏 Masofa: {distance} km\n🚚 Yetkazish narxi: <b>{cost} ₽</b>\n\n💰 Yetkazish bilan jami: <b>{total} ₽</b>",
    "delivery_too_far": "❌ Afsuski, 15 km dan ortiq masofaga yetkazmiz.",
    "confirm_delivery_btn": "✅ Tasdiqlash",

    # Payment
    "payment_intro": "💳 <b>Buyurtma to'lovi</b>\n\nSumma: <b>{amount} ₽</b>\n\nTo'lov uchun quyidagi tugmani bosing:",
    "pay_btn": "💳 {amount} ₽ to'lash",
    "payment_pending": "⏳ To'lov kutilmoqda...",
    "payment_success": (
        "✅ <b>To'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
        "🧾 Buyurtma <b>#{order_number}</b>\n"
        "💰 To'langan: <b>{amount} ₽</b>\n\n"
        "QR kodni kassirga ko'rsating 👇"
    ),
    "payment_failed": "❌ To'lov amalga oshmadi. Qayta urinib ko'ring.",
    "payment_cancelled": "To'lov bekor qilindi.",
    "order_confirmed_admin": (
        "🆕 <b>Yangi buyurtma #{order_number}</b>\n"
        "👤 {customer}\n📞 {phone}\n"
        "📦 Turi: {order_type}\n"
        "📍 {address}\n"
        "🍖 {items}\n"
        "💰 {total} ₽"
    ),

    # Order statuses
    "status_pending": "⏳ To'lov kutilmoqda",
    "status_paid": "✅ To'langan",
    "status_preparing": "👨‍🍳 Tayyorlanmoqda",
    "status_ready": "🎉 Tayyor!",
    "status_on_the_way": "🚚 Kuryer yo'lda",
    "status_completed": "✅ Bajarildi",
    "status_cancelled": "❌ Bekor qilindi",

    "order_status_update": "📦 <b>Buyurtma #{order_number}</b>\nHolat: {status}",
    "order_preparing_msg": "👨‍🍳 Oshxona buyurtmangizni tayyorlashni boshladi!",
    "order_ready_msg": "🎉 Buyurtmangiz tayyor! Sizni kutamiz 🏃",
    "order_on_way_msg": "🚚 Kuryer yo'lga chiqdi! Kuting.",

    # Profile
    "profile_title": "👤 <b>Sizning profilingiz</b>",
    "profile_info": (
        "👤 <b>{name}</b>\n"
        "📞 {phone}\n"
        "🎁 Bonus ballari: <b>{bonus}</b>\n"
        "💰 Jami sarflangan: <b>{spent} ₽</b>\n"
        "👥 Taklif qilingan do'stlar: <b>{referrals}</b>"
    ),
    "order_history_btn": "📋 Buyurtmalar tarixi",
    "settings_btn": "⚙️ Sozlamalar",
    "my_referral_btn": "🔗 Mening referral kodim",
    "edit_language_btn": "🌐 Tilni o'zgartirish",
    "notifications_btn": "🔔 Bildirishnomalar",
    "no_orders_yet": "Sizda hali buyurtmalar yo'q.",
    "order_history_item": "#{number} — {date} — {amount} ₽ — {status}",

    # Referral
    "referral_title": "👥 <b>Referral dastur</b>",
    "referral_info": (
        "🔗 Sizning referral havolangiz:\n{link}\n\n"
        "👥 Taklif qilingan: <b>{count}</b> do'st\n"
        "🎁 Topilgan bonuslar: <b>{earned}</b> ball\n\n"
        "Birinchi buyurtma bergan har bir do'st uchun:\n"
        "• Sizga: +150 ball\n"
        "• Do'stingizga: 10% chegirma"
    ),
    "referral_leaderboard": "🏆 <b>Top referrerlar:</b>\n{entries}",
    "referral_leaderboard_entry": "{pos}. {name} — {count} do'st",
    "referral_bonus_received": "🎁 Do'stingiz birinchi buyurtma berdi! +150 bonus ball!",
    "new_user_ref_discount": "🎉 Do'st taklif qildi! Birinchi buyurtmada 10% chegirma qo'llandi.",

    # Bonus
    "bonus_title": "🎁 <b>Bonus dasturi</b>",
    "bonus_info": (
        "💎 Sizning bonuslaringiz: <b>{points}</b> ball\n\n"
        "📈 Qoidalar:\n"
        "• Har 100 ₽ = 5 bonus ball\n"
        "• 1 ball = 1 ₽ chegirma\n"
        "• Buyurtma summasining 30% gacha to'lash mumkin\n"
        "• Balllar 90 kundan so'ng yonadi"
    ),
    "bonus_history_btn": "📊 Balllar tarixi",
    "bonus_transaction_line": "{date}: {sign}{amount} — {reason}",

    # Promo
    "enter_promo_code": "🏷 Promokodni kiriting:",
    "promo_applied_success": "✅ Promokod <b>{code}</b> qo'llandi!\nChegirma: <b>{discount} ₽</b>",

    # Reviews
    "review_request": "⭐ <b>#{order_number} buyurtmangiz qanday bo'ldi?</b>\n1 dan 5 gacha baho bering:",
    "review_comment_prompt": "Izoh qoldirmoqchimisiz?",
    "review_yes_btn": "✍️ Ha, yozaman",
    "review_no_btn": "Yo'q, rahmat",
    "enter_review_comment": "✍️ Sharhingizni yozing:",
    "review_saved": "✅ Sharhingiz uchun rahmat! Fikringiz bizga juda muhim 🙏",
    "reviews_title": "⭐ <b>Mijozlar sharhlari:</b>",
    "review_item": "⭐ {rating} — <b>{name}</b>\n{comment}\n<i>{date}</i>",
    "no_reviews": "Hozircha nashr etilgan sharhlar yo'q.",
    "review_reply": "💬 <b>Restoran javobi:</b> {reply}",

    # Courier
    "courier_menu": "🚚 <b>Kuryer menyusi</b>",
    "new_delivery_notification": (
        "📦 <b>Yangi buyurtma #{order_number}</b>\n"
        "📍 <b>{address}</b>\n"
        "📞 Mijoz: {phone}\n"
        "🍖 {items}\n"
        "💰 {total} ₽"
    ),
    "accept_order_btn": "✅ Buyurtmani qabul qilish",
    "order_accepted_courier": "✅ Siz #{order_number} buyurtmani qabul qildingiz",
    "order_already_taken": "❌ Buyurtma boshqa kuryer tomonidan qabul qilingan.",
    "courier_departed_btn": "🚗 Yo'lga chiqdim",
    "courier_arrived_btn": "📍 Yetib keldim",
    "courier_delivered_btn": "✅ Yetkazildi",
    "courier_departed_msg": "🚗 Kuryer sizga yo'lga chiqdi!",
    "courier_arrived_msg": "📍 Kuryer yetib keldi!",
    "order_delivered_msg": "✅ Buyurtma yetkazildi! Bizni tanlaganingiz uchun rahmat 🙏",
    "no_active_orders": "Faol buyurtmalaringiz yo'q.",
    "courier_accepted_client": "✅ <b>{name}</b> kuryer buyurtmangizni qabul qildi!",

    # Admin
    "admin_welcome": "🔐 <b>Administrator paneli</b>",
    "admin_dashboard": (
        "📊 <b>Dashboard</b>\n\n"
        "📦 Bugungi buyurtmalar: <b>{orders_today}</b>\n"
        "💰 Bugungi daromad: <b>{revenue_today} ₽</b>\n"
        "📈 Haftalik daromad: <b>{revenue_week} ₽</b>\n"
        "👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        "👤 Bugun yangilar: <b>{new_today}</b>\n"
        "🔥 Faol buyurtmalar: <b>{active_orders}</b>"
    ),
    "admin_products_btn": "📦 Mahsulotlar",
    "admin_orders_btn": "📋 Buyurtmalar",
    "admin_users_btn": "👥 Foydalanuvchilar",
    "admin_broadcast_btn": "📢 Xabar yuborish",
    "admin_promo_btn": "🎁 Promokodlar",
    "admin_stats_btn": "📊 Statistika",
    "admin_settings_btn": "⚙️ Sozlamalar",
    "admin_couriers_btn": "🚚 Kuryerlar",
    "admin_reviews_btn": "⭐ Sharhlar",
    "back_to_admin": "◀ Asosiy menyu",

    # Admin Products
    "product_list_title": "📦 <b>Mahsulotlar ro'yxati:</b>",
    "add_product_btn": "➕ Mahsulot qo'shish",
    "product_line": "{status} {badges}{name} — {price} ₽",
    "enter_product_name_ru": "Mahsulot nomini kiriting (RU):",
    "enter_product_name_uz": "Mahsulot nomini kiriting (UZ):",
    "enter_product_desc_ru": "Mahsulot tavsifini kiriting (RU):",
    "enter_product_desc_uz": "Mahsulot tavsifini kiriting (UZ):",
    "enter_product_price": "Narxni kiriting (rublda):",
    "enter_product_photo": "Mahsulot rasmini yuboring:",
    "choose_category_for_product": "Kategoriyani tanlang:",
    "product_added": "✅ <b>{name}</b> mahsuloti qo'shildi!",
    "product_updated": "✅ Mahsulot yangilandi.",
    "product_deleted": "🗑 Mahsulot o'chirildi.",
    "toggle_available": "Mavjudlik o'zgartirildi.",
    "toggle_new_badge": "🆕 belgisi o'zgartirildi.",
    "toggle_hot_badge": "🔥 belgisi o'zgartirildi.",
    "invalid_price": "❌ Noto'g'ri narx. Raqam kiriting.",

    # Admin Orders
    "orders_list_title": "📋 <b>Buyurtmalar:</b>",
    "order_detail": (
        "📦 <b>Buyurtma #{number}</b>\n"
        "👤 {customer}\n📞 {phone}\n"
        "📅 {date}\n"
        "📦 Turi: {order_type}\n"
        "📍 {address}\n"
        "🍖 Tarkib:\n{items}\n"
        "💰 Jami: <b>{total} ₽</b>\n"
        "🏷 Holat: <b>{status}</b>"
    ),
    "change_status_btn": "🔄 Holatni o'zgartirish",
    "cancel_order_btn": "❌ Buyurtmani bekor qilish",
    "order_cancelled_refund": "✅ Buyurtma bekor qilindi, qaytarish boshlandi.",
    "export_csv_btn": "📥 CSV eksport",

    # Admin Users
    "user_detail": (
        "👤 <b>{name}</b> (@{username})\n"
        "📞 {phone}\n"
        "🎁 Bonuslar: {bonus}\n"
        "💰 Sarflangan: {spent} ₽\n"
        "📦 Buyurtmalar: {orders_count}\n"
        "📅 Ro'yxatdan o'tgan: {reg_date}\n"
        "🔒 Holat: {status}"
    ),
    "ban_user_btn": "🚫 Bloklash",
    "unban_user_btn": "✅ Blokdan chiqarish",
    "user_banned": "🚫 Foydalanuvchi bloklandi.",
    "user_unbanned": "✅ Foydalanuvchi blokdan chiqarildi.",
    "add_bonus_btn": "🎁 Bonus qo'shish",
    "enter_bonus_amount": "Ball miqdorini kiriting:",
    "bonus_added_admin": "✅ {amount} ball qo'shildi.",
    "send_message_btn": "💬 Xabar yuborish",
    "enter_message_for_user": "Xabarni kiriting:",
    "message_sent": "✅ Xabar yuborildi.",

    # Admin Broadcast
    "broadcast_title": "📢 <b>Xabar yuborish</b>",
    "broadcast_text_only_btn": "📝 Faqat matn",
    "broadcast_with_photo_btn": "🖼 Matn + rasm",
    "broadcast_with_btn_btn": "🔗 Matn + tugma",
    "enter_broadcast_text": "Xabar matnini kiriting:",
    "enter_broadcast_photo": "Rasmni yuboring:",
    "enter_broadcast_btn_text": "Tugma matnini kiriting:",
    "enter_broadcast_btn_url": "Tugma URL sini kiriting:",
    "choose_broadcast_audience": "Auditoriyani tanlang:",
    "audience_all": "👥 Barcha foydalanuvchilar",
    "audience_active": "✅ Faol (30 kun)",
    "audience_ordered": "📦 Buyurtma berganlar",
    "schedule_or_now": "Hozir yoki keyinroq yuborish?",
    "send_now_btn": "⚡ Hozir",
    "schedule_btn": "🕐 Rejalashtirish",
    "enter_schedule_time": "Sana/vaqtni kiriting (KK.OO.YYYY SS:MM):",
    "broadcast_scheduled": "✅ Xabar {time} ga rejalashtirildi.",
    "broadcast_sent": "✅ Xabar yuborildi!\n📤 Yuborildi: {sent}\n❌ Xato: {failed}",

    # Admin Promo
    "promo_list_title": "🎁 <b>Promokodlar:</b>",
    "promo_line": "{code} — {type} {value} | Ishlatildi: {used}/{max}",
    "add_promo_btn": "➕ Promokod yaratish",
    "enter_promo_code_admin": "Kodni kiriting:",
    "choose_promo_type": "Chegirma turi:",
    "promo_percent_btn": "% Foiz",
    "promo_fixed_btn": "₽ Belgilangan",
    "enter_promo_value": "Chegirma qiymatini kiriting:",
    "enter_promo_min_order": "Minimal buyurtma summasi (0 = cheksiz):",
    "enter_promo_max_uses": "Maks. foydalanishlar (0 = cheksiz):",
    "enter_promo_valid_to": "Tugash sanasi (KK.OO.YYYY yoki 0 = muddatsiz):",
    "promo_created": "✅ Promokod <b>{code}</b> yaratildi!",
    "promo_deactivated": "✅ Promokod o'chirildi.",

    # Admin Statistics
    "stats_title": "📊 <b>Statistika</b>",
    "stats_detail": (
        "📅 <b>Davr: {period}</b>\n\n"
        "💰 Daromad: <b>{revenue} ₽</b>\n"
        "📦 Jami buyurtmalar: <b>{orders}</b>\n"
        "✅ Bajarildi: <b>{completed}</b>\n"
        "❌ Bekor qilindi: <b>{cancelled}</b>\n"
        "📊 O'rtacha chek: <b>{avg_order} ₽</b>\n"
        "🚚 Yetkazish: <b>{delivery_count}</b>\n"
        "🏪 Olib ketish: <b>{pickup_count}</b>\n"
        "🚕 Taksi: <b>{taxi_count}</b>\n"
        "🎁 Bonus berildi: <b>{bonus_issued}</b>\n"
        "🎁 Bonus ishlatildi: <b>{bonus_used}</b>"
    ),
    "top_products": "🔥 <b>Top mahsulotlar:</b>\n{entries}",
    "top_customers": "🏆 <b>Top mijozlar:</b>\n{entries}",

    # Admin Settings
    "settings_title": "⚙️ <b>Sozlamalar</b>",
    "working_hours_btn": "🕐 Ish soatlari",
    "min_order_btn": "💰 Minimal buyurtma summasi",
    "delivery_zones_btn": "📍 Yetkazish zonalari",
    "restaurant_info_btn": "🏪 Restoran ma'lumotlari",
    "bonus_rate_btn": "🎁 Bonus kursi",
    "maintenance_btn": "🔧 Texnik xizmat rejimi",
    "enter_working_hours": "Ish soatlarini kiriting (masalan: 10:00-22:00):",
    "working_hours_saved": "✅ Ish soatlari saqlandi.",
    "bot_closed": "🔧 Restoran hozir yopiq. Ish vaqtida tashrif buyuring!",
    "maintenance_on": "🔧 Bot texnik xizmat rejimiga o'tkazildi.",
    "maintenance_off": "✅ Texnik xizmat rejimi o'chirildi.",
    "setting_saved": "✅ Sozlama saqlandi.",

    # Admin Couriers
    "couriers_title": "🚚 <b>Kuryerlar:</b>",
    "courier_line": "{name} — {status} | Buyurtmalar: {count}",
    "add_courier_btn": "➕ Kuryer qo'shish",
    "enter_courier_id": "Kuryer Telegram ID sini kiriting:",
    "courier_added": "✅ Kuryer qo'shildi.",
    "courier_removed": "✅ Kuryer o'chirildi.",
    "remove_courier_btn": "🗑 Kuryerni o'chirish",

    # Admin Reviews
    "admin_reviews_title": "⭐ <b>Sharhlar:</b>",
    "review_admin_line": "⭐{rating} — {name}: {comment}",
    "publish_review_btn": "✅ Nashr qilish",
    "hide_review_btn": "🙈 Yashirish",
    "reply_review_btn": "💬 Javob berish",
    "enter_review_reply": "Sharhga javob kiriting:",
    "review_reply_sent": "✅ Javob mijozga yuborildi.",
    "review_published": "✅ Sharh nashr etildi.",
    "review_hidden": "✅ Sharh yashirildi.",

    # Notifications
    "notif_order_paid": "✅ <b>#{number}</b> buyurtmangiz to'landi! Tayyorlamoqdamiz 👨‍🍳",
    "notif_order_preparing": "👨‍🍳 Oshxona <b>#{number}</b> buyurtmangizni tayyorlamoqda",
    "notif_order_ready": "🎉 <b>#{number}</b> buyurtmangiz tayyor! Olib keting 🏃",
    "notif_order_on_way": "🚚 Kuryer <b>#{number}</b> buyurtmangiz bilan yo'lga chiqdi!",
    "notif_order_completed": "✅ <b>#{number}</b> buyurtma bajarildi. Rahmat!",
    "notif_review_request": "⭐ <b>#{number}</b> buyurtmangiz qanday bo'ldi? Bizga baho bering!",
    "notif_birthday": "🎂 Tug'ilgan kuningiz bilan, <b>{name}</b>!\n🎁 20% chegirma promokodi: <b>{code}</b>\n3 kun amal qiladi!",
    "notif_reengagement": "😴 Shaurmamizni sog'indingizmi?\n🥙 Kiring, siz uchun mazali narsalar bor!",
    "notif_birthday_soon": "🎂 Tug'ilgan kuningiz yaqin! Siz uchun sovg'a tayyorlamoqdamiz 🎁",

    # Misc
    "error_occurred": "❌ Xato yuz berdi. Qayta urinib ko'ring.",
    "cancelled": "❌ Bekor qilindi.",
    "cancel_btn": "❌ Bekor qilish",
    "confirm_btn": "✅ Tasdiqlash",
    "notifications_on": "🔔 Bildirishnomalar yoqildi.",
    "notifications_off": "🔕 Bildirishnomalar o'chirildi.",
    "user_not_registered": "Avval /start orqali ro'yxatdan o'ting.",
    "banned_message": "🚫 Hisobingiz bloklangan. Qo'llab-quvvatlash xizmatiga murojaat qiling.",
    "closed_message": "🔧 Restoran yopiq. Ish soatlari: {hours}",
    "language_changed": "✅ Til o'zbekchaga o'zgartirildi.",
    "enter_address_text": "Yetkazish manzilini kiriting:",
}
