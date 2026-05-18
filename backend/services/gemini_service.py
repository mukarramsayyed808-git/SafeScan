import httpx
import json
import base64
from config import settings

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
)

def _build_url():
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    )

async def analyze_ingredients(
    image_bytes: bytes,
    mime_type: str,
    ocr_text: str,
    user_profile: dict,
) -> dict:
    """
    Sends the label image + OCR text + user profile to Gemini 1.5 Flash.
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
            "maxOutputTokens": 4096,
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(_build_url(), json=payload)
        resp.raise_for_status()
        data = resp.json()

    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    # Strip accidental markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())