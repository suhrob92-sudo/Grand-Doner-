"""Product model with bilingual fields and badges."""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(200), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description_uz: Mapped[str] = mapped_column(Text, nullable=False, default="")
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Telegram file_id
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # in kopecks (₽ * 100)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hot: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product", lazy="select")

    @property
    def price_rub(self) -> float:
        """Price in rubles."""
        return self.price / 100

    def get_name(self, lang: str) -> str:
        return self.name_uz if lang == "uz" else self.name_ru

    def get_description(self, lang: str) -> str:
        return self.description_uz if lang == "uz" else self.description_ru

    def get_badges(self) -> str:
        badges = ""
        if self.is_new:
            badges += "🆕 "
        if self.is_hot:
            badges += "🔥 "
        return badges.strip()
