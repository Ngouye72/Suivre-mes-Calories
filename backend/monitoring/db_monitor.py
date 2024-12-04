from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
import psutil
import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy import event
import time
from datetime import datetime, timedelta
import threading
import json

class DatabaseMonitor:
    def __init__(self, engine: Engine):
        self.engine = engine
        
        # Métriques Prometheus
        self.query_counter = Counter(
            'nutrition_db_queries_total',
            'Nombre total de requêtes',
            ['query_type', 'table']
        )
        
        self.query_duration = Histogram(
            'nutrition_db_query_duration_seconds',
            'Durée des requêtes',
            ['query_type', 'table']
        )
        
        self.connection_gauge = Gauge(
            'nutrition_db_connections',
            'Nombre de connexions actives'
        )
        
        self.table_size = Gauge(
            'nutrition_db_table_size_bytes',
            'Taille des tables',
            ['table']
        )
        
        self.table_rows = Gauge(
            'nutrition_db_table_rows',
            'Nombre de lignes par table',
            ['table']
        )
        
        self.deadlock_counter = Counter(
            'nutrition_db_deadlocks_total',
            'Nombre total de deadlocks'
        )
        
        self.cache_hit_ratio = Gauge(
            'nutrition_db_cache_hit_ratio',
            'Ratio de hits du cache'
        )

        self.logger = logging.getLogger(__name__)
        
        # Activation du monitoring SQLAlchemy
        event.listen(engine, 'before_cursor_execute', self._before_cursor_execute)
        event.listen(engine, 'after_cursor_execute', self._after_cursor_execute)
        
        # Démarrage du monitoring périodique
        self._start_periodic_monitoring()

    def _before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Callback avant l'exécution d'une requête"""
        conn.info.setdefault('query_start_time', []).append(time.time())

    def _after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Callback après l'exécution d'une requête"""
        try:
            start_time = conn.info['query_start_time'].pop()
            duration = time.time() - start_time
            
            # Analyse de la requête
            query_type = self._get_query_type(statement)
            table = self._get_table_name(statement)
            
            # Métriques
            self.query_counter.labels(
                query_type=query_type,
                table=table
            ).inc()
            
            self.query_duration.labels(
                query_type=query_type,
                table=table
            ).observe(duration)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring de requête: {str(e)}")

    def _get_query_type(self, statement: str) -> str:
        """Détermine le type de requête"""
        statement = statement.strip().upper()
        if statement.startswith('SELECT'):
            return 'SELECT'
        elif statement.startswith('INSERT'):
            return 'INSERT'
        elif statement.startswith('UPDATE'):
            return 'UPDATE'
        elif statement.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'

    def _get_table_name(self, statement: str) -> str:
        """Extrait le nom de la table de la requête"""
        try:
            # Analyse simple pour démo
            words = statement.strip().upper().split()
            if 'FROM' in words:
                idx = words.index('FROM')
                if idx + 1 < len(words):
                    return words[idx + 1].strip(';')
            return 'unknown'
        except Exception:
            return 'unknown'

    def _start_periodic_monitoring(self):
        """Démarre le monitoring périodique"""
        def periodic_check():
            while True:
                try:
                    self._check_connections()
                    self._check_table_stats()
                    self._check_cache_stats()
                    time.sleep(60)  # Vérification toutes les minutes
                except Exception as e:
                    self.logger.error(f"Erreur monitoring périodique: {str(e)}")

        thread = threading.Thread(target=periodic_check, daemon=True)
        thread.start()

    def _check_connections(self):
        """Vérifie les connexions actives"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                active_connections = result.scalar()
                self.connection_gauge.set(active_connections)
        except Exception as e:
            self.logger.error(f"Erreur vérification connexions: {str(e)}")

    def _check_table_stats(self):
        """Vérifie les statistiques des tables"""
        try:
            with self.engine.connect() as conn:
                # Taille des tables
                result = conn.execute("""
                    SELECT relname as table_name,
                           pg_total_relation_size(relid) as total_size,
                           n_live_tup as row_count
                    FROM pg_stat_user_tables
                """)
                
                for row in result:
                    self.table_size.labels(
                        table=row.table_name
                    ).set(row.total_size)
                    
                    self.table_rows.labels(
                        table=row.table_name
                    ).set(row.row_count)
                    
        except Exception as e:
            self.logger.error(f"Erreur vérification stats tables: {str(e)}")

    def _check_cache_stats(self):
        """Vérifie les statistiques du cache"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute("""
                    SELECT 
                        sum(heap_blks_hit) as hits,
                        sum(heap_blks_read) as reads
                    FROM pg_statio_user_tables
                """)
                row = result.fetchone()
                
                if row and (row.hits + row.reads) > 0:
                    hit_ratio = row.hits / (row.hits + row.reads)
                    self.cache_hit_ratio.set(hit_ratio)
                    
        except Exception as e:
            self.logger.error(f"Erreur vérification cache: {str(e)}")

    def analyze_slow_queries(
        self,
        threshold_seconds: float = 1.0,
        timeframe_hours: int = 24
    ) -> List[Dict]:
        """Analyse les requêtes lentes"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute("""
                    SELECT query,
                           calls,
                           total_time / calls as avg_time,
                           rows
                    FROM pg_stat_statements
                    WHERE total_time / calls > :threshold
                    AND last_call >= now() - interval ':hours hours'
                    ORDER BY avg_time DESC
                    LIMIT 10
                """, {
                    "threshold": threshold_seconds * 1000,  # en ms
                    "hours": timeframe_hours
                })
                
                return [{
                    "query": row.query,
                    "calls": row.calls,
                    "avg_time": row.avg_time,
                    "rows": row.rows
                } for row in result]
                
        except Exception as e:
            self.logger.error(f"Erreur analyse requêtes lentes: {str(e)}")
            return []

    def analyze_index_usage(self) -> List[Dict]:
        """Analyse l'utilisation des index"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC
                """)
                
                return [{
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "index": row.indexname,
                    "scans": row.idx_scan,
                    "tuples_read": row.idx_tup_read,
                    "tuples_fetched": row.idx_tup_fetch
                } for row in result]
                
        except Exception as e:
            self.logger.error(f"Erreur analyse index: {str(e)}")
            return []

    def analyze_table_bloat(self) -> List[Dict]:
        """Analyse le bloat des tables"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute("""
                    SELECT
                        schemaname,
                        tablename,
                        n_dead_tup,
                        n_live_tup,
                        n_dead_tup::float / NULLIF(n_live_tup, 0) as dead_ratio
                    FROM pg_stat_user_tables
                    WHERE n_dead_tup > 0
                    ORDER BY dead_ratio DESC
                """)
                
                return [{
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "dead_tuples": row.n_dead_tup,
                    "live_tuples": row.n_live_tup,
                    "dead_ratio": row.dead_ratio
                } for row in result]
                
        except Exception as e:
            self.logger.error(f"Erreur analyse bloat: {str(e)}")
            return []

    def generate_db_report(self) -> Dict:
        """Génère un rapport complet sur la base de données"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "general_stats": {
                    "active_connections": self.connection_gauge._value.get(),
                    "cache_hit_ratio": self.cache_hit_ratio._value.get(),
                    "total_queries": self.query_counter._value.get()
                },
                "performance_analysis": {
                    "slow_queries": self.analyze_slow_queries(),
                    "index_usage": self.analyze_index_usage(),
                    "table_bloat": self.analyze_table_bloat()
                },
                "recommendations": self._generate_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les métriques"""
        recommendations = []
        
        try:
            # Analyse du cache
            cache_ratio = self.cache_hit_ratio._value.get()
            if cache_ratio < 0.9:
                recommendations.append(
                    "Le ratio de hits du cache est bas. Augmenter la mémoire cache."
                )

            # Analyse des connexions
            connections = self.connection_gauge._value.get()
            if connections > 100:  # seuil arbitraire
                recommendations.append(
                    "Nombre élevé de connexions. Vérifier le pooling."
                )

            # Analyse du bloat
            bloat_analysis = self.analyze_table_bloat()
            for table in bloat_analysis:
                if table["dead_ratio"] > 0.2:  # 20% de tuples morts
                    recommendations.append(
                        f"Table {table['table']} nécessite un VACUUM."
                    )

            # Analyse des index
            index_analysis = self.analyze_index_usage()
            unused_indexes = [
                idx for idx in index_analysis
                if idx["scans"] == 0 and idx["tuples_fetched"] == 0
            ]
            if unused_indexes:
                recommendations.append(
                    f"{len(unused_indexes)} index non utilisés. Considérer leur suppression."
                )

        except Exception as e:
            self.logger.error(f"Erreur génération recommandations: {str(e)}")

        return recommendations

# Exemple d'utilisation:
"""
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost:5432/nutrition_db')
db_monitor = DatabaseMonitor(engine)

# Analyse des requêtes lentes
slow_queries = db_monitor.analyze_slow_queries(threshold_seconds=1.0)

# Analyse des index
index_usage = db_monitor.analyze_index_usage()

# Analyse du bloat
bloat_analysis = db_monitor.analyze_table_bloat()

# Génération rapport
report = db_monitor.generate_db_report()
"""
