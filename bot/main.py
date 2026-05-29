"""Application entry point — sets up bot, dispatcher, webhook and scheduler."""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
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


async def on_startup(bot: Bot) -> None:
    """Register webhook and initialize DB on startup."""
    await init_db()
    webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    logger.info("Webhook set to %s", webhook_url)


async def on_shutdown(bot: Bot) -> None:
    """Delete webhook on shutdown."""
    await bot.delete_webhook()
    logger.info("Webhook deleted")


def create_dispatcher() -> Dispatcher:
    """Build and configure the Dispatcher with all middlewares and routers."""
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    # Middlewares (order matters)
    dp.update.middleware(ThrottlingMiddleware(rate_limit=1.0))
    dp.update.middleware(LanguageMiddleware())
    dp.update.middleware(AuthMiddleware())

    # Routers
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

    # Admin routers
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

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    return dp


def main() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    # Start APScheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()

    # Build aiohttp app for webhook
    app = web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # YooKassa webhook route handled separately
    from handlers.payment import yookassa_webhook
    app.router.add_post("/webhook/yookassa", yookassa_webhook)

    web.run_app(app, host="0.0.0.0", port=settings.WEBHOOK_PORT)


if __name__ == "__main__":
    main()
