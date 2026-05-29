"""Import all models so that Base.metadata knows about every table."""

from models.base import Base, engine, AsyncSessionLocal, init_db
from models.user import User
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.referral import Referral
from models.promo import PromoCode, PromoUsage
from models.review import Review
from models.bonus import BonusTransaction
from models.settings import BotSetting

__all__ = [
    "Base", "engine", "AsyncSessionLocal", "init_db",
    "User", "Category", "Product", "Order", "OrderItem",
    "Referral", "PromoCode", "PromoUsage", "Review",
    "BonusTransaction", "BotSetting",
]
