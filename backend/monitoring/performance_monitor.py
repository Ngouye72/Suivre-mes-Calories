from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import psutil
import numpy as np
import pandas as pd
from prometheus_client import Counter, Gauge, Histogram
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self):
        # Métriques système
        self.cpu_usage = Gauge(
            'nutrition_cpu_usage',
            'Utilisation CPU en pourcentage'
        )
        
        self.memory_usage = Gauge(
            'nutrition_memory_usage',
            'Utilisation mémoire en pourcentage'
        )
        
        self.disk_usage = Gauge(
            'nutrition_disk_usage',
            'Utilisation disque en pourcentage'
        )
        
        # Métriques application
        self.request_latency = Histogram(
            'nutrition_request_latency_seconds',
            'Latence des requêtes',
            ['endpoint']
        )
        
        self.request_throughput = Counter(
            'nutrition_request_throughput',
            'Débit des requêtes',
            ['endpoint']
        )
        
        self.error_rate = Gauge(
            'nutrition_error_rate',
            'Taux d\'erreurs',
            ['endpoint']
        )
        
        # Métriques base de données
        self.db_connections = Gauge(
            'nutrition_db_connections',
            'Connexions base de données actives'
        )
        
        self.query_duration = Histogram(
            'nutrition_query_duration_seconds',
            'Durée des requêtes DB',
            ['query_type']
        )

        self.logger = logging.getLogger(__name__)

    def collect_system_metrics(self) -> Dict:
        """Collecte les métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)

            # Mémoire
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.percent)

            # Disque
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.percent)

            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Erreur collecte système: {str(e)}")
            return {}

    def track_request_performance(
        self,
        endpoint: str,
        duration: float,
        status_code: int
    ):
        """Suit la performance des requêtes"""
        try:
            # Latence
            self.request_latency.labels(
                endpoint=endpoint
            ).observe(duration)

            # Throughput
            self.request_throughput.labels(
                endpoint=endpoint
            ).inc()

            # Taux d'erreur
            if status_code >= 400:
                current_rate = self.error_rate.labels(
                    endpoint=endpoint
                )._value.get()
                self.error_rate.labels(endpoint=endpoint).set(
                    (current_rate + 1) / 2
                )
            else:
                current_rate = self.error_rate.labels(
                    endpoint=endpoint
                )._value.get()
                self.error_rate.labels(endpoint=endpoint).set(
                    current_rate / 2
                )

        except Exception as e:
            self.logger.error(f"Erreur tracking requête: {str(e)}")

    def track_database_performance(
        self,
        query_type: str,
        duration: float
    ):
        """Suit la performance de la base de données"""
        try:
            # Durée requête
            self.query_duration.labels(
                query_type=query_type
            ).observe(duration)

        except Exception as e:
            self.logger.error(f"Erreur tracking DB: {str(e)}")

    def analyze_system_performance(
        self,
        metrics: List[Dict],
        window_minutes: int = 60
    ) -> Dict:
        """Analyse la performance système"""
        try:
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Agrégation par fenêtre
            window = f'{window_minutes}min'
            agg = df.set_index('timestamp').resample(window).agg({
                'cpu_usage': ['mean', 'max', 'std'],
                'memory_usage': ['mean', 'max', 'std'],
                'disk_usage': ['mean', 'max', 'std']
            })

            return {
                "cpu": {
                    "mean": agg['cpu_usage']['mean'].iloc[-1],
                    "max": agg['cpu_usage']['max'].iloc[-1],
                    "std": agg['cpu_usage']['std'].iloc[-1]
                },
                "memory": {
                    "mean": agg['memory_usage']['mean'].iloc[-1],
                    "max": agg['memory_usage']['max'].iloc[-1],
                    "std": agg['memory_usage']['std'].iloc[-1]
                },
                "disk": {
                    "mean": agg['disk_usage']['mean'].iloc[-1],
                    "max": agg['disk_usage']['max'].iloc[-1],
                    "std": agg['disk_usage']['std'].iloc[-1]
                }
            }

        except Exception as e:
            self.logger.error(f"Erreur analyse système: {str(e)}")
            return {}

    def analyze_request_performance(
        self,
        window_minutes: int = 60
    ) -> Dict:
        """Analyse la performance des requêtes"""
        try:
            performance = {}
            for endpoint in ['/api/meals', '/api/users', '/api/weight']:
                # Latence
                latency = self.request_latency.labels(
                    endpoint=endpoint
                )._sum.get() / max(
                    self.request_latency.labels(
                        endpoint=endpoint
                    )._count.get(), 1
                )

                # Throughput
                throughput = self.request_throughput.labels(
                    endpoint=endpoint
                )._value.get() / (window_minutes * 60)

                # Taux d'erreur
                error_rate = self.error_rate.labels(
                    endpoint=endpoint
                )._value.get()

                performance[endpoint] = {
                    "latency": latency,
                    "throughput": throughput,
                    "error_rate": error_rate
                }

            return performance

        except Exception as e:
            self.logger.error(f"Erreur analyse requêtes: {str(e)}")
            return {}

    def analyze_database_performance(self) -> Dict:
        """Analyse la performance de la base de données"""
        try:
            performance = {}
            for query_type in ['select', 'insert', 'update', 'delete']:
                # Durée moyenne
                duration = self.query_duration.labels(
                    query_type=query_type
                )._sum.get() / max(
                    self.query_duration.labels(
                        query_type=query_type
                    )._count.get(), 1
                )

                performance[query_type] = {
                    "mean_duration": duration
                }

            return performance

        except Exception as e:
            self.logger.error(f"Erreur analyse DB: {str(e)}")
            return {}

    def detect_performance_issues(
        self,
        metrics: List[Dict]
    ) -> List[Dict]:
        """Détecte les problèmes de performance"""
        issues = []
        try:
            # Analyse système
            system_analysis = self.analyze_system_performance(metrics)
            
            # CPU
            if system_analysis["cpu"]["mean"] > 80:
                issues.append({
                    "type": "system",
                    "component": "cpu",
                    "severity": "high",
                    "message": f"CPU usage high: {system_analysis['cpu']['mean']}%"
                })

            # Mémoire
            if system_analysis["memory"]["mean"] > 85:
                issues.append({
                    "type": "system",
                    "component": "memory",
                    "severity": "high",
                    "message": f"Memory usage high: {system_analysis['memory']['mean']}%"
                })

            # Disque
            if system_analysis["disk"]["mean"] > 90:
                issues.append({
                    "type": "system",
                    "component": "disk",
                    "severity": "medium",
                    "message": f"Disk usage high: {system_analysis['disk']['mean']}%"
                })

            # Analyse requêtes
            request_analysis = self.analyze_request_performance()
            for endpoint, metrics in request_analysis.items():
                # Latence
                if metrics["latency"] > 1.0:
                    issues.append({
                        "type": "request",
                        "component": endpoint,
                        "severity": "high",
                        "message": f"High latency: {metrics['latency']}s"
                    })

                # Taux d'erreur
                if metrics["error_rate"] > 0.05:
                    issues.append({
                        "type": "request",
                        "component": endpoint,
                        "severity": "high",
                        "message": f"High error rate: {metrics['error_rate']}"
                    })

            # Analyse DB
            db_analysis = self.analyze_database_performance()
            for query_type, metrics in db_analysis.items():
                if metrics["mean_duration"] > 0.5:
                    issues.append({
                        "type": "database",
                        "component": query_type,
                        "severity": "medium",
                        "message": f"Slow queries: {metrics['mean_duration']}s"
                    })

        except Exception as e:
            self.logger.error(f"Erreur détection problèmes: {str(e)}")

        return issues

    def generate_performance_report(
        self,
        metrics: List[Dict]
    ) -> Dict:
        """Génère un rapport de performance"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "system_performance": self.analyze_system_performance(metrics),
                "request_performance": self.analyze_request_performance(),
                "database_performance": self.analyze_database_performance(),
                "issues": self.detect_performance_issues(metrics),
                "recommendations": self._generate_performance_recommendations(metrics)
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_performance_recommendations(
        self,
        metrics: List[Dict]
    ) -> List[Dict]:
        """Génère des recommandations de performance"""
        recommendations = []
        try:
            # Analyse problèmes
            issues = self.detect_performance_issues(metrics)
            
            # Recommandations système
            system_issues = [
                issue for issue in issues
                if issue["type"] == "system"
            ]
            if system_issues:
                recommendations.append({
                    "type": "system",
                    "priority": "high",
                    "message": "Optimiser ressources système",
                    "actions": [
                        "Augmenter ressources",
                        "Optimiser utilisation",
                        "Mettre en place auto-scaling"
                    ]
                })

            # Recommandations requêtes
            request_issues = [
                issue for issue in issues
                if issue["type"] == "request"
            ]
            if request_issues:
                recommendations.append({
                    "type": "request",
                    "priority": "high",
                    "message": "Améliorer performance requêtes",
                    "actions": [
                        "Optimiser endpoints",
                        "Implémenter caching",
                        "Revoir logique métier"
                    ]
                })

            # Recommandations DB
            db_issues = [
                issue for issue in issues
                if issue["type"] == "database"
            ]
            if db_issues:
                recommendations.append({
                    "type": "database",
                    "priority": "medium",
                    "message": "Optimiser performance DB",
                    "actions": [
                        "Optimiser requêtes",
                        "Ajouter indexes",
                        "Revoir schéma"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
perf_monitor = PerformanceMonitor()

# Collecte métriques système
system_metrics = perf_monitor.collect_system_metrics()

# Tracking requête
perf_monitor.track_request_performance(
    endpoint='/api/meals',
    duration=0.5,
    status_code=200
)

# Tracking DB
perf_monitor.track_database_performance(
    query_type='select',
    duration=0.1
)

# Analyse performance
metrics = [
    # Liste de métriques système
]
system_analysis = perf_monitor.analyze_system_performance(metrics)
request_analysis = perf_monitor.analyze_request_performance()
db_analysis = perf_monitor.analyze_database_performance()

# Détection problèmes
issues = perf_monitor.detect_performance_issues(metrics)

# Génération rapport
report = perf_monitor.generate_performance_report(metrics)
"""
