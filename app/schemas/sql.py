"""
Schémas Pydantic pour les endpoints SQL
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List

class SQLQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="Question en langage naturel")
    execute_query: bool = Field(False, description="Exécuter la requête SQL générée")
    use_cache: bool = Field(True, description="Utiliser le cache pour les résultats")

class SQLQueryResponse(BaseModel):
    sql: str
    execution_time: float
    cached: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None

class TablesResponse(BaseModel):
    tables: str

class HealthResponse(BaseModel):
    status: str
    database: str
    llm: str
    cache_stats: dict
