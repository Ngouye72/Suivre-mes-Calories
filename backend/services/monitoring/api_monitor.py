from functools import wraps
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from prometheus_client import Counter, Histogram, Gauge, Summary
import json

logger = logging.getLogger(__name__)

# Métriques Prometheus
API_REQUEST_COUNT = Counter('api_request_total', 'Total des requêtes API', ['method', 'endpoint', 'status'])
API_LATENCY = Histogram('api_latency_seconds', 'Latence API', ['method', 'endpoint'])
API_ERROR_COUNT = Counter('api_error_total', 'Total des erreurs API', ['method', 'endpoint', 'error_type'])
API_ACTIVE_USERS = Gauge('api_active_users', 'Utilisateurs actifs')
API_RESPONSE_SIZE = Summary('api_response_bytes', 'Taille des réponses API', ['endpoint'])

class APIMonitor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.request_history = deque(maxlen=10000)
        self.error_history = deque(maxlen=1000)
        self.active_sessions = set()
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'errors': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0
        })
        
        self._initialized = True

    def monitor_endpoint(self, endpoint_name):
        """Décorateur pour monitorer un endpoint"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    status = 'success'
                    return result
                except Exception as e:
                    status = 'error'
                    self._record_error(endpoint_name, str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    self._record_request(endpoint_name, duration, status)
                    
                    # Mise à jour des métriques Prometheus
                    API_REQUEST_COUNT.labels(
                        method=func.__name__,
                        endpoint=endpoint_name,
                        status=status
                    ).inc()
                    
                    API_LATENCY.labels(
                        method=func.__name__,
                        endpoint=endpoint_name
                    ).observe(duration)
                    
            return wrapper
        return decorator

    def _record_request(self, endpoint, duration, status):
        """Enregistre une requête"""
        timestamp = datetime.now()
        
        self.request_history.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'duration': duration,
            'status': status
        })
        
        # Mise à jour des statistiques de l'endpoint
        stats = self.endpoint_stats[endpoint]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        
        if status == 'error':
            stats['errors'] += 1

    def _record_error(self, endpoint, error):
        """Enregistre une erreur"""
        timestamp = datetime.now()
        
        self.error_history.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'error': str(error)
        })
        
        # Mise à jour des métriques Prometheus
        API_ERROR_COUNT.labels(
            method='unknown',
            endpoint=endpoint,
            error_type=type(error).__name__
        ).inc()

    def track_session(self, session_id):
        """Suit une session active"""
        self.active_sessions.add(session_id)
        API_ACTIVE_USERS.set(len(self.active_sessions))

    def end_session(self, session_id):
        """Termine une session"""
        self.active_sessions.discard(session_id)
        API_ACTIVE_USERS.set(len(self.active_sessions))

    def get_endpoint_stats(self, endpoint=None):
        """Retourne les statistiques des endpoints"""
        if endpoint:
            stats = self.endpoint_stats[endpoint]
            return {
                'endpoint': endpoint,
                'requests': stats['count'],
                'errors': stats['errors'],
                'avg_time': stats['total_time'] / stats['count'] if stats['count'] > 0 else 0,
                'min_time': stats['min_time'] if stats['min_time'] != float('inf') else 0,
                'max_time': stats['max_time'],
                'error_rate': (stats['errors'] / stats['count'] * 100) if stats['count'] > 0 else 0
            }
        
        return {
            endpoint: self.get_endpoint_stats(endpoint)
            for endpoint in self.endpoint_stats
        }

    def get_recent_errors(self, minutes=None):
        """Retourne les erreurs récentes"""
        if minutes is None:
            return list(self.error_history)
            
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [
            error for error in self.error_history
            if error['timestamp'] >= cutoff
        ]

    def get_traffic_analysis(self, hours=24):
        """Analyse le trafic sur une période"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Agrégation par heure
        hourly_stats = defaultdict(lambda: defaultdict(int))
        
        for request in self.request_history:
            if request['timestamp'] >= cutoff:
                hour = request['timestamp'].replace(minute=0, second=0, microsecond=0)
                hourly_stats[hour][request['endpoint']] += 1
        
        return dict(hourly_stats)

    def get_performance_report(self):
        """Génère un rapport de performance"""
        stats = self.get_endpoint_stats()
        errors = self.get_recent_errors(minutes=60)
        traffic = self.get_traffic_analysis(hours=24)
        
        return {
            'timestamp': datetime.now(),
            'active_users': len(self.active_sessions),
            'endpoint_stats': stats,
            'recent_errors': errors,
            'traffic_analysis': traffic,
            'summary': {
                'total_requests': sum(s['count'] for s in self.endpoint_stats.values()),
                'total_errors': sum(s['errors'] for s in self.endpoint_stats.values()),
                'avg_response_time': sum(s['total_time'] for s in self.endpoint_stats.values()) / 
                                   sum(s['count'] for s in self.endpoint_stats.values() if s['count'] > 0)
            }
        }

    def export_report(self, file_path):
        """Exporte le rapport de performance"""
        report = self.get_performance_report()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, default=str)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export du rapport: {str(e)}")
            return False
