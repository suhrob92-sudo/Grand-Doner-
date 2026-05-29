# 🥙 Shaurma House — Telegram Bot

Production-ready Telegram bot for an Uzbek shawarma restaurant in Russia.

## Tech Stack

| Component | Library |
|-----------|---------|
| Bot framework | aiogram 3.x (async) |
| Database | PostgreSQL + SQLAlchemy (async) |
| FSM storage | Redis |
| Payments | YooKassa SDK |
| Delivery | Yandex Taxi Business API |
| QR codes | qrcode + Pillow |
| Scheduler | APScheduler |
| Web server | aiohttp (webhook mode) |

---

## Project Structure

```
bot/
├── main.py                  # Entry point — webhook + scheduler
├── config.py                # Pydantic settings from .env
├── .env.example             # Environment variable template
├── requirements.txt
├── alembic/                 # DB migrations
│   ├── env.py
│   └── versions/
├── middlewares/
│   ├── language.py          # Auto-detect user language from DB
│   ├── throttling.py        # 1 msg/sec rate limit via Redis
│   └── auth.py              # Ban check
├── handlers/
│   ├── start.py             # /start, language selection, registration
│   ├── language.py          # /language command
│   ├── menu.py              # Category/product catalog
│   ├── cart.py              # Cart management (Redis)
│   ├── order.py             # Order creation (shared logic)
│   ├── payment.py           # YooKassa payment + webhook
│   ├── taxi.py              # Yandex Taxi flow
│   ├── delivery.py          # Courier delivery flow
│   ├── courier.py           # Courier-facing handlers
│   ├── profile.py           # User profile & history
│   ├── referral.py          # Referral program
│   ├── bonus.py             # Bonus points
│   ├── reviews.py           # Review submission
│   └── admin/               # Full admin panel
│       ├── dashboard.py     # Stats overview
│       ├── products.py      # CRUD products
│       ├── orders.py        # Order management
│       ├── users.py         # User management
│       ├── broadcast.py     # Mass messaging
│       ├── promo.py         # Promo code management
│       ├── statistics.py    # Revenue/order stats
│       ├── settings.py      # Bot settings
│       ├── couriers.py      # Courier management
│       └── reviews.py       # Review moderation
├── models/                  # SQLAlchemy ORM models
├── services/
│   ├── yookassa.py          # Payment integration
│   ├── yandex_taxi.py       # Taxi API integration
│   ├── qr_generator.py      # QR code images
│   ├── broadcast.py         # Bulk messaging
│   ├── scheduler.py         # Scheduled tasks
│   └── statistics.py        # DB aggregations
├── locales/
│   ├── ru.py                # Russian translations
│   └── uz.py                # Uzbek translations
└── utils/
    ├── i18n.py              # Translation helper _()
    ├── decorators.py        # @handle_errors
    ├── validators.py        # Phone/price/date validation
    └── helpers.py           # Distance, QR helpers, formatters
```

---

## Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- A domain with SSL (for webhooks)

### 2. Clone & install

```bash
git clone <repo>
cd Grand-Doner-/bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

Required variables:
```
BOT_TOKEN=            # BotFather token
ADMIN_IDS=            # Comma-separated Telegram IDs
DATABASE_URL=         # postgresql+asyncpg://...
REDIS_URL=            # redis://...
YOOKASSA_SHOP_ID=     # YooKassa shop ID
YOOKASSA_SECRET_KEY=  # YooKassa secret
WEBHOOK_URL=          # https://yourdomain.com
YANDEX_TAXI_API_KEY=  # Yandex Taxi Business API key
YANDEX_TAXI_CLIENT_ID=
YANDEX_TAXI_PARK_ID=
```

### 4. Initialize the database

```bash
# Create DB
createdb shaurma_bot

# Run Alembic migrations
cd bot
alembic upgrade head

# Or use the auto-create shortcut (development only):
python -c "import asyncio; from models.base import init_db; asyncio.run(init_db())"
```

### 5. Seed initial categories (run once)

```python
# Run from bot/ directory
import asyncio
from models.base import AsyncSessionLocal
from models.category import Category

async def seed():
    async with AsyncSessionLocal() as s:
        cats = [
            Category(name_ru="Шаурма", name_uz="Shaurma", emoji="🥙", sort_order=1),
            Category(name_ru="Бургеры", name_uz="Burgerlar", emoji="🍔", sort_order=2),
            Category(name_ru="Картошка фри", name_uz="Kartoshka fri", emoji="🍟", sort_order=3),
            Category(name_ru="Напитки", name_uz="Ichimliklar", emoji="🥤", sort_order=4),
            Category(name_ru="Комбо-сеты", name_uz="Kombo-setlar", emoji="🍱", sort_order=5),
            Category(name_ru="Салаты", name_uz="Salatlar", emoji="🥗", sort_order=6),
        ]
        s.add_all(cats)
        await s.commit()

asyncio.run(seed())
```

### 6. Set up webhook

Configure your web server (nginx example):

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    location /webhook/bot {
        proxy_pass http://127.0.0.1:8080;
    }

    location /webhook/yookassa {
        proxy_pass http://127.0.0.1:8080;
    }
}
```

### 7. Run the bot

```bash
cd bot
python main.py
```

### 8. Run with systemd (production)

```ini
# /etc/systemd/system/shaurma-bot.service
[Unit]
Description=Shaurma House Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Grand-Doner-/bot
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=5
EnvironmentFile=/path/to/Grand-Doner-/bot/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable shaurma-bot
sudo systemctl start shaurma-bot
sudo journalctl -u shaurma-bot -f
```

---

## Features

### For customers
- 🌐 Language selection (Russian / Uzbek)
- 📱 Phone registration
- 🍽 Menu catalog with categories, photos, badges (🆕🔥)
- 🛒 Cart with promo codes and bonus points
- 🏪 Pickup — time selection
- 🚕 Yandex Taxi — order taxi to restaurant
- 🚚 Courier delivery — geolocation, distance pricing
- 💳 YooKassa payment + QR code receipt
- 🎁 Bonus points (5 pts / 100 ₽, valid 90 days)
- 👥 Referral program (+150 pts for referrer, 10% for new user)
- ⭐ Post-order reviews with admin reply
- 🎂 Birthday promo (20% off, 3 days)

### For admins (`/admin`)
- 📊 Real-time dashboard
- 📦 Full product CRUD (photos, bilingual, badges)
- 📋 Order management with status updates and CSV export
- 👥 User search, ban, bonus, personal message
- 📢 Broadcast (text/photo/button, scheduled, segmented)
- 🎁 Promo code creation (% or ₽, limits, dates)
- 📈 Revenue/order statistics with top products/customers
- ⚙️ Settings (working hours, maintenance mode, bonus rate)
- 🚚 Courier management

### For couriers (`/courier_menu`)
- 📦 Accept new delivery orders
- 🚗 Departed / Arrived / Delivered status updates
- Real-time notifications to customers

### Automated (APScheduler)
- Bonus point expiry (daily at 03:00)
- Birthday promo generation (daily at 09:00)
- Re-engagement push (weekly on Monday)

---

## Development notes

- All handlers use `@handle_errors` decorator — no unhandled exceptions
- Cart is stored in Redis (TTL 24h)
- All payments go through YooKassa webhook `/webhook/yookassa`
- Taxi orders are tracked with background asyncio tasks polling every 60s
- Courier notifications fan out to all registered couriers simultaneously
- All DB operations use async SQLAlchemy sessions via `AsyncSessionLocal`
