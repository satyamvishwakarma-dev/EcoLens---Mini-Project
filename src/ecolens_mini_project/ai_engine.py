"""
Gemini 2.5 Flash Vision Engine with Structured JSON Output.
Guarantees valid JSON responses without fragile markdown string stripping.
"""
import json
from typing import Literal
from pydantic import BaseModel
from google import genai
from google.genai import types

from ecolens_mini_project.config import API_KEY, MODEL_NAME


# Pydantic schema enforced directly by Gemini API
class WasteItem(BaseModel):
    item: str
    category: Literal["Refuse", "Reduce", "Reuse", "Recycle", "Rot"]
    reason: str
    reuse_ideas: list[str]
    where_to_dispose: list[str]
    local_tip: str


class EcoLensAI:
    def __init__(self):
        if not API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing! Add it to your .env file in the project root."
            )
        self.client = genai.Client(api_key=API_KEY)

    def analyze_image_bytes(self, image_bytes: bytes, city: str = "Delhi") -> list[dict]:
        """Sends JPEG bytes to Gemini 2.5 Flash and returns a validated list of waste items."""
        prompt = f"""
        You are EcoLens, an expert waste management AI.
        Analyze this image and identify EVERY visible waste or recyclable item.

        Rules:
        - category must be exactly one of: Refuse, Reduce, Reuse, Recycle, Rot
        - reuse_ideas: 3 practical, creative upcycling or reuse suggestions
        - where_to_dispose: 3 real facility or bin types
        - local_tip: 1 specific actionable disposal tip tailored for {city}
        - List EVERY visible item separately. If no waste is visible, return an empty list [].
        """

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[WasteItem],
                temperature=0.2,
            ),
        )

        return json.loads(response.text)