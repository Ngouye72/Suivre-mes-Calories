from functools import wraps
import time
import cProfile
import pstats
import io
import logging
import psutil
import os
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge
import tracemalloc
from threading import Lock

logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter('request_total', 'Total des requêtes', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latence des requêtes', ['method', 'endpoint'])
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Utilisation mémoire')
CPU_USAGE = Gauge('cpu_usage_percent', 'Utilisation CPU')
DB_QUERY_COUNT = Counter('db_query_total', 'Total des requêtes DB', ['query_type'])
CACHE_HIT = Counter('cache_hit_total', 'Total des hits cache')
CACHE_MISS = Counter('cache_miss_total', 'Total des miss cache')

class PerformanceMonitor:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.process = psutil.Process(os.getpid())
        self.start_time = datetime.now()
        self.profiler = None
        self._initialized = True
        
        # Activation du tracking mémoire
        tracemalloc.start()

    def start_profiling(self):
        """Démarre le profilage"""
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    def stop_profiling(self):
        """Arrête le profilage et retourne les statistiques"""
        self.profiler.disable()
        s = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        stats.print_stats()
        return s.getvalue()

    def get_memory_usage(self):
        """Retourne l'utilisation mémoire actuelle"""
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current': current / 10**6,  # MB
            'peak': peak / 10**6,        # MB
            'system': self.process.memory_info().rss / 10**6  # MB
        }

    def get_cpu_usage(self):
        """Retourne l'utilisation CPU"""
        return self.process.cpu_percent()

    def get_system_stats(self):
        """Retourne les statistiques système"""
        return {
            'cpu_usage': self.get_cpu_usage(),
            'memory_usage': self.get_memory_usage(),
            'uptime': (datetime.now() - self.start_time).total_seconds()
        }

def profile_function(func):
    """Décorateur pour profiler une fonction"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        monitor.start_profiling()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            profile_stats = monitor.stop_profiling()
            
            logger.info(
                f"Performance profile for {func.__name__}:\n"
                f"Duration: {duration:.2f}s\n"
                f"Profile stats:\n{profile_stats}"
            )
    return wrapper

def monitor_endpoint(endpoint_name):
    """Décorateur pour monitorer un endpoint"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            REQUEST_COUNT.labels(
                method=func.__name__,
                endpoint=endpoint_name
            ).inc()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(
                    method=func.__name__,
                    endpoint=endpoint_name
                ).observe(duration)
                
                # Mise à jour des métriques système
                monitor = PerformanceMonitor()
                MEMORY_USAGE.set(monitor.get_memory_usage()['current'])
                CPU_USAGE.set(monitor.get_cpu_usage())
        return wrapper
    return decorator

def monitor_db_query(query_type):
    """Décorateur pour monitorer les requêtes DB"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            DB_QUERY_COUNT.labels(
                query_type=query_type
            ).inc()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger.debug(
                    f"DB Query {query_type} completed in {duration:.2f}s"
                )
        return wrapper
    return decorator

def monitor_cache(func):
    """Décorateur pour monitorer le cache"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        
        if result is not None:
            CACHE_HIT.inc()
        else:
            CACHE_MISS.inc()
            
        duration = time.time() - start_time
        logger.debug(
            f"Cache operation completed in {duration:.2f}s"
        )
        
        return result
    return wrapper

class QueryProfiler:
    """Profileur de requêtes SQL"""
    
    def __init__(self):
        self.queries = []
        self.total_time = 0
        
    def record_query(self, query, duration):
        """Enregistre une requête"""
        self.queries.append({
            'query': str(query),
            'duration': duration,
            'timestamp': datetime.now()
        })
        self.total_time += duration
        
    def get_slow_queries(self, threshold=1.0):
        """Retourne les requêtes lentes"""
        return [q for q in self.queries if q['duration'] > threshold]
    
    def get_stats(self):
        """Retourne les statistiques des requêtes"""
        if not self.queries:
            return {}
            
        return {
            'total_queries': len(self.queries),
            'total_time': self.total_time,
            'avg_time': self.total_time / len(self.queries),
            'slow_queries': len(self.get_slow_queries())
        }
    
    def clear(self):
        """Réinitialise le profileur"""
        self.queries = []
        self.total_time = 0
