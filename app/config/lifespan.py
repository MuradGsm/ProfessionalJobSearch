import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.redis import redis_connection
from app.config.cache import CacheManager
from app.config.logging import setup_logging
from app.config.setting import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up application...")
    
    # Setup logging
    setup_logging(settings.LOG_LEVEL, settings.LOG_FILE)
    
    # Connect to Redis
    try:
        redis_client = await redis_connection.connect()
        
        # Initialize cache manager
        cache_manager = CacheManager(redis_client)
        app.state.cache = cache_manager
        
        logger.info("Successfully connected to Redis and initialized cache")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        # Continue without Redis (graceful degradation)
        app.state.cache = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Disconnect from Redis
    await redis_connection.disconnect()
    
    logger.info("Application shutdown complete")