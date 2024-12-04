from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, joinedload, contains_eager
import logging
from typing import List, Set, Dict, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.slow_query_threshold = 1.0  # secondes
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(self, conn, cursor, statement, 
                            parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(self, conn, cursor, statement,
                           parameters, context, executemany):
        total_time = time.time() - conn.info['query_start_time'].pop()
        
        # Log les requêtes lentes
        if total_time > self.slow_query_threshold:
            logger.warning(f"Requête lente détectée ({total_time:.2f}s): {statement}")
            
        # Collecte des statistiques
        query_hash = hash(statement)
        if query_hash in self.query_stats:
            stats = self.query_stats[query_hash]
            stats['count'] += 1
            stats['total_time'] += total_time
            stats['avg_time'] = stats['total_time'] / stats['count']
        else:
            self.query_stats[query_hash] = {
                'query': statement,
                'count': 1,
                'total_time': total_time,
                'avg_time': total_time
            }

def optimize_query(query: Query, model: Any) -> Query:
    """Optimise une requête SQLAlchemy"""
    # Analyse les relations du modèle
    relationships = get_model_relationships(model)
    
    # Applique les optimisations appropriées
    for relation in relationships:
        if is_collection(relation):
            query = query.options(joinedload(relation))
        else:
            query = query.options(contains_eager(relation))
    
    return query

def get_model_relationships(model: Any) -> List[str]:
    """Récupère les relations d'un modèle"""
    return [r.key for r in model.__mapper__.relationships]

def is_collection(relationship: str) -> bool:
    """Vérifie si une relation est une collection"""
    return relationship.property.uselist

def analyze_query_performance(func):
    """Décorateur pour analyser les performances des requêtes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log la performance
        logger.info(f"Exécution de {func.__name__}: {duration:.2f}s")
        
        return result
    return wrapper

class QueryCache:
    """Cache de requêtes pour éviter les requêtes répétées"""
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.ttl: Dict[str, float] = {}
        
    def get(self, key: str) -> Any:
        """Récupère un résultat du cache"""
        if key in self.cache and time.time() < self.ttl[key]:
            return self.cache[key]
        return None
        
    def set(self, key: str, value: Any, ttl: int = 300):
        """Stocke un résultat dans le cache"""
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
        
    def invalidate(self, key: str):
        """Invalide une entrée du cache"""
        if key in self.cache:
            del self.cache[key]
            del self.ttl[key]

# Exemple d'utilisation:
"""
class MealRepository:
    def __init__(self):
        self.query_cache = QueryCache()
    
    @analyze_query_performance
    def get_user_meals(self, user_id: int) -> List[Dict]:
        cache_key = f"user_meals:{user_id}"
        
        # Vérifie le cache
        cached_result = self.query_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Construit et optimise la requête
        query = db.session.query(Meal).filter_by(user_id=user_id)
        query = optimize_query(query, Meal)
        
        # Exécute et met en cache
        result = query.all()
        self.query_cache.set(cache_key, result)
        
        return result
"""
