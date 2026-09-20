"""QR code generation, texture rendering, and payload parsing utilities for customer pickup."""

import io
import json
from typing import Any, Dict, Optional
import qrcode


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
    """Generate a crisp, high-resolution in-memory Kivy Texture from a QR payload string with UCT navy styling."""
    from kivy.core.image import Image as CoreImage

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=3,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A3871", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    core_img = CoreImage(buf, ext="png")
    return core_img.texture


def decode_qr_image(image_input: Any) -> Optional[str]:
    """Decode QR payload from an image file path, numpy ndarray, PIL Image, or bytes using OpenCV."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None

    try:
        img_bgr = None
        if isinstance(image_input, str):
            img_bgr = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            img_bgr = image_input
        elif isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif hasattr(image_input, "convert"):  # PIL Image
            rgb = np.array(image_input.convert("RGB"))
            img_bgr = rgb[:, :, ::-1].copy()

        if img_bgr is None:
            return None

        detector = cv2.QRCodeDetector()
        val, _, _ = detector.detectAndDecode(img_bgr)
        if val and val.strip():
            return val.strip()

        # Fallback: try grayscale thresholding for lower contrast lighting
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        val, _, _ = detector.detectAndDecode(gray)
        if val and val.strip():
            return val.strip()

        return None
    except Exception:
        return None


def scan_qr_from_frame(frame) -> Optional[Dict[str, Any]]:
    """Detect and parse QR comanda from a live video capture frame."""
    decoded_str = decode_qr_image(frame)
    if decoded_str:
        return parse_pickup_payload(decoded_str)
    return None
