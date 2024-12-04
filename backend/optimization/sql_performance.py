from sqlalchemy import event, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from functools import wraps
import time
import logging
from typing import Any, Callable, List, Dict, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLPerformanceMonitor:
    def __init__(self, threshold_ms: int = 100):
        self.threshold_ms = threshold_ms
        self.slow_queries: List[Dict[str, Any]] = []
        
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(self, conn, cursor, statement, 
                            parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(self, conn, cursor, statement,
                           parameters, context, executemany):
        total_time = time.time() - conn.info['query_start_time'].pop() * 1000
        
        if total_time > self.threshold_ms:
            self.slow_queries.append({
                'query': statement,
                'parameters': parameters,
                'execution_time': total_time
            })
            logger.warning(f"Requête lente détectée ({total_time:.2f}ms): {statement}")
            
    def get_slow_queries(self) -> List[Dict[str, Any]]:
        return sorted(
            self.slow_queries,
            key=lambda x: x['execution_time'],
            reverse=True
        )
        
    def clear_slow_queries(self):
        self.slow_queries.clear()

def optimize_query(func: Callable) -> Callable:
    """Décorateur pour optimiser automatiquement les requêtes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extraction de la session si présente
        session = next((arg for arg in args if isinstance(arg, Session)), None)
        if not session:
            return func(*args, **kwargs)
            
        # Active l'eager loading si nécessaire
        if hasattr(session, 'enable_eager_loading'):
            session.enable_eager_loading = True
            
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            if hasattr(session, 'enable_eager_loading'):
                session.enable_eager_loading = False
    return wrapper

class QueryOptimizer:
    def __init__(self, session: Session):
        self.session = session
        
    def analyze_query(self, query: Any) -> Dict[str, Any]:
        """Analyse une requête pour détecter les problèmes potentiels"""
        start_time = time.time()
        explain_plan = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        
        # Exécute EXPLAIN ANALYZE
        result = self.session.execute(f"EXPLAIN ANALYZE {explain_plan}")
        execution_plan = result.fetchall()
        
        analysis = {
            'execution_time': (time.time() - start_time) * 1000,
            'plan': execution_plan,
            'warnings': [],
            'suggestions': []
        }
        
        # Analyse du plan d'exécution
        self._analyze_execution_plan(analysis)
        
        return analysis
        
    def _analyze_execution_plan(self, analysis: Dict[str, Any]):
        """Analyse le plan d'exécution pour générer des suggestions"""
        plan_str = '\n'.join(str(row[0]) for row in analysis['plan'])
        
        # Détection des scans séquentiels
        if 'Seq Scan' in plan_str:
            analysis['warnings'].append("Scan séquentiel détecté")
            analysis['suggestions'].append(
                "Considérer l'ajout d'un index pour éviter les scans séquentiels"
            )
            
        # Détection des jointures coûteuses
        if 'Nested Loop' in plan_str:
            analysis['warnings'].append("Jointure imbriquée détectée")
            analysis['suggestions'].append(
                "Optimiser les jointures avec des index appropriés"
            )
            
        # Vérification des estimations de lignes
        if 'rows=' in plan_str:
            analysis['warnings'].append("Possible mauvaise estimation du nombre de lignes")
            analysis['suggestions'].append(
                "Mettre à jour les statistiques de la table avec ANALYZE"
            )
            
    def suggest_indexes(self, table_name: str) -> List[str]:
        """Suggère des index basés sur l'utilisation des requêtes"""
        # Analyse des colonnes fréquemment utilisées
        query = f"""
        SELECT a.attname, n_distinct, null_frac
        FROM pg_stats s
        JOIN pg_attribute a ON a.attname = s.attname
        WHERE schemaname = 'public' AND tablename = '{table_name}'
        ORDER BY n_distinct DESC;
        """
        
        result = self.session.execute(query)
        suggestions = []
        
        for row in result:
            column, n_distinct, null_frac = row
            
            # Suggère un index si la colonne a beaucoup de valeurs distinctes
            if n_distinct > 100 and null_frac < 0.5:
                suggestions.append(
                    f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column});"
                )
                
        return suggestions
        
    def optimize_table(self, table_name: str):
        """Optimise une table spécifique"""
        # Analyse la table
        self.session.execute(f"ANALYZE {table_name};")
        
        # Vacuum pour récupérer l'espace
        self.session.execute(f"VACUUM ANALYZE {table_name};")
        
        # Suggère des index
        return self.suggest_indexes(table_name)

# Exemple d'utilisation:
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Création de la connexion
engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)
session = Session()

# Monitoring des performances
monitor = SQLPerformanceMonitor(threshold_ms=100)

# Optimisation des requêtes
optimizer = QueryOptimizer(session)

# Exemple avec décorateur
@optimize_query
def get_user_meals(session, user_id):
    return session.query(Meal).filter_by(user_id=user_id).all()

# Analyse d'une requête
query = session.query(Meal).join(User).filter(User.id == 1)
analysis = optimizer.analyze_query(query)

# Optimisation d'une table
suggestions = optimizer.optimize_table('meals')

# Vérification des requêtes lentes
slow_queries = monitor.get_slow_queries()
"""
