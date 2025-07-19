"""
Routeur pour les endpoints de santé
"""
from fastapi import APIRouter
from app.schemas.health import HealthResponse
from infrastructure.monitoring import get_system_health, metrics
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

@router.get("/metrics")
async def get_metrics():
    """Endpoint pour les métriques détaillées"""
    return metrics.get_metrics()

@router.get("/health/detailed")
async def detailed_health_check():
    """Endpoint de santé détaillé avec métriques système"""
    from infrastructure.database import db_manager
    
    system_health = get_system_health()
    app_metrics = metrics.get_metrics()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database_connected": db_manager.health_check(),
        "cache_connected": True,
        "system_health": system_health,
        "metrics": app_metrics
    }
