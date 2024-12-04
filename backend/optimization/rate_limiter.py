from flask import request, current_app
from functools import wraps
import time
from typing import Dict, Tuple, Optional, Callable
import redis
from dataclasses import dataclass

@dataclass
class RateLimit:
    requests: int  # Nombre de requêtes autorisées
    window: int   # Période en secondes
    by: str       # Critère de limitation ('ip', 'user', 'token')

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limit = RateLimit(100, 3600, 'ip')  # 100 requêtes/heure par IP
        
    def _get_identifier(self, by: str) -> str:
        """Récupère l'identifiant pour la limitation"""
        if by == 'ip':
            return request.remote_addr
        elif by == 'user':
            return str(getattr(request, 'user_id', 'anonymous'))
        elif by == 'token':
            auth_header = request.headers.get('Authorization', '')
            return auth_header.replace('Bearer ', '')
        return 'default'
        
    def _get_rate_limit_data(self, key: str) -> Tuple[int, int]:
        """Récupère les données de limitation pour une clé"""
        pipe = self.redis.pipeline()
        
        # Incrémente le compteur
        pipe.incr(key)
        # Récupère le TTL
        pipe.ttl(key)
        
        result = pipe.execute()
        return result[0], result[1]
        
    def limit(self, 
              requests: Optional[int] = None,
              window: Optional[int] = None,
              by: Optional[str] = None,
              exempt_when: Optional[Callable] = None):
        """Décorateur pour limiter les requêtes"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Vérifie si on doit ignorer la limitation
                if exempt_when and exempt_when():
                    return f(*args, **kwargs)
                
                # Utilise les paramètres fournis ou par défaut
                limit = RateLimit(
                    requests or self.default_limit.requests,
                    window or self.default_limit.window,
                    by or self.default_limit.by
                )
                
                # Génère la clé Redis
                identifier = self._get_identifier(limit.by)
                key = f"rate_limit:{limit.by}:{identifier}"
                
                # Vérifie et met à jour la limitation
                count, ttl = self._get_rate_limit_data(key)
                
                # Si c'est la première requête, initialise le TTL
                if ttl == -1:
                    self.redis.expire(key, limit.window)
                    ttl = limit.window
                
                # Ajoute les headers de limitation
                response = make_response(f(*args, **kwargs))
                response.headers.update({
                    'X-RateLimit-Limit': str(limit.requests),
                    'X-RateLimit-Remaining': str(max(0, limit.requests - count)),
                    'X-RateLimit-Reset': str(int(time.time() + ttl))
                })
                
                # Vérifie si la limite est dépassée
                if count > limit.requests:
                    response = make_response({
                        'error': 'Rate limit exceeded',
                        'retry_after': ttl
                    }, 429)
                    response.headers['Retry-After'] = str(ttl)
                    return response
                
                return response
                
            return decorated_function
        return decorator

# Exemple d'utilisation:
"""
from flask import Flask
from optimization.rate_limiter import RateLimiter
import redis

app = Flask(__name__)
redis_client = redis.from_url("redis://localhost:6379/0")
limiter = RateLimiter(redis_client)

# Limite globale par IP
@app.route('/api/public')
@limiter.limit(requests=100, window=3600, by='ip')
def public_endpoint():
    return {'message': 'Public API'}

# Limite par utilisateur
@app.route('/api/user')
@limiter.limit(requests=1000, window=3600, by='user')
def user_endpoint():
    return {'message': 'User API'}

# Limite par token avec exemption
def is_admin():
    return getattr(request, 'is_admin', False)

@app.route('/api/admin')
@limiter.limit(requests=50, window=60, by='token', exempt_when=is_admin)
def admin_endpoint():
    return {'message': 'Admin API'}
"""
