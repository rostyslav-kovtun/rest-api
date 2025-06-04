import time
from typing import Optional
from fastapi import Request, HTTPException, status
from redis_client import redis_client
from config import settings

class RateLimiter:
    def __init__(self, redis_client_instance=None):
        self.redis_client_instance = redis_client_instance or redis_client
    
    async def check_rate_limit(self, request: Request, user_id: Optional[str] = None):
        if hasattr(self.redis_client_instance, 'get_client'):
            r = self.redis_client_instance.get_client()
        else:
            r = self.redis_client_instance

        identity = user_id or request.client.host
        
        limit_type = "authenticated" if user_id else "anonymous"
        limit, period = settings.RATE_LIMITS[limit_type]

        key = f"rate_limit_{identity}_{limit_type}"

        now = int(time.time())
        window_start = now - period
        
        try:
            await r.zremrangebyscore(key, min=0, max=window_start)

            request_count = await r.zcard(key)
            
            if request_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {limit} requests per minute for {limit_type} users.",
                    headers={"Retry-After": str(period)}
                )

            await r.zadd(key, {str(now): now})

            await r.expire(key, period)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Rate limiter error: {e}")

rate_limiter = RateLimiter()