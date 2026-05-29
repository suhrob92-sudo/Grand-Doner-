"""Referral tracking model."""

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)  # telegram_id
    referred_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)  # telegram_id
    bonus_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    bonus_amount: Mapped[int] = mapped_column(Integer, default=150)  # points
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
