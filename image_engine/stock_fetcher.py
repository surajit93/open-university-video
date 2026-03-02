"""
stock_fetcher.py
Hybrid stock image fetcher (Pexels example).
"""

import requests
import os
import logging

logger = logging.getLogger("StockFetcher")


class StockFetcher:

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY not configured")

    def fetch(self, query: str) -> bytes:

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.api_key}
        params = {"query": query, "per_page": 1}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            logger.error(response.text)
            raise RuntimeError("Stock fetch failed")

        data = response.json()

        if not data["photos"]:
            raise RuntimeError("No stock images found")

        image_url = data["photos"][0]["src"]["large"]

        img_response = requests.get(image_url, timeout=30)
        return img_response.content
