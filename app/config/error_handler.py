from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config.exceptions import BaseAppException
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: BaseAppException):
    logger.error(f'Application error: {exc.message}')
    return JSONResponse(
        status_code=400, content={
            'error': exc.__class__.__name__,
            'message': exc.message,
            'error_code': exc.error_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    
    
    errors = []
    for error in exc.errors():
        error_dict = {
            'type': error.get('type'),
            'loc': error.get('loc'),
            'msg': error.get('msg'),
            'input': str(error.get('input')) if error.get('input') is not None else None
        }
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422,  
        content={
            'error': 'ValidationError',
            'message': 'Request validation failed',
            'details': errors  
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f'HTTP error: {exc.status_code} - {exc.detail}')
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later."
        }
    )