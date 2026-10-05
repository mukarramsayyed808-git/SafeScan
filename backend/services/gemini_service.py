import httpx
import json
import base64
import asyncio
import random
from config import settings


MAX_ATTEMPTS = 4
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class GeminiServiceError(Exception):
    """An expected Gemini integration failure that is safe to return to clients."""

    def __init__(self, detail: str, status_code: int = 502):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _build_url():
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )


def _retry_delay(attempt: int, retry_after: str | None) -> float:
    """Use Gemini's retry hint when available, otherwise exponential backoff + jitter."""
    try:
        if retry_after:
            return min(float(retry_after), 30.0)
    except ValueError:
        pass
    return min(2 ** attempt, 12.0) + random.uniform(0.0, 0.25)

async def analyze_ingredients(
    image_bytes: bytes,
    mime_type: str,
    ocr_text: str,
    user_profile: dict,
) -> dict:
    """
    Sends the label image + OCR text + user profile to Gemini.
    Returns structured JSON with per-ingredient safety, health score, and alternatives.
    """
    allergies   = user_profile.get("allergies", [])
    diet        = user_profile.get("dietary_preferences", [])
    conditions  = user_profile.get("medical_conditions", [])
    avoid       = user_profile.get("custom_avoid_list", [])

    prompt = f"""You are a product safety and nutrition expert. Analyse the ingredient label from the image below.

User health profile:
- Allergies: {', '.join(allergies) if allergies else 'None'}
- Dietary preferences: {', '.join(diet) if diet else 'None'}
- Medical conditions: {', '.join(conditions) if conditions else 'None'}
- Custom ingredients to avoid: {', '.join(avoid) if avoid else 'None'}

Also use this OCR-extracted text as a fallback if the image is unclear:
\"\"\"{ocr_text}\"\"\"

Return ONLY a valid JSON object (no markdown fences, no preamble) with this exact structure:
{{
  "overall_verdict": "safe" | "caution" | "unsafe",
  "health_score": <integer 0-100>,
  "ingredients": [
    {{
      "name": "<ingredient name>",
      "safety_level": "safe" | "caution" | "unsafe",
      "explanation": "<plain English, max 2 sentences>",
      "triggers_user_allergy": true | false,
      "triggered_allergy_name": "<allergy name or null>",
      "is_natural": true | false,
      "side_effects": "<brief note or null>"
    }}
  ],
  "triggered_allergies": ["<list of triggered allergy names>"],
  "main_concerns": ["<array of short concern strings>"],
  "alternatives": [
    {{
      "name": "<product name>",
      "brand": "<brand>",
      "why_better": "<specific reason related to user profile>",
      "calories": "<per serving>",
      "protein": "<g>",
      "fat": "<g>",
      "carbs": "<g>",
      "sugar": "<g>",
      "sodium": "<mg>",
      "fiber": "<g>",
      "benefits": "<2 sentence health benefit>",
      "price_range": "<e.g. ₹80-120>",
      "where_to_buy": "<e.g. Amazon, BigBasket, local health stores>"
    }}
  ]
}}

Provide 3-5 alternatives only if the product is not fully safe. If it is safe, return an empty alternatives array.
"""

    if not settings.GEMINI_API_KEY:
        raise GeminiServiceError("Gemini is not configured on this server.", 503)

    img_b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": img_b64}},
            ]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json",
        }
    }

    timeout = httpx.Timeout(connect=10.0, read=90.0, write=30.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(MAX_ATTEMPTS):
            try:
                resp = await client.post(
                    _build_url(),
                    json=payload,
                    headers={"X-goog-api-key": settings.GEMINI_API_KEY},
                )
            except httpx.TransportError:
                if attempt == MAX_ATTEMPTS - 1:
                    raise GeminiServiceError(
                        "Could not connect to Gemini after several attempts. Please try again shortly.",
                        503,
                    )
                await asyncio.sleep(_retry_delay(attempt, None))
                continue

            if resp.status_code in RETRYABLE_STATUS_CODES:
                if attempt == MAX_ATTEMPTS - 1:
                    raise GeminiServiceError(
                        "Gemini is temporarily unavailable after several attempts. Please try again shortly.",
                        503,
                    )
                await asyncio.sleep(_retry_delay(attempt, resp.headers.get("Retry-After")))
                continue

            if resp.is_error:
                raise GeminiServiceError(
                    f"Gemini rejected the request (HTTP {resp.status_code}). Check the API key and model configuration.",
                    502,
                )

            data = resp.json()
            break

    try:
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiServiceError("Gemini returned an incomplete analysis response.", 502) from exc
    # Strip accidental markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError as exc:
        raise GeminiServiceError("Gemini returned an invalid analysis response.", 502) from exc
