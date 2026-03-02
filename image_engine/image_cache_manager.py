"""
image_cache_manager.py
Enterprise-safe local caching system.
"""

from pathlib import Path
import hashlib
import logging

logger = logging.getLogger("ImageCacheManager")


class ImageCacheManager:

    def __init__(self, base_dir: str = "assets"):
        self.ai_cache = Path(base_dir) / "ai_cache"
        self.stock_cache = Path(base_dir) / "stock_cache"

        self.ai_cache.mkdir(parents=True, exist_ok=True)
        self.stock_cache.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get_cached_path(self, key: str, mode: str) -> Path | None:
        hashed = self._hash_key(key)
        directory = self.ai_cache if mode == "ai" else self.stock_cache
        file_path = directory / f"{hashed}.jpg"
        return file_path if file_path.exists() else None

    def store(self, key: str, mode: str, content: bytes) -> Path:
        hashed = self._hash_key(key)
        directory = self.ai_cache if mode == "ai" else self.stock_cache
        file_path = directory / f"{hashed}.jpg"

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Image cached: {file_path}")
        return file_path
