"""Input validation helpers."""

import re
from datetime import datetime


def is_valid_phone(phone: str) -> bool:
    """Accept Russian mobile numbers in various formats."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(r"^(\+7|7|8)\d{10}$", cleaned))


def normalize_phone(phone: str) -> str:
    """Normalize phone to +7XXXXXXXXXX format."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if cleaned.startswith("8"):
        cleaned = "+7" + cleaned[1:]
    elif cleaned.startswith("7"):
        cleaned = "+" + cleaned
    return cleaned


def is_valid_price(value: str) -> bool:
    """Check that a price string is a positive number."""
    try:
        p = float(value.replace(",", "."))
        return p > 0
    except ValueError:
        return False


def parse_price_to_kopecks(value: str) -> int:
    """Convert 'XX.YY' rubles string to integer kopecks."""
    return int(float(value.replace(",", ".")) * 100)


def is_valid_date(value: str, fmt: str = "%d.%m.%Y") -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False


def parse_date(value: str, fmt: str = "%d.%m.%Y") -> datetime:
    return datetime.strptime(value, fmt)


def is_valid_time(value: str) -> bool:
    """Validate HH:MM format."""
    return bool(re.match(r"^\d{1,2}:\d{2}$", value.strip()))
