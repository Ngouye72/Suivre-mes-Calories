from prometheus_client import Gauge, Counter, Histogram
import psycopg2
from psycopg2.extras import DictCursor
import time
from functools import wraps

# Métriques de base de données
DB_CONNECTIONS = Gauge(
    'nutrition_db_connections',
    'Number of active database connections',
    ['database', 'state']
)

DB_TRANSACTION_DURATION = Histogram(
    'nutrition_db_transaction_duration_seconds',
    'Database transaction duration',
    ['operation', 'table'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

DB_QUERY_COUNT = Counter(
    'nutrition_db_queries_total',
    'Total number of database queries',
    ['operation', 'table']
)

DB_TABLE_SIZE = Gauge(
    'nutrition_db_table_size_bytes',
    'Size of database tables in bytes',
    ['table']
)

DB_INDEX_SIZE = Gauge(
    'nutrition_db_index_size_bytes',
    'Size of database indexes in bytes',
    ['table', 'index']
)

DB_CACHE_HIT_RATIO = Gauge(
    'nutrition_db_cache_hit_ratio',
    'Database cache hit ratio',
    ['table']
)

class DatabaseMetricsCollector:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def collect_metrics(self):
        """Collecter toutes les métriques de la base de données"""
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                self._collect_connection_metrics(cur)
                self._collect_table_metrics(cur)
                self._collect_index_metrics(cur)
                self._collect_cache_metrics(cur)
    
    def _collect_connection_metrics(self, cur):
        """Collecter les métriques de connexion"""
        cur.execute("""
            SELECT state, COUNT(*) 
            FROM pg_stat_activity 
            GROUP BY state
        """)
        for row in cur.fetchall():
            DB_CONNECTIONS.labels(
                database=self.db_config['dbname'],
                state=row['state']
            ).set(row['count'])
    
    def _collect_table_metrics(self, cur):
        """Collecter les métriques des tables"""
        cur.execute("""
            SELECT 
                relname as table_name,
                pg_total_relation_size(relid) as total_size
            FROM pg_catalog.pg_statio_user_tables
        """)
        for row in cur.fetchall():
            DB_TABLE_SIZE.labels(
                table=row['table_name']
            ).set(row['total_size'])
    
    def _collect_index_metrics(self, cur):
        """Collecter les métriques des index"""
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                indexrelname,
                pg_relation_size(indexrelid) as index_size
            FROM pg_catalog.pg_statio_user_indexes
        """)
        for row in cur.fetchall():
            DB_INDEX_SIZE.labels(
                table=row['tablename'],
                index=row['indexrelname']
            ).set(row['index_size'])
    
    def _collect_cache_metrics(self, cur):
        """Collecter les métriques de cache"""
        cur.execute("""
            SELECT 
                relname as table_name,
                heap_blks_hit,
                heap_blks_read,
                CASE WHEN heap_blks_hit + heap_blks_read = 0 
                    THEN 0 
                    ELSE heap_blks_hit::float / (heap_blks_hit + heap_blks_read) 
                END as cache_hit_ratio
            FROM pg_statio_user_tables
        """)
        for row in cur.fetchall():
            DB_CACHE_HIT_RATIO.labels(
                table=row['table_name']
            ).set(row['cache_hit_ratio'])

def track_db_operation(operation, table):
    """Décorateur pour suivre les opérations de base de données"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Incrémenter le compteur de requêtes
            DB_QUERY_COUNT.labels(
                operation=operation,
                table=table
            ).inc()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Enregistrer la durée de la transaction
                DB_TRANSACTION_DURATION.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                
                return result
                
            except Exception as e:
                # En cas d'erreur, on enregistre quand même la durée
                duration = time.time() - start_time
                DB_TRANSACTION_DURATION.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                raise e
                
        return wrapper
    return decorator

# Exemple d'utilisation:
"""
@track_db_operation('insert', 'meals')
def create_meal(meal_data):
    with db.session.begin():
        meal = Meal(**meal_data)
        db.session.add(meal)
        return meal

# Configuration et démarrage du collecteur
db_config = {
    'dbname': 'nutrition_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'localhost'
}

collector = DatabaseMetricsCollector(db_config)

# Collecter les métriques périodiquement
def collect_metrics_job():
    while True:
        collector.collect_metrics()
        time.sleep(60)  # Collecter toutes les minutes

# Démarrer dans un thread séparé
import threading
metrics_thread = threading.Thread(target=collect_metrics_job)
metrics_thread.daemon = True
metrics_thread.start()
"""
