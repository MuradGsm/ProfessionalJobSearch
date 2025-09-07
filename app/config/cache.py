import json
from typing import Any, Optional
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

class CacheManager:  
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f'Cache get error: {e}')
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.error(f'Cache set error: {e}')

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f'Cache delete error: {e}')