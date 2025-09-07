from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging

from app.routers import auth
from app.config.setting import settings
from app.config.lifespan import lifespan
from app.config.error_handler import (
    app_exception_handler,
    http_exception_handler,
    general_exception_handler,
    validation_exception_handler  # Добавлен новый обработчик
)
from app.config.exceptions import BaseAppException
from app.config.middleware import rate_limit_middleware


logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Job Platform API",
    description="A comprehensive job platform with user management, job posting, and application tracking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Custom middleware for rate limiting
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# Request timing middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
    
    return response

# Exception handlers - ИСПРАВЛЕНО
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)  
app.add_exception_handler(HTTPException, http_exception_handler) 
app.add_exception_handler(Exception, general_exception_handler)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )