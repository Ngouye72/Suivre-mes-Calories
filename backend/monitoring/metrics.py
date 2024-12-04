from prometheus_client import Counter, Histogram, Gauge, Summary
from functools import wraps
import time

class MetricsManager:
    def __init__(self):
        # Métriques HTTP
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total des requêtes HTTP',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'Durée des requêtes HTTP',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )

        # Métriques Business
        self.meals_logged = Counter(
            'meals_logged_total',
            'Nombre total de repas enregistrés',
            ['meal_type']
        )

        self.calories_per_meal = Histogram(
            'calories_per_meal',
            'Distribution des calories par repas',
            ['meal_type'],
            buckets=[100, 300, 500, 800, 1200, 1500]
        )

        self.active_users = Gauge(
            'active_users',
            'Nombre d\'utilisateurs actifs'
        )

        self.weight_changes = Summary(
            'weight_changes_kg',
            'Changements de poids des utilisateurs',
            ['direction']
        )

        # Métriques Performance
        self.db_connection_pool = Gauge(
            'db_connection_pool_size',
            'Taille du pool de connexions DB'
        )

        self.cache_hits = Counter(
            'cache_hits_total',
            'Nombre total de hits du cache'
        )

        self.cache_misses = Counter(
            'cache_misses_total',
            'Nombre total de misses du cache'
        )

    def track_request(self, method, endpoint):
        """Décorateur pour tracker les requêtes HTTP"""
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                start_time = time.time()
                try:
                    response = f(*args, **kwargs)
                    status = response.status_code
                    self.http_requests_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status=status
                    ).inc()
                    return response
                except Exception as e:
                    self.http_requests_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status=500
                    ).inc()
                    raise e
                finally:
                    duration = time.time() - start_time
                    self.http_request_duration.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(duration)
            return wrapped
        return decorator

    def track_meal(self, meal_type, calories):
        """Enregistre les métriques d'un repas"""
        self.meals_logged.labels(meal_type=meal_type).inc()
        self.calories_per_meal.labels(meal_type=meal_type).observe(calories)

    def track_weight_change(self, change_kg):
        """Enregistre un changement de poids"""
        direction = 'gain' if change_kg > 0 else 'loss'
        self.weight_changes.labels(direction=direction).observe(abs(change_kg))

    def update_active_users(self, count):
        """Met à jour le nombre d'utilisateurs actifs"""
        self.active_users.set(count)

    def track_cache_operation(self, hit):
        """Enregistre une opération de cache"""
        if hit:
            self.cache_hits.inc()
        else:
            self.cache_misses.inc()

    def set_db_pool_size(self, size):
        """Met à jour la taille du pool de connexions"""
        self.db_connection_pool.set(size)

# Instance globale du gestionnaire de métriques
metrics = MetricsManager()

# Exemple d'utilisation
@metrics.track_request('GET', '/api/meals')
def get_meals():
    # Logique de l'endpoint
    pass
