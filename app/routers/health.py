"""
Routeur pour les endpoints de santé
"""
from fastapi import APIRouter
from app.schemas.health import HealthResponse
import time

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé pour le monitoring"""
    from infrastructure.database import db_manager
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        database_connected=db_manager.health_check(),
        cache_connected=True  # Cache mémoire toujours disponible
    )
