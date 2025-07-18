"""
Dépendances FastAPI pour rate limiting et middleware
"""
from fastapi import HTTPException, Request
import time
from collections import defaultdict
from infrastructure.settings import settings

# Rate limiting simple en mémoire (gratuit)
request_counts = defaultdict(list)

def rate_limit_check(request: Request):
    """Simple rate limiting middleware"""
    client_ip = request.client.host
    now = time.time()
    
    # Nettoie les anciens requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if now - req_time < settings.rate_limit_window
    ]
    
    # Vérifie la limite
    if len(request_counts[client_ip]) >= settings.rate_limit_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {settings.rate_limit_requests} requests per {settings.rate_limit_window} seconds"
        )
    
    # Ajoute le request actuel
    request_counts[client_ip].append(now)
