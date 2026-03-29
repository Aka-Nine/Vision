import json
import os
import time
from typing import Any, Optional

class Cache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
            
        try:
            with open(path, "r") as f:
                data = json.load(f)
                
            if time.time() - data.get("timestamp", 0) > ttl_seconds:
                return None
                
            return data.get("value")
        except Exception:
            return None

    def set(self, key: str, value: Any):
        path = self._get_path(key)
        with open(path, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "value": value
            }, f, indent=4)

    def clear(self):
        """Remove all cached files."""
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".json"):
                os.remove(filepath)

cache = Cache()
