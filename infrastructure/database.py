"""
Gestion robuste des connexions Redshift avec retry et pooling
"""
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy import inspect
from langchain_community.utilities import SQLDatabase
from tenacity import retry, stop_after_attempt, wait_exponential
from core.settings import settings
from core.logging import logger
import time

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.db = None
        self._connect()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _connect(self):
        """Connexion avec retry automatique"""
        try:
            logger.info("Connecting to Redshift", 
                       host=settings.redshift_host, 
                       database=settings.redshift_db,
                       schema=settings.redshift_schema)
            
            # Engine avec pooling robuste
            self.engine = create_engine(
                settings.redshift_dsn,
                poolclass=QueuePool,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_pool_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_pre_ping=True,  # Vérifie la connexion avant utilisation
                pool_recycle=3600,   # Renouvelle les connexions toutes les heures
                echo=settings.debug  # Log SQL en mode debug
            )
            
            # Test de connexion
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            # Introspection du schéma
            inspector = inspect(self.engine)
            tables = inspector.get_table_names(schema=settings.redshift_schema)
            
            logger.info("Database connection successful", 
                       tables_count=len(tables),
                       tables=tables[:5])  # Log les 5 premières tables
            
            # Création de l'objet SQLDatabase pour LangChain
            self.db = SQLDatabase(
                self.engine, 
                schema=settings.redshift_schema, 
                include_tables=tables
            )
            
        except Exception as e:
            logger.error("Database connection failed", 
                        error=str(e),
                        host=settings.redshift_host)
            raise
    
    def get_db(self) -> SQLDatabase:
        """Retourne l'instance SQLDatabase"""
        if self.db is None:
            self._connect()
        return self.db
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    def close(self):
        """Ferme proprement les connexions"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Instance globale
db_manager = DatabaseManager()

def connect_to_redshift() -> SQLDatabase:
    """Interface publique pour la connexion Redshift"""
    return db_manager.get_db()
