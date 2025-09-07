from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict

request_counts: Dict[str, list] = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] if current_time - req_time < 60
    ]

    if len(request_counts[client_ip]) >= 60:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={'detail': "Too many requests"}
        )
    
    request_counts[client_ip].append(current_time)

    response = await call_next(request)
    return response