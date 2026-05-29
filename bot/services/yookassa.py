"""YooKassa payment service — create invoices and process webhooks."""

import logging
import uuid
from typing import Optional

from yookassa import Configuration, Payment
from yookassa.domain.models import Currency
from config import settings

logger = logging.getLogger(__name__)

# Configure SDK once at import time
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


async def create_payment(
    amount_kopecks: int,
    order_number: str,
    description: str,
    return_url: str,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None,
) -> dict:
    """Create a YooKassa payment and return {payment_id, confirmation_url}."""
    try:
        idempotence_key = str(uuid.uuid4())
        amount_rub = str(amount_kopecks / 100)

        payment_data = {
            "amount": {"value": f"{float(amount_rub):.2f}", "currency": Currency.RUB},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": description,
            "metadata": {"order_number": order_number},
            "capture": True,
        }

        if customer_email or customer_phone:
            receipt: dict = {"customer": {}}
            if customer_email:
                receipt["customer"]["email"] = customer_email
            if customer_phone:
                receipt["customer"]["phone"] = customer_phone
            receipt["items"] = [
                {
                    "description": description,
                    "quantity": "1",
                    "amount": {"value": f"{float(amount_rub):.2f}", "currency": Currency.RUB},
                    "vat_code": 1,
                }
            ]
            payment_data["receipt"] = receipt

        payment = Payment.create(payment_data, idempotence_key)
        return {
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
            "status": payment.status,
        }
    except Exception as exc:
        logger.exception("YooKassa create_payment error: %s", exc)
        raise


async def cancel_payment(payment_id: str) -> bool:
    """Cancel (refund) a payment by its YooKassa ID."""
    try:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.find_one(payment_id)
        if payment.status == "succeeded":
            # Issue refund
            from yookassa import Refund
            Refund.create(
                {
                    "payment_id": payment_id,
                    "amount": payment.amount,
                },
                idempotence_key,
            )
            return True
        elif payment.status == "pending":
            Payment.cancel(payment_id, idempotence_key)
            return True
        return False
    except Exception as exc:
        logger.exception("YooKassa cancel_payment error: %s", exc)
        return False


def parse_webhook_event(data: dict) -> dict:
    """Extract relevant fields from a YooKassa webhook payload."""
    event = data.get("event", "")
    payment_obj = data.get("object", {})
    return {
        "event": event,
        "payment_id": payment_obj.get("id"),
        "status": payment_obj.get("status"),
        "order_number": payment_obj.get("metadata", {}).get("order_number"),
        "amount": payment_obj.get("amount", {}).get("value"),
    }
