"""Miscellaneous helper utilities."""

import math
import random
import string
from datetime import datetime


def generate_order_number(order_id: int) -> str:
    """Format order number as ORD-00123."""
    return f"ORD-{order_id:05d}"


def generate_referral_code(telegram_id: int) -> str:
    """Deterministic referral code based on user ID."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"REF{telegram_id}{suffix}"


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula — straight-line distance in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def delivery_cost_from_distance(distance_km: float) -> int | None:
    """Return delivery cost in kopecks or None if out of range."""
    if distance_km <= 3:
        return 150_00  # 150 ₽
    elif distance_km <= 7:
        return 250_00
    elif distance_km <= 15:
        return 400_00
    return None  # too far


def format_price(kopecks: int) -> str:
    """Format kopecks as '350 ₽'."""
    return f"{kopecks // 100} ₽"


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def stars(rating: int) -> str:
    return "⭐" * rating + "☆" * (5 - rating)
