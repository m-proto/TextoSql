"""
Schémas Pydantic pour les endpoints de santé
"""
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    database_connected: bool
    cache_connected: bool
