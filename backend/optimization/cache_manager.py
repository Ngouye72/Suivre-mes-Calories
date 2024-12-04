import redis
from functools import wraps
import json
import hashlib
import logging
from typing import Any, Optional, Union, Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 heure par défaut
        
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Génère une clé de cache unique"""
        key_parts = [prefix]
        
        # Ajoute les arguments positionnels
        if args:
            key_parts.extend([str(arg) for arg in args])
            
        # Ajoute les arguments nommés, triés pour la cohérence
        if kwargs:
            sorted_items = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_items])
            
        # Crée un hash de la clé complète
        key_str = ":".join(key_parts)
        return f"nutrition:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans le cache"""
        try:
            ttl = ttl or self.default_ttl
            return self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans le cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une valeur du cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Supprime toutes les clés correspondant à un pattern"""
        try:
            keys = self.redis.keys(f"nutrition:{pattern}*")
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache: {e}")
            return 0

def cache_result(prefix: str, ttl: Optional[int] = None):
    """Décorateur pour mettre en cache le résultat d'une fonction"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Récupère l'instance du CacheManager
            cache_manager = getattr(self, 'cache_manager', None)
            if not cache_manager:
                return func(self, *args, **kwargs)
            
            # Génère la clé de cache
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Tente de récupérer depuis le cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Exécute la fonction et met en cache
            result = func(self, *args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
            
        return wrapper
    return decorator

# Exemple d'utilisation:
"""
class MealService:
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    @cache_result('meal', ttl=1800)
    def get_meal(self, meal_id: int) -> dict:
        # Logique pour récupérer un repas
        return {'id': meal_id, 'name': 'Example Meal'}
    
    @cache_result('user_meals', ttl=3600)
    def get_user_meals(self, user_id: int) -> list:
        # Logique pour récupérer les repas d'un utilisateur
        return [{'id': 1, 'name': 'Meal 1'}, {'id': 2, 'name': 'Meal 2'}]
"""
