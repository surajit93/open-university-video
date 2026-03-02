"""
ai_generator.py
AI-based image generation using OpenAI Images API.
Production ready with timeout & error handling.
"""

import logging
import requests
import os

logger = logging.getLogger("AIGenerator")


class AIGenerator:

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

    def generate(self, prompt: str) -> bytes:
        endpoint = "https://api.openai.com/v1/images/generations"

        payload = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": "1024x1024"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            logger.error(f"AI generation failed: {response.text}")
            raise RuntimeError("AI image generation failed")

        data = response.json()
        image_base64 = data["data"][0]["b64_json"]

        import base64
        return base64.b64decode(image_base64)
