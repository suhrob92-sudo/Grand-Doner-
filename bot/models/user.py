"""User model — stores Telegram user data, language, bonuses and referral info."""

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="ru", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_courier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Bonus system
    bonus_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # in kopecks

    # Referral
    referral_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    referral_bonus_received: Mapped[bool] = mapped_column(Boolean, default=False)

    # Birthday promo
    birthdate: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    birthday_promo_sent_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Notifications
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", foreign_keys="[Order.user_id]", back_populates="user", lazy="select")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user", lazy="select")
    bonus_transactions: Mapped[list["BonusTransaction"]] = relationship("BonusTransaction", back_populates="user", lazy="select")
