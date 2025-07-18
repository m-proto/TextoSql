"""
API FastAPI production-ready avec rate limiting et validation
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import time
from collections import defaultdict
from core.settings import settings
from core.database import connect_to_redshift
from core.llm import init_llm
from core.sql_generator import generate_sql_query_only
from core.cache import cache_manager
from core.logging import logger
import asyncio

# Rate limiting simple (en production, utilisez Redis)
request_counts = defaultdict(list)

# Initialisation des composants globaux
db = None
llm = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application (startup et shutdown)"""
    global db, llm
    
    # STARTUP
    logger.info("Starting up TextToSQL API")
    
    try:
        # Connexion à la base
        db = connect_to_redshift()
        logger.info("Database connection established")
        
        # Initialisation du LLM
        llm = init_llm()
        logger.info("LLM initialized")
        
    except Exception as e:
        logger.error("Startup failed", error=str(e))
        raise
    
    # L'application est prête
    yield
    
    # SHUTDOWN
    logger.info("Shutting down TextToSQL API")
    
    # Fermeture des connexions
    from core.database import db_manager
    db_manager.close()
    logger.info("Cleanup completed")

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

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    database_connected: bool
    cache_connected: bool

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

# Initialisation de l'application avec lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready Text-to-SQL API with Redshift integration",
    lifespan=lifespan  # Nouvelle syntaxe pour startup/shutdown
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé pour le monitoring"""
    from core.database import db_manager
    
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        database_connected=db_manager.health_check(),
        cache_connected=True  # Cache mémoire toujours disponible
    )

@app.post("/sql/generate", response_model=SQLQueryResponse)
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

@app.get("/sql/tables")
async def get_tables():
    """Retourne la liste des tables disponibles"""
    try:
        tables_info = db.get_table_info()
        return {"tables": tables_info}
    except Exception as e:
        logger.error("Failed to get tables", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global des exceptions"""
    logger.error("Unhandled exception", 
                error=str(exc),
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
