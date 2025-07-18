"""
Routeur pour les endpoints SQL
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.sql import SQLQueryRequest, SQLQueryResponse, TablesResponse
from app.dependencies import rate_limit_check
from domain.sql.service import generate_sql_query_only
from infrastructure.cache import cache_manager
from infrastructure.logging import logger
import time

router = APIRouter(prefix="/sql", tags=["SQL"])

# Variables globales pour DB et LLM (initialisées dans main.py)
db = None
llm = None

def set_dependencies(database, language_model):
    """Fonction pour injecter les dépendances"""
    global db, llm
    db = database
    llm = language_model

@router.post("/generate", response_model=SQLQueryResponse)
async def generate_sql(
    request: SQLQueryRequest,
    req: Request,
    _: None = Depends(rate_limit_check)
):
    """Génère une requête SQL à partir d'une question en langage naturel"""
    start_time = time.time()
    
    try:
        logger.info("SQL generation request", 
                   question=request.question,
                   execute_query=request.execute_query,
                   client_ip=req.client.host)
        
        # Vérification du cache
        cached_result = None
        if request.use_cache:
            cached_result = cache_manager.get_cached_sql_result(request.question)
        
        if cached_result:
            logger.info("Cache hit for SQL generation")
            return SQLQueryResponse(
                sql=cached_result["sql"],
                execution_time=time.time() - start_time,
                cached=True,
                result=cached_result.get("result")
            )
        
        # Génération SQL
        sql = generate_sql_query_only(request.question, llm, db)
        
        if not sql:
            raise HTTPException(status_code=400, detail="Failed to generate SQL")
        
        response_data = {
            "sql": sql,
            "execution_time": time.time() - start_time,
            "cached": False
        }
        
        # Exécution optionnelle de la requête
        if request.execute_query:
            try:
                result = db.run(sql)
                response_data["result"] = result
                logger.info("SQL executed successfully", rows_returned=len(result) if result else 0)
            except Exception as e:
                logger.error("SQL execution failed", error=str(e), sql=sql)
                response_data["error"] = str(e)
        
        # Mise en cache
        if request.use_cache:
            cache_manager.cache_sql_result(request.question, response_data)
        
        return SQLQueryResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("SQL generation failed", error=str(e), question=request.question)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/tables", response_model=TablesResponse)
async def get_tables():
    """Retourne la liste des tables disponibles"""
    try:
        tables_info = db.get_table_info()
        return TablesResponse(tables=tables_info)
    except Exception as e:
        logger.error("Failed to get tables", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
