from redis.asyncio import Redis
import logging
from app.config.setting import settings

logger = logging.getLogger(__name__)

class RedisConnection:
    def __init__(self):
        self.redis: Redis = None

    async def connect(self) -> Redis:
        """Connect to Redis"""
        try:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
            return self.redis
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def get_client(self) -> Redis:
        """Get Redis client"""
        if not self.redis:
            return await self.connect()
        return self.redis

redis_connection = RedisConnection()