# 🥙 Shaurma House — Telegram Bot

Production-ready Telegram bot for an Uzbek shawarma restaurant in Russia.

---

## 🚀 Deploy to Render + UptimeRobot (free 24/7)

### Step 1 — Free services you need

| Service | Free tier | Link |
|---------|-----------|------|
| **Render** | Web service (sleeps after 15 min on free) | render.com |
| **UptimeRobot** | Pings every 5 min → keeps Render awake | uptimerobot.com |
| **Neon** (PostgreSQL) | 512 MB free forever | neon.tech |
| **Upstash** (Redis) | 10K req/day free | upstash.com |

---

### Step 2 — PostgreSQL on Neon

1. Go to [neon.tech](https://neon.tech) → New project
2. Copy the **connection string** — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb
   ```
3. Change the scheme to `asyncpg`:
   ```
   postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

---

### Step 3 — Redis on Upstash

1. Go to [upstash.com](https://upstash.com) → Create database → **Redis**
2. Region: **EU (Frankfurt)** — closest to Russia
3. Copy the **Redis URL** (starts with `rediss://`)

---

### Step 4 — Deploy on Render

1. Push this repo to GitHub (already done ✅)
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Settings:
   ```
   Root Directory : bot
   Build Command  : pip install -r requirements.txt
   Start Command  : python main.py
   ```
5. Under **Environment Variables** add:

   | Key | Value |
   |-----|-------|
   | `BOT_TOKEN` | Your BotFather token |
   | `ADMIN_IDS` | Your Telegram ID (e.g. `123456789`) |
   | `DATABASE_URL` | Neon connection string (asyncpg) |
   | `REDIS_URL` | Upstash Redis URL |
   | `WEBHOOK_URL` | Leave **blank for now** (fill after deploy) |
   | `YOOKASSA_SHOP_ID` | YooKassa shop ID |
   | `YOOKASSA_SECRET_KEY` | YooKassa secret |
   | `RESTAURANT_NAME` | Shaurma House |
   | `RESTAURANT_ADDRESS` | Your address |
   | `RESTAURANT_LAT` | Your latitude |
   | `RESTAURANT_LON` | Your longitude |
   | `RESTAURANT_PHONE` | +7XXXXXXXXXX |

6. Click **Deploy** → wait ~2 min

7. After deploy, copy your Render URL:
   ```
   https://shaurma-bot.onrender.com
   ```

8. Go back to **Environment → Edit** → set:
   ```
   WEBHOOK_URL = https://shaurma-bot.onrender.com
   ```
   → **Save** (triggers redeploy)

---

### Step 5 — Run DB migrations (one time)

In Render dashboard → your service → **Shell**:
```bash
python -c "import asyncio; from models.base import init_db; asyncio.run(init_db())"
```

Seed initial categories:
```bash
python -c "
import asyncio
from models.base import AsyncSessionLocal
from models.category import Category

async def seed():
    async with AsyncSessionLocal() as s:
        s.add_all([
            Category(name_ru='Шаурма',       name_uz='Shaurma',       emoji='🥙', sort_order=1),
            Category(name_ru='Бургеры',      name_uz='Burgerlar',     emoji='🍔', sort_order=2),
            Category(name_ru='Картошка фри', name_uz='Kartoshka fri', emoji='🍟', sort_order=3),
            Category(name_ru='Напитки',      name_uz='Ichimliklar',   emoji='🥤', sort_order=4),
            Category(name_ru='Комбо-сеты',   name_uz='Kombo-setlar',  emoji='🍱', sort_order=5),
            Category(name_ru='Салаты',       name_uz='Salatlar',      emoji='🥗', sort_order=6),
        ])
        await s.commit()

asyncio.run(seed())
"
```

---

### Step 6 — Keep alive with UptimeRobot

Render free tier sleeps after **15 minutes** of no traffic.
UptimeRobot pings `/health` every **5 minutes** — bot never sleeps.

1. Go to [uptimerobot.com](https://uptimerobot.com) → **Add New Monitor**
2. Settings:
   ```
   Monitor Type : HTTP(s)
   Friendly Name: Shaurma Bot
   URL          : https://shaurma-bot.onrender.com/health
   Monitoring Interval: 5 minutes
   ```
3. Click **Create Monitor** ✅

The `/health` endpoint returns:
```json
{"status": "ok", "ts": "2025-01-15T10:30:00"}
```

---

### Step 7 — Verify everything works

```
https://shaurma-bot.onrender.com/health     → {"status":"ok","ts":"..."}
https://shaurma-bot.onrender.com/           → {"status":"ok","ts":"..."}
```

Then open Telegram → find your bot → send `/start` 🎉

---

### YooKassa webhook (important!)

In your YooKassa dashboard set the webhook URL to:
```
https://shaurma-bot.onrender.com/webhook/yookassa
```

---

### Upgrade to always-on (optional)

Render **Starter plan ($7/month)** removes the sleep entirely.
When you're ready: Render dashboard → your service → **Upgrade plan**.

---

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
