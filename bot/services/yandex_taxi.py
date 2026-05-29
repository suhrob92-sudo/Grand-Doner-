"""Yandex Taxi Business API integration (Taximeter / B2B)."""

import logging
import aiohttp
from config import settings

logger = logging.getLogger(__name__)

TAXI_API_BASE = "https://fleet-api.taxi.yandex.net/v1"


async def create_taxi_order(
    from_lat: float,
    from_lon: float,
    from_address: str,
    user_phone: str,
) -> dict:
    """
    Request a taxi from user location to the restaurant.
    The restaurant is the destination (to_address).
    Returns driver info and ETA on success, raises on failure.
    """
    headers = {
        "Authorization": f"Bearer {settings.YANDEX_TAXI_API_KEY}",
        "X-Client-ID": settings.YANDEX_TAXI_CLIENT_ID,
        "Content-Type": "application/json",
    }
    payload = {
        "park_id": settings.YANDEX_TAXI_PARK_ID,
        "source": {
            "type": "Point",
            "coordinates": [from_lon, from_lat],
            "full_address": from_address,
        },
        "destinations": [
            {
                "type": "Point",
                "coordinates": [settings.RESTAURANT_LON, settings.RESTAURANT_LAT],
                "full_address": settings.RESTAURANT_ADDRESS,
            }
        ],
        "client_phone": user_phone,
        "class": "econom",
        "comment": "Заказ из Shaurma House бота",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TAXI_API_BASE}/orders",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status not in (200, 201):
                    text = await resp.text()
                    logger.error("Yandex Taxi API error %s: %s", resp.status, text)
                    raise RuntimeError(f"Taxi API returned {resp.status}")
                data = await resp.json()
                return {
                    "order_id": data.get("id", ""),
                    "driver_name": data.get("performer", {}).get("first_name", "Водитель"),
                    "car_model": data.get("performer", {}).get("car_model", ""),
                    "car_color": data.get("performer", {}).get("car_color", ""),
                    "car_plate": data.get("performer", {}).get("license_plate", ""),
                    "eta_minutes": data.get("eta", 5),
                    "status": data.get("status", "searching"),
                }
    except aiohttp.ClientError as exc:
        logger.exception("Yandex Taxi network error: %s", exc)
        raise


async def get_order_status(order_id: str) -> str:
    """Poll the status of an existing Yandex Taxi order."""
    headers = {
        "Authorization": f"Bearer {settings.YANDEX_TAXI_API_KEY}",
        "X-Client-ID": settings.YANDEX_TAXI_CLIENT_ID,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{TAXI_API_BASE}/orders/{order_id}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return "unknown"
                data = await resp.json()
                return data.get("status", "unknown")
    except Exception as exc:
        logger.warning("get_order_status error: %s", exc)
        return "unknown"


async def cancel_order(order_id: str) -> bool:
    """Cancel a pending Yandex Taxi order."""
    headers = {
        "Authorization": f"Bearer {settings.YANDEX_TAXI_API_KEY}",
        "X-Client-ID": settings.YANDEX_TAXI_CLIENT_ID,
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{TAXI_API_BASE}/orders/{order_id}/cancel",
                headers=headers,
                json={},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return resp.status in (200, 204)
    except Exception as exc:
        logger.warning("cancel_order error: %s", exc)
        return False


# Status mapping from Yandex to user-friendly strings
TAXI_STATUS_MAP = {
    "searching": "🔍 Ищем водителя...",
    "driving": "🚗 Водитель едет к вам",
    "waiting": "📍 Водитель прибыл!",
    "transporting": "🏎 Везём вас в ресторан",
    "complete": "✅ Поездка завершена",
    "cancelled": "❌ Такси отменено",
    "failed": "❌ Такси не найдено",
    "unknown": "⏳ Уточняем статус...",
}
