"""APScheduler setup — runs daily/weekly background jobs."""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from sqlalchemy import select, and_, func, update

logger = logging.getLogger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        expire_bonus_points,
        trigger=CronTrigger(hour=3, minute=0),
        args=[bot],
        id="expire_bonus",
        replace_existing=True,
    )
    scheduler.add_job(
        send_birthday_promos,
        trigger=CronTrigger(hour=9, minute=0),
        args=[bot],
        id="birthday_promos",
        replace_existing=True,
    )
    scheduler.add_job(
        send_reengagement_push,
        trigger=CronTrigger(day_of_week="mon", hour=12, minute=0),
        args=[bot],
        id="reengagement",
        replace_existing=True,
    )

    return scheduler


async def expire_bonus_points(bot: Bot) -> None:
    """Deduct expired bonus points from user balances (runs daily at 03:00)."""
    from models.base import AsyncSessionLocal
    from models.bonus import BonusTransaction
    from models.user import User
    from config import settings

    cutoff = datetime.utcnow() - timedelta(days=settings.BONUS_EXPIRE_DAYS)
    try:
        async with AsyncSessionLocal() as session:
            # Find transactions that have expired and haven't been negated yet
            result = await session.execute(
                select(BonusTransaction).where(
                    and_(
                        BonusTransaction.expires_at <= datetime.utcnow(),
                        BonusTransaction.amount > 0,
                        BonusTransaction.reason == "order_accrual",
                    )
                )
            )
            expired = result.scalars().all()
            for txn in expired:
                # Check if already negated
                neg_result = await session.execute(
                    select(BonusTransaction).where(
                        and_(
                            BonusTransaction.user_id == txn.user_id,
                            BonusTransaction.reason == "expiry",
                            BonusTransaction.order_id == txn.order_id,
                        )
                    )
                )
                if neg_result.scalar_one_or_none():
                    continue
                # Deduct from user balance
                user_result = await session.execute(
                    select(User).where(User.id == txn.user_id)
                )
                user = user_result.scalar_one_or_none()
                if user and user.bonus_points >= txn.amount:
                    user.bonus_points -= txn.amount
                    session.add(BonusTransaction(
                        user_id=txn.user_id,
                        amount=-txn.amount,
                        reason="expiry",
                        order_id=txn.order_id,
                    ))
                    logger.info("Expired %s bonus points for user %s", txn.amount, txn.user_id)
            await session.commit()
    except Exception as exc:
        logger.exception("expire_bonus_points error: %s", exc)


async def send_birthday_promos(bot: Bot) -> None:
    """Send birthday promo codes 7 days before birthday and on the day (runs daily at 09:00)."""
    from models.base import AsyncSessionLocal
    from models.user import User
    from models.promo import PromoCode
    from utils.helpers import generate_referral_code

    now = datetime.utcnow()
    current_year = now.year
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(
                    and_(User.birthdate.isnot(None), User.is_active == True, User.notifications_enabled == True)
                )
            )
            users = result.scalars().all()
            for user in users:
                if not user.birthdate:
                    continue
                bday_this_year = user.birthdate.replace(year=current_year)
                days_until = (bday_this_year.date() - now.date()).days

                if days_until == 7:
                    # 7-day advance notification
                    from utils.i18n import _
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            _("notif_birthday_soon", user.language),
                        )
                    except Exception:
                        pass

                elif days_until == 0 and user.birthday_promo_sent_year != current_year:
                    # On birthday — generate promo code
                    promo_code_str = f"BDAY{user.telegram_id}{current_year}"
                    promo = PromoCode(
                        code=promo_code_str,
                        discount_type="percent",
                        discount_value=20,
                        max_uses_per_user=1,
                        max_uses=1,
                        valid_from=now,
                        valid_to=now + timedelta(days=3),
                        is_birthday=True,
                        is_active=True,
                    )
                    session.add(promo)
                    user.birthday_promo_sent_year = current_year
                    from utils.i18n import _
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            _("notif_birthday", user.language, name=user.full_name, code=promo_code_str),
                        )
                    except Exception:
                        pass
            await session.commit()
    except Exception as exc:
        logger.exception("send_birthday_promos error: %s", exc)


async def send_reengagement_push(bot: Bot) -> None:
    """Send re-engagement push to users who haven't ordered in 14 days (runs weekly on Monday)."""
    from models.base import AsyncSessionLocal
    from models.user import User
    from models.order import Order
    from utils.i18n import _

    cutoff = datetime.utcnow() - timedelta(days=14)
    try:
        async with AsyncSessionLocal() as session:
            # Users who have at least one order but none in the last 14 days
            subq = (
                select(Order.user_id)
                .where(Order.created_at >= cutoff)
                .distinct()
                .scalar_subquery()
            )
            result = await session.execute(
                select(User).where(
                    and_(
                        User.is_active == True,
                        User.notifications_enabled == True,
                        User.is_banned == False,
                        User.id.not_in(subq),
                    )
                ).join(Order, Order.user_id == User.id).distinct()
            )
            users = result.scalars().all()
            for user in users:
                try:
                    await bot.send_message(
                        user.telegram_id,
                        _("notif_reengagement", user.language),
                    )
                except Exception:
                    pass
            logger.info("Re-engagement push sent to %s users", len(users))
    except Exception as exc:
        logger.exception("send_reengagement_push error: %s", exc)
