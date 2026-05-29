"""Order model with status tracking and delivery info."""

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # ORD-00123

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    courier_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Pricing
    subtotal: Mapped[int] = mapped_column(Integer, default=0)       # sum of items in kopecks
    delivery_cost: Mapped[int] = mapped_column(Integer, default=0)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)
    bonus_used: Mapped[int] = mapped_column(Integer, default=0)     # bonus points used
    total: Mapped[int] = mapped_column(Integer, default=0)          # final amount in kopecks

    # Order type: pickup | taxi | delivery
    order_type: Mapped[str] = mapped_column(String(20), nullable=False, default="pickup")

    # Delivery info
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_lat: Mapped[float | None] = mapped_column(nullable=True)
    delivery_lon: Mapped[float | None] = mapped_column(nullable=True)
    delivery_distance_km: Mapped[float | None] = mapped_column(nullable=True)

    # Pickup info
    pickup_time: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Taxi info
    yandex_taxi_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    taxi_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Payment
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)   # YooKassa payment ID
    payment_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Promo
    promo_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status: pending → paid → preparing → ready/on_the_way → completed → cancelled
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)

    # Bonus accrued after completion
    bonus_accrued: Mapped[int] = mapped_column(Integer, default=0)

    # Review
    review_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="orders")
    courier: Mapped["User | None"] = relationship("User", foreign_keys=[courier_id])
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", lazy="select")
    review: Mapped["Review | None"] = relationship("Review", back_populates="order", uselist=False)

    @property
    def total_rub(self) -> float:
        return self.total / 100
