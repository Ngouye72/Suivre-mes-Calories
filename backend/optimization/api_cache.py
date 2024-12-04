from functools import wraps
from flask import request, make_response, current_app
import hashlib
import time
from typing import Callable, Optional, Any
from .cache_manager import CacheManager

class ApiCache:
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.default_ttl = 300  # 5 minutes par défaut
        
    def _generate_cache_key(self, prefix: str) -> str:
        """Génère une clé de cache unique pour la requête"""
        # Combine les éléments de la requête
        key_parts = [
            prefix,
            request.path,
            request.method,
            str(sorted(request.args.items())),
            str(sorted(request.form.items())),
            request.headers.get('Authorization', '')
        ]
        
        # Crée un hash unique
        key_str = ':'.join(key_parts)
        return f"api:{hashlib.md5(key_str.encode()).hexdigest()}"
        
    def cached_response(self, ttl: Optional[int] = None, 
                       key_prefix: str = '',
                       unless: Optional[Callable] = None):
        """Décorateur pour mettre en cache les réponses API"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Vérifie si on doit ignorer le cache
                if unless and unless():
                    return f(*args, **kwargs)
                
                cache_key = self._generate_cache_key(key_prefix)
                cached_response = self.cache.get(cache_key)
                
                if cached_response is not None:
                    response = make_response(cached_response)
                    response.headers['X-Cache'] = 'HIT'
                    return response
                
                # Exécute la fonction et met en cache
                response = f(*args, **kwargs)
                response_data = response.get_json()
                
                if response.status_code == 200:
                    self.cache.set(
                        cache_key,
                        response_data,
                        ttl or self.default_ttl
                    )
                
                response.headers['X-Cache'] = 'MISS'
                return response
                
            return decorated_function
        return decorator
        
    def invalidate_pattern(self, pattern: str):
        """Invalide toutes les clés correspondant à un pattern"""
        return self.cache.clear_pattern(f"api:{pattern}")

# Exemple d'utilisation:
"""
from flask import Flask, jsonify
from optimization.api_cache import ApiCache
from optimization.cache_manager import CacheManager

app = Flask(__name__)
cache_manager = CacheManager(redis_url="redis://localhost:6379/0")
api_cache = ApiCache(cache_manager)

@app.route('/api/meals/<int:user_id>')
@api_cache.cached_response(ttl=300, key_prefix='meals')
def get_user_meals(user_id):
    # Logique pour récupérer les repas
    meals = meal_service.get_user_meals(user_id)
    return jsonify(meals)

@app.route('/api/meals', methods=['POST'])
def create_meal():
    # Après création d'un repas, invalide le cache
    user_id = request.json.get('user_id')
    result = meal_service.create_meal(request.json)
    api_cache.invalidate_pattern(f'meals:{user_id}')
    return jsonify(result)
"""
