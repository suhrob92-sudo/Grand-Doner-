"""QR code generation for paid orders using qrcode + Pillow."""

import io
import json
import logging
from datetime import datetime

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def generate_order_qr(
    order_id: int,
    order_number: str,
    restaurant_name: str,
    items: list[dict],
    total_kopecks: int,
    delivery_type: str,
    customer_phone: str,
) -> io.BytesIO:
    """
    Generate a QR code image containing order JSON.
    Returns a BytesIO PNG buffer ready to send via Telegram.
    """
    payload = {
        "order_id": order_id,
        "order_number": order_number,
        "restaurant": restaurant_name,
        "items": items,
        "total": total_kopecks // 100,
        "delivery_type": delivery_type,
        "paid": True,
        "timestamp": datetime.utcnow().isoformat(),
        "customer_phone": customer_phone,
    }
    payload_str = json.dumps(payload, ensure_ascii=False)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)

    qr_img: Image.Image = qr.make_image(fill_color="black", back_color="white").convert("RGB")  # type: ignore

    # Add a small caption below the QR
    caption_height = 60
    final_img = Image.new("RGB", (qr_img.width, qr_img.height + caption_height), "white")
    final_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final_img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    text = f"Заказ {order_number}  •  {total_kopecks // 100} ₽"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    draw.text(
        ((final_img.width - text_w) / 2, qr_img.height + 10),
        text,
        fill="black",
        font=font,
    )

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    return buf
