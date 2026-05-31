"""Seed default categories and sample products on first run."""

import logging
from sqlalchemy import select
from models.base import AsyncSessionLocal
from models.category import Category
from models.product import Product

logger = logging.getLogger(__name__)

CATEGORIES = [
    {"name_ru": "Шаурма",       "name_uz": "Shaurma",        "emoji": "🥙", "sort_order": 1},
    {"name_ru": "Бургеры",      "name_uz": "Burgerlar",      "emoji": "🍔", "sort_order": 2},
    {"name_ru": "Картошка фри", "name_uz": "Kartoshka fri",  "emoji": "🍟", "sort_order": 3},
    {"name_ru": "Напитки",      "name_uz": "Ichimliklar",    "emoji": "🥤", "sort_order": 4},
    {"name_ru": "Комбо-сеты",   "name_uz": "Kombo-setlar",   "emoji": "🍱", "sort_order": 5},
]

PRODUCTS = [
    # Шаурма
    {
        "name_ru": "Шаурма классическая",
        "name_uz": "Klassik shaurma",
        "description_ru": "Сочная шаурма с куриным мясом, свежими овощами и фирменным соусом. Завёрнута в тонкий лаваш.",
        "description_uz": "Tovuq go'shti, yangi sabzavotlar va maxsus sous bilan mazali shaurma. Yupqa lavashga o'ralgan.",
        "price": 35000,  # 350 ₽
        "cat_index": 0,
        "is_hot": True,
        "is_new": False,
        "sort_order": 1,
    },
    {
        "name_ru": "Шаурма острая",
        "name_uz": "Achchiq shaurma",
        "description_ru": "Шаурма с острым перцем и чесночным соусом. Для любителей остренького!",
        "description_uz": "Achchiq qalampir va sarimsoq sous bilan shaurma. Achchiq yaxshi ko'ruvchilar uchun!",
        "price": 38000,
        "cat_index": 0,
        "is_hot": True,
        "is_new": False,
        "sort_order": 2,
    },
    {
        "name_ru": "Шаурма с говядиной",
        "name_uz": "Mol go'shtli shaurma",
        "description_ru": "Нежная говядина с хрустящими овощами и сыром.",
        "description_uz": "Yumshoq mol go'shti, qo'shimcha sabzavotlar va pishloq bilan.",
        "price": 42000,
        "cat_index": 0,
        "is_hot": False,
        "is_new": True,
        "sort_order": 3,
    },
    # Бургеры
    {
        "name_ru": "Бургер классический",
        "name_uz": "Klassik burger",
        "description_ru": "Сочная котлета, свежие овощи, специальный соус, булочка с кунжутом.",
        "description_uz": "Shirali kotlet, yangi sabzavotlar, maxsus sous, kunjutli bulochka.",
        "price": 32000,
        "cat_index": 1,
        "is_hot": False,
        "is_new": False,
        "sort_order": 1,
    },
    {
        "name_ru": "Двойной бургер",
        "name_uz": "Qo'sh burger",
        "description_ru": "Две котлеты, двойной сыр и все любимые добавки.",
        "description_uz": "Ikki kotlet, qo'sh pishloq va barcha sevimli qo'shimchalar.",
        "price": 45000,
        "cat_index": 1,
        "is_hot": True,
        "is_new": False,
        "sort_order": 2,
    },
    # Картошка фри
    {
        "name_ru": "Картошка фри маленькая",
        "name_uz": "Kichik kartoshka fri",
        "description_ru": "Хрустящая картошка фри с солью.",
        "description_uz": "Tuzlangan qiyqir kartoshka fri.",
        "price": 12000,
        "cat_index": 2,
        "is_hot": False,
        "is_new": False,
        "sort_order": 1,
    },
    {
        "name_ru": "Картошка фри большая",
        "name_uz": "Katta kartoshka fri",
        "description_ru": "Большая порция хрустящей картошки фри.",
        "description_uz": "Katta porsiya qiyqir kartoshka fri.",
        "price": 18000,
        "cat_index": 2,
        "is_hot": False,
        "is_new": False,
        "sort_order": 2,
    },
    # Напитки
    {
        "name_ru": "Кола 0.5л",
        "name_uz": "Kola 0.5l",
        "description_ru": "Освежающая Coca-Cola в бутылке 0.5л.",
        "description_uz": "Yangilovchi Coca-Cola 0.5l shishada.",
        "price": 8000,
        "cat_index": 3,
        "is_hot": False,
        "is_new": False,
        "sort_order": 1,
    },
    {
        "name_ru": "Айран",
        "name_uz": "Ayron",
        "description_ru": "Свежий кисломолочный напиток. Отлично подходит к шаурме.",
        "description_uz": "Yangi kefirli ichimlik. Shaurma bilan juda mos.",
        "price": 7000,
        "cat_index": 3,
        "is_hot": False,
        "is_new": False,
        "sort_order": 2,
    },
    # Комбо-сеты
    {
        "name_ru": "Комбо Шаурма + Фри + Кола",
        "name_uz": "Kombo Shaurma + Fri + Kola",
        "description_ru": "Классическая шаурма + картошка фри + кола 0.5л. Выгодно!",
        "description_uz": "Klassik shaurma + kartoshka fri + kola 0.5l. Foydali!",
        "price": 50000,
        "cat_index": 4,
        "is_hot": True,
        "is_new": True,
        "sort_order": 1,
    },
    {
        "name_ru": "Комбо 2 шаурмы + 2 напитка",
        "name_uz": "Kombo 2 shaurma + 2 ichimlik",
        "description_ru": "Две классические шаурмы и два напитка на ваш выбор.",
        "description_uz": "Ikkita klassik shaurma va ikki xil ichimlik.",
        "price": 75000,
        "cat_index": 4,
        "is_hot": False,
        "is_new": True,
        "sort_order": 2,
    },
]


async def seed_data() -> None:
    """Insert default categories and products if DB is empty."""
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Category))).scalars().first()
        if existing:
            return  # already seeded

        logger.info("Seeding default categories and products...")

        cat_objects = []
        for cat in CATEGORIES:
            obj = Category(**cat)
            session.add(obj)
            cat_objects.append(obj)

        await session.flush()  # get IDs

        for p in PRODUCTS:
            cat = cat_objects[p["cat_index"]]
            product = Product(
                name_ru=p["name_ru"],
                name_uz=p["name_uz"],
                description_ru=p["description_ru"],
                description_uz=p["description_uz"],
                price=p["price"],
                category_id=cat.id,
                is_hot=p["is_hot"],
                is_new=p["is_new"],
                is_available=True,
                sort_order=p["sort_order"],
            )
            session.add(product)

        await session.commit()
        logger.info("Seeded %d categories and %d products", len(CATEGORIES), len(PRODUCTS))
