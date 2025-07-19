"""
Point d'entrée principal de l'API TextToSQL
Architecture propre avec FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from infrastructure.settings import settings
from infrastructure.database import connect_to_redshift
from infrastructure.llm import init_llm
from infrastructure.logging import logger

from app.routers import sql, health

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
        
        # Injection des dépendances dans les routers
        sql.set_dependencies(db, llm)
        
    except Exception as e:
        logger.error("Startup failed", error=str(e))
        raise
    
    # L'application est prête
    yield
    
    # SHUTDOWN
    logger.info("Shutting down TextToSQL API")
    
    # Fermeture des connexions
    from infrastructure.database import db_manager
    db_manager.close()
    logger.info("Cleanup completed")

# Initialisation de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready Text-to-SQL API with Redshift integration",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(health.router)
app.include_router(sql.router)

# Gestionnaire global des exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Gestionnaire global des exceptions"""
    logger.error("Unhandled exception", 
                error=str(exc),
                path=request.url.path,
                method=request.method)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


