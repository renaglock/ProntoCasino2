"""QR code generation, texture rendering, and payload parsing utilities for customer pickup."""

import io
import json
from typing import Any, Dict, Optional
import qrcode
from kivy.core.image import Image as CoreImage


def generate_pickup_payload(order_id: str, customer_name: str) -> str:
    """Generate encoded JSON payload string to embed into QR code for order pickup."""
    payload: Dict[str, Any] = {
        "app": "PuntoCasino",
        "order_id": order_id,
        "customer": customer_name,
    }
    return json.dumps(payload, separators=(",", ":"))


def parse_pickup_payload(payload_str: str) -> Optional[Dict[str, Any]]:
    """Parse decoded QR payload string and extract order pickup data."""
    if not payload_str:
        return None
    try:
        data = json.loads(payload_str.strip())
        if isinstance(data, dict) and data.get("app") == "PuntoCasino" and "order_id" in data:
            return data
        return None
    except (json.JSONDecodeError, TypeError):
        # Fallback: Check if direct order ID was entered
        if payload_str.strip().startswith("PED-"):
            return {"app": "PuntoCasino", "order_id": payload_str.strip(), "customer": "Cliente"}
        return None


def generate_qr_texture(payload_str: str):
    """Generate an in-memory Kivy Texture from a QR payload string with UCT navy styling."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A3871", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    core_img = CoreImage(buf, ext="png")
    return core_img.texture
