import redis.asyncio as redis
from config import settings
from typing import Optional

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        print("Підключено до Redis")
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            print("Відключено від Redis")
    
    def get_client(self) -> redis.Redis:
        if not self.redis:
            raise RuntimeError("Redis не підключений")
        return self.redis

redis_client = RedisClient()