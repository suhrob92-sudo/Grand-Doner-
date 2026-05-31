"""Application entry point — polling mode with health check server.

Polling mode is more reliable on Render free tier than webhook mode.
Health check server runs on PORT so Render and UptimeRobot can ping /health.
"""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web
from redis.asyncio import Redis

from config import settings
from models.base import init_db
from middlewares.language import LanguageMiddleware
from middlewares.throttling import ThrottlingMiddleware
from middlewares.auth import AuthMiddleware
from services.scheduler import setup_scheduler

from handlers import start, language, menu, cart, order, payment, taxi, delivery
from handlers import profile, referral, bonus, promo, reviews, courier
from handlers.admin import (
    dashboard as admin_dashboard,
    products as admin_products,
    orders as admin_orders,
    users as admin_users,
    broadcast as admin_broadcast,
    promo as admin_promo,
    statistics as admin_statistics,
    settings as admin_settings,
    couriers as admin_couriers,
    reviews as admin_reviews,
)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=False,
        ssl_cert_reqs=None,
    )
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.update.middleware(ThrottlingMiddleware(rate_limit=1.0))
    dp.update.middleware(LanguageMiddleware())
    dp.update.middleware(AuthMiddleware())

    dp.include_router(start.router)
    dp.include_router(language.router)
    dp.include_router(menu.router)
    dp.include_router(cart.router)
    dp.include_router(order.router)
    dp.include_router(payment.router)
    dp.include_router(taxi.router)
    dp.include_router(delivery.router)
    dp.include_router(profile.router)
    dp.include_router(referral.router)
    dp.include_router(bonus.router)
    dp.include_router(promo.router)
    dp.include_router(reviews.router)
    dp.include_router(courier.router)

    dp.include_router(admin_dashboard.router)
    dp.include_router(admin_products.router)
    dp.include_router(admin_orders.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_broadcast.router)
    dp.include_router(admin_promo.router)
    dp.include_router(admin_statistics.router)
    dp.include_router(admin_settings.router)
    dp.include_router(admin_couriers.router)
    dp.include_router(admin_reviews.router)

    return dp


async def start_health_server(port: int) -> web.AppRunner:
    """Run a minimal aiohttp server so Render health check and UptimeRobot work."""
    app = web.Application()

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "ts": datetime.utcnow().isoformat()})

    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server started on port %s", port)
    return runner


async def main_async() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    # Delete any existing webhook so polling works cleanly
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted, switching to polling mode")
    except Exception as exc:
        logger.warning("delete_webhook failed: %s", exc)

    # Initialize DB
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as exc:
        logger.error("Database init failed: %s", exc)

    # Start health check server (keeps Render + UptimeRobot happy)
    runner = await start_health_server(settings.PORT)

    # Start APScheduler
    try:
        scheduler = setup_scheduler(bot)
        scheduler.start()
        logger.info("Scheduler started")
    except Exception as exc:
        logger.error("Scheduler start failed: %s", exc)

    logger.info("Starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await runner.cleanup()
        await bot.session.close()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
