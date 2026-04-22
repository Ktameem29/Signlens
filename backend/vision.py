import os
import base64
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

def _pil_to_b64(pil_image: Image.Image) -> str:
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG", quality=85)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")

def describe_sign(pil_image: Image.Image) -> str | None:
    """Use Claude vision to identify and describe the sign in the image."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        b64 = _pil_to_b64(pil_image)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a street sign or road sign image. "
                            "Identify exactly what the sign says or means in plain English. "
                            "If it is a text sign, return the exact text. "
                            "If it is a symbol sign (e.g. pedestrian crossing, no entry, speed limit), "
                            "describe it in 2-5 words (e.g. 'Pedestrian Crossing', 'No Entry', 'Speed Limit 50'). "
                            "Reply with ONLY the sign text or description, nothing else."
                        )
                    }
                ]
            }]
        )
        result = msg.content[0].text.strip()
        return result if result else None
    except Exception as e:
        logger.warning(f"Vision API failed: {e}")
        return None
