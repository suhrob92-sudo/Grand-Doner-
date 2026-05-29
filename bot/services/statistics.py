"""Statistics aggregation queries used by admin panel."""

import logging
from datetime import datetime, timedelta
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from models.bonus import BonusTransaction

logger = logging.getLogger(__name__)


async def get_revenue_and_orders(
    session: AsyncSession,
    start: datetime,
    end: datetime,
) -> dict:
    """Return revenue (kopecks) and order counts for a date range."""
    result = await session.execute(
        select(
            func.count(Order.id).label("total"),
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.count(Order.id).filter(Order.status == "completed").label("completed"),
            func.count(Order.id).filter(Order.status == "cancelled").label("cancelled"),
            func.count(Order.id).filter(Order.order_type == "delivery").label("delivery"),
            func.count(Order.id).filter(Order.order_type == "pickup").label("pickup"),
            func.count(Order.id).filter(Order.order_type == "taxi").label("taxi"),
        ).where(and_(Order.created_at >= start, Order.created_at <= end, Order.is_paid == True))
    )
    row = result.one()
    avg = int(row.revenue / row.total) if row.total else 0
    return {
        "orders": row.total,
        "revenue": row.revenue,
        "completed": row.completed,
        "cancelled": row.cancelled,
        "avg_order": avg,
        "delivery_count": row.delivery,
        "pickup_count": row.pickup,
        "taxi_count": row.taxi,
    }


async def get_top_products(session: AsyncSession, limit: int = 10) -> list[dict]:
    """Top products by total quantity sold."""
    result = await session.execute(
        select(
            OrderItem.name_snapshot,
            func.sum(OrderItem.quantity).label("qty"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status == "completed")
        .group_by(OrderItem.name_snapshot)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
    )
    return [{"name": row.name_snapshot, "qty": row.qty} for row in result]


async def get_top_customers(session: AsyncSession, limit: int = 10) -> list[dict]:
    """Top customers by total amount spent."""
    result = await session.execute(
        select(User.full_name, User.total_spent)
        .order_by(User.total_spent.desc())
        .limit(limit)
    )
    return [{"name": row.full_name, "spent": row.total_spent} for row in result]


async def get_dashboard_stats(session: AsyncSession) -> dict:
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    today = await get_revenue_and_orders(session, today_start, datetime.utcnow())
    week = await get_revenue_and_orders(session, week_start, datetime.utcnow())

    total_users = (await session.execute(select(func.count(User.id)))).scalar_one()
    new_today = (await session.execute(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )).scalar_one()
    active_orders = (await session.execute(
        select(func.count(Order.id)).where(Order.status.in_(["paid", "preparing", "on_the_way"]))
    )).scalar_one()

    bonus_issued = (await session.execute(
        select(func.coalesce(func.sum(BonusTransaction.amount), 0))
        .where(BonusTransaction.amount > 0)
    )).scalar_one()
    bonus_used = abs((await session.execute(
        select(func.coalesce(func.sum(BonusTransaction.amount), 0))
        .where(BonusTransaction.amount < 0)
    )).scalar_one())

    return {
        "orders_today": today["orders"],
        "revenue_today": today["revenue"] // 100,
        "revenue_week": week["revenue"] // 100,
        "total_users": total_users,
        "new_today": new_today,
        "active_orders": active_orders,
        "bonus_issued": bonus_issued,
        "bonus_used": bonus_used,
    }
