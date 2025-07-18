"""
Schémas Pydantic pour les requêtes et réponses SQL
"""
from pydantic import BaseModel, Field
from typing import Optional, Any

class SQLQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="Natural language question")
    execute_query: bool = Field(False, description="Whether to execute the generated SQL")
    use_cache: bool = Field(True, description="Whether to use cache for results")

class SQLQueryResponse(BaseModel):
    sql: str
    execution_time: float
    cached: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None

class TablesResponse(BaseModel):
    tables: list
