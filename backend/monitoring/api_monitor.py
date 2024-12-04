from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json

class APIMonitor:
    def __init__(self):
        # Métriques des requêtes
        self.request_duration = Histogram(
            'nutrition_request_duration_seconds',
            'Durée des requêtes API',
            ['endpoint', 'method']
        )
        
        self.request_count = Counter(
            'nutrition_request_total',
            'Nombre total de requêtes',
            ['endpoint', 'method', 'status']
        )
        
        self.request_size = Histogram(
            'nutrition_request_size_bytes',
            'Taille des requêtes',
            ['endpoint']
        )
        
        # Métriques des erreurs
        self.error_count = Counter(
            'nutrition_error_total',
            'Nombre total d\'erreurs',
            ['endpoint', 'error_type']
        )
        
        self.error_rate = Gauge(
            'nutrition_error_rate',
            'Taux d\'erreurs',
            ['endpoint']
        )
        
        # Métriques de performance
        self.response_time = Histogram(
            'nutrition_response_time_seconds',
            'Temps de réponse',
            ['endpoint', 'percentile']
        )
        
        self.throughput = Counter(
            'nutrition_throughput_total',
            'Débit de requêtes',
            ['endpoint']
        )
        
        # Métriques utilisateur
        self.user_sessions = Gauge(
            'nutrition_user_sessions',
            'Sessions utilisateur actives',
            ['user_type']
        )
        
        self.user_interactions = Counter(
            'nutrition_user_interactions_total',
            'Interactions utilisateur',
            ['interaction_type']
        )

        self.logger = logging.getLogger(__name__)

    async def track_request(
        self,
        request: Request,
        call_next
    ):
        """Middleware pour suivre les requêtes API"""
        try:
            start_time = time.time()
            
            # Tracking de la requête
            endpoint = request.url.path
            method = request.method
            
            # Taille de la requête
            content_length = int(request.headers.get('content-length', 0))
            self.request_size.labels(endpoint=endpoint).observe(content_length)
            
            # Exécution de la requête
            response = await call_next(request)
            
            # Durée et statut
            duration = time.time() - start_time
            self.request_duration.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
            
            self.request_count.labels(
                endpoint=endpoint,
                method=method,
                status=response.status_code
            ).inc()
            
            # Throughput
            self.throughput.labels(endpoint=endpoint).inc()
            
            # Erreurs
            if response.status_code >= 400:
                self.error_count.labels(
                    endpoint=endpoint,
                    error_type=f'http_{response.status_code}'
                ).inc()
                
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur tracking requête: {str(e)}")
            raise

    def track_user_interaction(
        self,
        user_id: str,
        interaction_type: str,
        details: Dict
    ):
        """Suit les interactions utilisateur"""
        try:
            self.user_interactions.labels(
                interaction_type=interaction_type
            ).inc()
            
            # Mise à jour sessions
            user_type = details.get('user_type', 'standard')
            self.user_sessions.labels(
                user_type=user_type
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur tracking interaction: {str(e)}")

    def track_api_error(
        self,
        endpoint: str,
        error_type: str,
        details: Dict
    ):
        """Suit les erreurs API"""
        try:
            self.error_count.labels(
                endpoint=endpoint,
                error_type=error_type
            ).inc()
            
            # Calcul taux d'erreur
            total_requests = self.request_count.labels(
                endpoint=endpoint,
                method='ALL',
                status='ALL'
            )._value.get()
            
            if total_requests > 0:
                error_rate = (
                    self.error_count.labels(
                        endpoint=endpoint,
                        error_type='ALL'
                    )._value.get() / total_requests
                )
                self.error_rate.labels(endpoint=endpoint).set(error_rate)
            
        except Exception as e:
            self.logger.error(f"Erreur tracking erreur: {str(e)}")

    def analyze_api_performance(
        self,
        timeframe_minutes: int = 60
    ) -> Dict:
        """Analyse les performances de l'API"""
        try:
            return {
                "requests": {
                    endpoint: {
                        "count": self.request_count.labels(
                            endpoint=endpoint,
                            method='ALL',
                            status='ALL'
                        )._value.get(),
                        "duration": {
                            "mean": self.request_duration.labels(
                                endpoint=endpoint,
                                method='ALL'
                            )._sum.get() / max(
                                self.request_duration.labels(
                                    endpoint=endpoint,
                                    method='ALL'
                                )._count.get(), 1
                            )
                        },
                        "size": {
                            "mean": self.request_size.labels(
                                endpoint=endpoint
                            )._sum.get() / max(
                                self.request_size.labels(
                                    endpoint=endpoint
                                )._count.get(), 1
                            )
                        }
                    }
                    for endpoint in ['/api/meals', '/api/users', '/api/weight']
                },
                "errors": {
                    endpoint: {
                        "count": self.error_count.labels(
                            endpoint=endpoint,
                            error_type='ALL'
                        )._value.get(),
                        "rate": self.error_rate.labels(
                            endpoint=endpoint
                        )._value.get()
                    }
                    for endpoint in ['/api/meals', '/api/users', '/api/weight']
                },
                "performance": {
                    endpoint: {
                        "throughput": self.throughput.labels(
                            endpoint=endpoint
                        )._value.get() / (timeframe_minutes * 60),
                        "response_time": {
                            percentile: self.response_time.labels(
                                endpoint=endpoint,
                                percentile=str(percentile)
                            )._value.get()
                            for percentile in [50, 90, 99]
                        }
                    }
                    for endpoint in ['/api/meals', '/api/users', '/api/weight']
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse performance: {str(e)}")
            return {}

    def analyze_user_activity(self) -> Dict:
        """Analyse l'activité utilisateur"""
        try:
            return {
                "sessions": {
                    user_type: self.user_sessions.labels(
                        user_type=user_type
                    )._value.get()
                    for user_type in ['standard', 'premium', 'admin']
                },
                "interactions": {
                    interaction_type: self.user_interactions.labels(
                        interaction_type=interaction_type
                    )._value.get()
                    for interaction_type in [
                        'meal_log',
                        'weight_update',
                        'goal_check'
                    ]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse activité: {str(e)}")
            return {}

    def generate_api_insights(self) -> List[Dict]:
        """Génère des insights sur l'API"""
        insights = []
        try:
            # Analyse performance
            perf_analysis = self.analyze_api_performance()
            
            # Vérification temps de réponse
            for endpoint, metrics in perf_analysis["performance"].items():
                if metrics["response_time"]["90"] > 1.0:
                    insights.append({
                        "type": "performance",
                        "severity": "high",
                        "message": f"Temps de réponse élevé pour {endpoint}",
                        "value": metrics["response_time"]["90"]
                    })

            # Vérification taux d'erreur
            for endpoint, metrics in perf_analysis["errors"].items():
                if metrics["rate"] > 0.05:
                    insights.append({
                        "type": "errors",
                        "severity": "high",
                        "message": f"Taux d'erreur élevé pour {endpoint}",
                        "value": metrics["rate"]
                    })

            # Vérification throughput
            for endpoint, metrics in perf_analysis["performance"].items():
                if metrics["throughput"] < 10:
                    insights.append({
                        "type": "throughput",
                        "severity": "medium",
                        "message": f"Faible throughput pour {endpoint}",
                        "value": metrics["throughput"]
                    })

        except Exception as e:
            self.logger.error(f"Erreur génération insights: {str(e)}")

        return insights

    def generate_api_report(self) -> Dict:
        """Génère un rapport complet sur l'API"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "performance": self.analyze_api_performance(),
                "user_activity": self.analyze_user_activity(),
                "insights": self.generate_api_insights(),
                "recommendations": self._generate_api_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_api_recommendations(self) -> List[Dict]:
        """Génère des recommandations pour l'API"""
        recommendations = []
        try:
            # Analyse performance
            perf_analysis = self.analyze_api_performance()
            
            # Recommandations temps de réponse
            slow_endpoints = [
                endpoint
                for endpoint, metrics in perf_analysis["performance"].items()
                if metrics["response_time"]["90"] > 1.0
            ]
            if slow_endpoints:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "message": "Optimiser les temps de réponse",
                    "actions": [
                        "Optimiser les requêtes database",
                        "Implémenter du caching",
                        "Revoir la logique métier"
                    ]
                })

            # Recommandations erreurs
            high_error_endpoints = [
                endpoint
                for endpoint, metrics in perf_analysis["errors"].items()
                if metrics["rate"] > 0.05
            ]
            if high_error_endpoints:
                recommendations.append({
                    "type": "errors",
                    "priority": "high",
                    "message": "Réduire le taux d'erreurs",
                    "actions": [
                        "Améliorer la gestion d'erreurs",
                        "Ajouter des validations",
                        "Monitorer les causes racines"
                    ]
                })

            # Recommandations throughput
            low_throughput_endpoints = [
                endpoint
                for endpoint, metrics in perf_analysis["performance"].items()
                if metrics["throughput"] < 10
            ]
            if low_throughput_endpoints:
                recommendations.append({
                    "type": "throughput",
                    "priority": "medium",
                    "message": "Améliorer le throughput",
                    "actions": [
                        "Optimiser les ressources",
                        "Mettre en place du load balancing",
                        "Augmenter la capacité"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
api_monitor = APIMonitor()

# Utilisation comme middleware FastAPI
app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=api_monitor.track_request
)

# Tracking interaction utilisateur
api_monitor.track_user_interaction(
    user_id="123",
    interaction_type="meal_log",
    details={"user_type": "premium"}
)

# Tracking erreur API
api_monitor.track_api_error(
    endpoint="/api/meals",
    error_type="validation_error",
    details={"message": "Invalid data"}
)

# Analyse performance
performance = api_monitor.analyze_api_performance()

# Analyse activité
activity = api_monitor.analyze_user_activity()

# Génération insights
insights = api_monitor.generate_api_insights()

# Génération rapport
report = api_monitor.generate_api_report()
"""
