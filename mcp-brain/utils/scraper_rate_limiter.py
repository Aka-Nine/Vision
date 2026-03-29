import asyncio
import random
import time
import logging

class ScraperRateLimiter:
    def __init__(self, base_delay: float = 2.0, max_jitter: float = 3.0):
        self.base_delay = base_delay
        self.max_jitter = max_jitter
        self.last_request_time = 0.0

    async def wait(self):
        now = time.time()
        elapsed = now - self.last_request_time
        jitter = random.uniform(0, self.max_jitter)
        delay = max(0, self.base_delay + jitter - elapsed)
        if delay > 0:
            logging.info(f"RateLimiter: Sleeping for {delay:.2f}s")
            await asyncio.sleep(delay)
        self.last_request_time = time.time()

    def get_user_agent(self) -> str:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
        ]
        return random.choice(user_agents)

rate_limiter = ScraperRateLimiter()
