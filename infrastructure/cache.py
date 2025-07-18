"""
Cache manager pour optimiser les performances (Version mémoire gratuite)
"""
import json
import hashlib
import time
from typing import Optional, Any, Dict
from infrastructure.settings import settings
from infrastructure.logging import logger

class CacheManager:
    def __init__(self):
        # Cache mémoire gratuit au lieu de Redis
        self.memory_cache: Dict[str, Dict] = {}
        logger.info("In-memory cache initialized (FREE)")
    
    def _is_expired(self, cache_item: Dict) -> bool:
        """Vérifie si l'item de cache a expiré"""
        return time.time() > cache_item.get("expires_at", 0)
    
    def _generate_key(self, prefix: str, data: str) -> str:
        """Génère une clé de cache basée sur le hash du contenu"""
        hash_object = hashlib.md5(data.encode())
        return f"{prefix}:{hash_object.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Stocke une valeur dans le cache"""
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or settings.cache_ttl
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    def cache_sql_result(self, query: str, result: Any) -> bool:
        """Cache le résultat d'une requête SQL"""
        key = self._generate_key("sql", query)
        return self.set(key, result)
    
    def get_cached_sql_result(self, query: str) -> Optional[Any]:
        """Récupère le résultat d'une requête SQL du cache"""
        key = self._generate_key("sql", query)
        return self.get(key)

# Instance globale
cache_manager = CacheManager()
