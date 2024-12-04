import redis
import json
import pickle
from datetime import datetime, timedelta
import logging
import hashlib
from functools import wraps
import os

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        self.default_ttl = int(os.getenv('CACHE_DEFAULT_TTL', 3600))  # 1 heure par défaut

    def get(self, key):
        """Récupère une valeur du cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du cache: {str(e)}")
            return None

    def set(self, key, value, ttl=None):
        """Stocke une valeur dans le cache"""
        try:
            serialized_value = json.dumps(value)
            self.redis_client.set(
                key,
                serialized_value,
                ex=ttl or self.default_ttl
            )
            return True
        except Exception as e:
            logger.error(f"Erreur lors du stockage dans le cache: {str(e)}")
            return False

    def delete(self, key):
        """Supprime une valeur du cache"""
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {str(e)}")
            return False

    def clear_pattern(self, pattern):
        """Supprime toutes les clés correspondant à un pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys) > 0
            return False
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du cache: {str(e)}")
            return False

    def get_or_set(self, key, callback, ttl=None):
        """Récupère une valeur du cache ou l'initialise si absente"""
        try:
            value = self.get(key)
            if value is None:
                value = callback()
                self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Erreur lors de get_or_set: {str(e)}")
            return callback()

    def mget(self, keys):
        """Récupère plusieurs valeurs du cache"""
        try:
            values = self.redis_client.mget(keys)
            return [json.loads(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Erreur lors de mget: {str(e)}")
            return [None] * len(keys)

    def mset(self, mapping, ttl=None):
        """Stocke plusieurs valeurs dans le cache"""
        try:
            serialized_mapping = {
                k: json.dumps(v) for k, v in mapping.items()
            }
            pipeline = self.redis_client.pipeline()
            pipeline.mset(serialized_mapping)
            if ttl:
                for key in mapping.keys():
                    pipeline.expire(key, ttl)
            pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de mset: {str(e)}")
            return False

    def increment(self, key, amount=1):
        """Incrémente une valeur numérique"""
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Erreur lors de l'incrémentation: {str(e)}")
            return None

    def expire_at(self, key, timestamp):
        """Définit une expiration à un timestamp spécifique"""
        try:
            return self.redis_client.expireat(key, int(timestamp.timestamp()))
        except Exception as e:
            logger.error(f"Erreur lors de la définition de l'expiration: {str(e)}")
            return False

    def generate_key(self, prefix, *args, **kwargs):
        """Génère une clé de cache unique"""
        key_parts = [prefix]
        
        # Ajout des arguments positionnels
        key_parts.extend(str(arg) for arg in args)
        
        # Ajout des arguments nommés, triés par nom
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        
        # Génération du hash
        key = ":".join(key_parts)
        if len(key) > 200:  # Si la clé est trop longue, on la hashe
            key = f"{prefix}:hash:{hashlib.md5(key.encode()).hexdigest()}"
            
        return key

def cached(prefix, ttl=None):
    """Décorateur pour mettre en cache le résultat d'une fonction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            
            # Génération de la clé de cache
            cache_key = cache_manager.generate_key(
                prefix,
                *args,
                **kwargs
            )
            
            # Tentative de récupération depuis le cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Exécution de la fonction et mise en cache
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

class CacheInvalidator:
    """Gestionnaire d'invalidation du cache"""
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalide le cache lié à un utilisateur"""
        cache_manager = CacheManager()
        patterns = [
            f"user:{user_id}:*",
            f"profile:{user_id}:*",
            f"meals:{user_id}:*",
            f"analysis:{user_id}:*"
        ]
        for pattern in patterns:
            cache_manager.clear_pattern(pattern)

    @staticmethod
    def invalidate_meal_cache(user_id, meal_id=None):
        """Invalide le cache lié aux repas"""
        cache_manager = CacheManager()
        patterns = [
            f"meals:{user_id}:*",
            f"analysis:{user_id}:*"
        ]
        if meal_id:
            patterns.append(f"meal:{meal_id}:*")
        for pattern in patterns:
            cache_manager.clear_pattern(pattern)

    @staticmethod
    def invalidate_analysis_cache(user_id, analysis_type=None):
        """Invalide le cache lié aux analyses"""
        cache_manager = CacheManager()
        if analysis_type:
            cache_manager.clear_pattern(f"analysis:{user_id}:{analysis_type}:*")
        else:
            cache_manager.clear_pattern(f"analysis:{user_id}:*")
