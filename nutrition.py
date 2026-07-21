import base64
import json
from anthropic import AsyncAnthropic
from config import ANTHROPIC_API_KEY
from PIL import Image
import io

client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You estimate nutrition for a food-logging bot.
You will primarily be given a photo of food, sometimes with extra text context.
Respond with ONLY a JSON object, no markdown, no extra text, in this exact shape:
{"description": "short food description", "calories": 000, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
Use reasonable average portion sizes when not specified. Always give your best estimate, never refuse."""


async def estimate_nutrition(image_bytes: bytes, media_type: str, context: str = None) -> dict:
    detected_format = Image.open(io.BytesIO(image_bytes)).format
    format_to_mime = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
        "GIF": "image/gif",
    }
    media_type = format_to_mime.get(detected_format, media_type)

    b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")

    user_text = "Estimate the nutrition for the food in this photo."
    if context:
        user_text += f" Additional context: {context}"

    content = [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64_image}
        },
        {"type": "text", "text": user_text}
    ]

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
        timeout=30.0
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    cleaned = text.strip().strip("`")
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]

    return json.loads(cleaned)