"""
Gemini Vision Engine with Structured JSON Output, 2D Bounding Boxes,
Low Thinking Latency, and Automatic 503/429 Model Fallback.
"""
import json
import time
from typing import Literal
from pydantic import BaseModel, Field
from google import genai  # type: ignore
from google.genai import types # type: ignore
from google.genai.errors import APIError # type: ignore

from ecolens_mini_project.config import API_KEY, MODEL_NAME


class WasteItem(BaseModel):
    item: str
    category: Literal["Refuse", "Reduce", "Reuse", "Recycle", "Rot"]
    box_2d: list[int] = Field(
        description="Normalized 2D bounding box [ymin, xmin, ymax, xmax] scaled 0 to 1000"
    )
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
        self.client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(
                api_version="v1beta",
                timeout=20000,  # 20s per request so it never hangs indefinitely
            ),
        )
        self.fallback_models = list(
            dict.fromkeys([MODEL_NAME, "gemini-3.5-flash-lite", "gemini-2.5-flash"])
        )

    def analyze_image_bytes(self, image_bytes: bytes, city: str = "Delhi") -> list[dict]:
        """Sends JPEG bytes to Gemini with low thinking level and fast fallback."""
        prompt = f"""
        You are EcoLens, an expert waste management AI.
        Analyze this image and identify EVERY visible waste or recyclable item.

        Rules:
        - category must be exactly one of: Refuse, Reduce, Reuse, Recycle, Rot
        - box_2d: tight bounding box [ymin, xmin, ymax, xmax] normalized to 0..1000 integers
        - reuse_ideas: 3 practical, creative upcycling or reuse suggestions
        - where_to_dispose: 3 real facility or bin types
        - local_tip: 1 specific actionable disposal tip tailored for {city}
        - List EVERY visible item separately. If no waste is visible, return an empty list [].
        """

        last_err = None
        for model_id in self.fallback_models:
            for attempt in range(2):
                try:
                    print(f"  [AI] Calling {model_id} (attempt {attempt + 1})...")
                    response = self.client.models.generate_content(
                        model=model_id,
                        contents=[
                            prompt,
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        ],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=list[WasteItem],
                            temperature=0.2,
                            thinking_config=types.ThinkingConfig(thinking_level="low"),
                        ),
                    )
                    print(f"  [AI] Success from {model_id}")
                    return json.loads(response.text)
                except APIError as exc:
                    last_err = exc
                    print(f"  [AI] {model_id} APIError {exc.code}: {exc.message}")
                    if exc.code in (429, 503):
                        time.sleep(0.5)
                        continue
                    raise
                except Exception as exc:
                    last_err = exc
                    print(f"  [AI] {model_id} error: {exc}")
                    time.sleep(0.5)
                    continue

        raise RuntimeError(f"Gemini request failed across models: {last_err}")