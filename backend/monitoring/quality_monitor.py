from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.metrics import completeness_score, homogeneity_score

class QualityMonitor:
    def __init__(self):
        # Métriques de qualité des données
        self.data_completeness = Gauge(
            'nutrition_data_completeness',
            'Complétude des données',
            ['data_type']
        )
        
        self.data_accuracy = Gauge(
            'nutrition_data_accuracy',
            'Précision des données',
            ['data_type']
        )
        
        self.data_consistency = Gauge(
            'nutrition_data_consistency',
            'Cohérence des données',
            ['data_type']
        )
        
        # Métriques de performance
        self.response_time = Histogram(
            'nutrition_response_time',
            'Temps de réponse',
            ['endpoint']
        )
        
        self.error_rate = Counter(
            'nutrition_error_total',
            'Taux d\'erreurs',
            ['error_type']
        )
        
        self.request_rate = Counter(
            'nutrition_request_total',
            'Taux de requêtes',
            ['endpoint']
        )
        
        # Métriques de validation
        self.validation_errors = Counter(
            'nutrition_validation_error_total',
            'Erreurs de validation',
            ['validation_type']
        )
        
        self.data_quality_score = Gauge(
            'nutrition_data_quality_score',
            'Score de qualité des données',
            ['metric_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_data_completeness(
        self,
        data_type: str,
        total_fields: int,
        filled_fields: int
    ):
        """Suit la complétude des données"""
        try:
            completeness = filled_fields / total_fields
            self.data_completeness.labels(
                data_type=data_type
            ).set(completeness)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de complétude: {str(e)}")

    def track_data_accuracy(
        self,
        data_type: str,
        predicted: List[Any],
        actual: List[Any]
    ):
        """Suit la précision des données"""
        try:
            accuracy = sum(p == a for p, a in zip(predicted, actual)) / len(actual)
            self.data_accuracy.labels(data_type=data_type).set(accuracy)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de précision: {str(e)}")

    def track_data_consistency(
        self,
        data_type: str,
        data_points: List[Any]
    ):
        """Suit la cohérence des données"""
        try:
            # Calcul de la cohérence basé sur la variance normalisée
            if len(data_points) > 1:
                variance = np.var(data_points)
                max_variance = np.square(max(data_points) - min(data_points))
                consistency = 1 - (variance / max_variance if max_variance > 0 else 0)
                self.data_consistency.labels(data_type=data_type).set(consistency)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de cohérence: {str(e)}")

    def track_response_time(
        self,
        endpoint: str,
        duration: float
    ):
        """Suit les temps de réponse"""
        try:
            self.response_time.labels(endpoint=endpoint).observe(duration)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi du temps de réponse: {str(e)}")

    def track_error(
        self,
        error_type: str
    ):
        """Suit les erreurs"""
        try:
            self.error_rate.labels(error_type=error_type).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi d'erreur: {str(e)}")

    def track_request(
        self,
        endpoint: str
    ):
        """Suit les requêtes"""
        try:
            self.request_rate.labels(endpoint=endpoint).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de requête: {str(e)}")

    def track_validation_error(
        self,
        validation_type: str
    ):
        """Suit les erreurs de validation"""
        try:
            self.validation_errors.labels(
                validation_type=validation_type
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de validation: {str(e)}")

    def calculate_quality_score(
        self,
        metric_type: str,
        metrics: Dict[str, float]
    ):
        """Calcule le score de qualité"""
        try:
            # Moyenne pondérée des métriques
            weights = {
                "completeness": 0.4,
                "accuracy": 0.3,
                "consistency": 0.3
            }
            
            score = sum(
                metrics.get(key, 0) * weight 
                for key, weight in weights.items()
            )
            
            self.data_quality_score.labels(
                metric_type=metric_type
            ).set(score)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du score: {str(e)}")

    def analyze_data_quality(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse la qualité des données"""
        try:
            return {
                "completeness": {
                    data_type: self.data_completeness.labels(
                        data_type=data_type
                    )._value.get()
                    for data_type in ["user", "meal", "weight"]
                },
                "accuracy": {
                    data_type: self.data_accuracy.labels(
                        data_type=data_type
                    )._value.get()
                    for data_type in ["user", "meal", "weight"]
                },
                "consistency": {
                    data_type: self.data_consistency.labels(
                        data_type=data_type
                    )._value.get()
                    for data_type in ["user", "meal", "weight"]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse qualité: {str(e)}")
            return {}

    def analyze_performance(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse les performances"""
        try:
            return {
                "response_times": {
                    endpoint: {
                        "mean": self.response_time.labels(
                            endpoint=endpoint
                        )._sum.get() / max(
                            self.response_time.labels(
                                endpoint=endpoint
                            )._count.get(), 1
                        )
                    }
                    for endpoint in ["/api/meals", "/api/users", "/api/weight"]
                },
                "error_rates": {
                    error_type: self.error_rate.labels(
                        error_type=error_type
                    )._value.get()
                    for error_type in ["validation", "system", "user"]
                },
                "request_rates": {
                    endpoint: self.request_rate.labels(
                        endpoint=endpoint
                    )._value.get()
                    for endpoint in ["/api/meals", "/api/users", "/api/weight"]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse performance: {str(e)}")
            return {}

    def generate_quality_insights(self) -> List[Dict]:
        """Génère des insights sur la qualité"""
        insights = []
        try:
            # Analyse de la qualité
            quality_analysis = self.analyze_data_quality()
            
            # Vérification de la complétude
            for data_type, completeness in quality_analysis["completeness"].items():
                if completeness < 0.9:
                    insights.append({
                        "type": "completeness",
                        "severity": "high",
                        "message": f"Données incomplètes pour {data_type}",
                        "value": completeness
                    })

            # Vérification de la précision
            for data_type, accuracy in quality_analysis["accuracy"].items():
                if accuracy < 0.95:
                    insights.append({
                        "type": "accuracy",
                        "severity": "medium",
                        "message": f"Précision faible pour {data_type}",
                        "value": accuracy
                    })

            # Vérification de la cohérence
            for data_type, consistency in quality_analysis["consistency"].items():
                if consistency < 0.85:
                    insights.append({
                        "type": "consistency",
                        "severity": "medium",
                        "message": f"Incohérences dans {data_type}",
                        "value": consistency
                    })

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération d'insights: {str(e)}")

        return insights

    def generate_performance_insights(self) -> List[Dict]:
        """Génère des insights sur les performances"""
        insights = []
        try:
            # Analyse des performances
            perf_analysis = self.analyze_performance()
            
            # Vérification des temps de réponse
            for endpoint, metrics in perf_analysis["response_times"].items():
                if metrics["mean"] > 1.0:  # seuil de 1 seconde
                    insights.append({
                        "type": "response_time",
                        "severity": "high",
                        "message": f"Temps de réponse élevé pour {endpoint}",
                        "value": metrics["mean"]
                    })

            # Vérification des erreurs
            total_errors = sum(perf_analysis["error_rates"].values())
            total_requests = sum(perf_analysis["request_rates"].values())
            if total_requests > 0:
                error_rate = total_errors / total_requests
                if error_rate > 0.01:  # seuil de 1%
                    insights.append({
                        "type": "error_rate",
                        "severity": "high",
                        "message": "Taux d'erreur élevé",
                        "value": error_rate
                    })

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération d'insights: {str(e)}")

        return insights

    def generate_quality_report(self) -> Dict:
        """Génère un rapport complet de qualité"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "data_quality": self.analyze_data_quality(),
                "performance": self.analyze_performance(),
                "quality_insights": self.generate_quality_insights(),
                "performance_insights": self.generate_performance_insights(),
                "recommendations": self._generate_quality_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_quality_recommendations(self) -> List[Dict]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        try:
            # Analyse qualité
            quality_analysis = self.analyze_data_quality()
            perf_analysis = self.analyze_performance()

            # Recommandations complétude
            if any(c < 0.9 for c in quality_analysis["completeness"].values()):
                recommendations.append({
                    "type": "data_quality",
                    "priority": "high",
                    "message": "Améliorer la complétude des données",
                    "actions": [
                        "Identifier les champs manquants fréquents",
                        "Mettre en place des validations plus strictes",
                        "Améliorer le processus de collecte"
                    ]
                })

            # Recommandations précision
            if any(a < 0.95 for a in quality_analysis["accuracy"].values()):
                recommendations.append({
                    "type": "data_quality",
                    "priority": "medium",
                    "message": "Améliorer la précision des données",
                    "actions": [
                        "Revoir les processus de validation",
                        "Mettre à jour les règles de validation",
                        "Implémenter des vérifications croisées"
                    ]
                })

            # Recommandations performance
            high_latency_endpoints = [
                endpoint
                for endpoint, metrics in perf_analysis["response_times"].items()
                if metrics["mean"] > 1.0
            ]
            if high_latency_endpoints:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "message": "Optimiser les temps de réponse",
                    "actions": [
                        "Optimiser les requêtes database",
                        "Mettre en place du caching",
                        "Revoir l'architecture des endpoints lents"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la génération des recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
quality_monitor = QualityMonitor()

# Suivi de la complétude
quality_monitor.track_data_completeness(
    data_type="user",
    total_fields=10,
    filled_fields=9
)

# Suivi de la précision
quality_monitor.track_data_accuracy(
    data_type="meal",
    predicted=[1, 2, 3],
    actual=[1, 2, 3]
)

# Suivi de la cohérence
quality_monitor.track_data_consistency(
    data_type="weight",
    data_points=[70, 70.5, 71, 70.8]
)

# Suivi des performances
quality_monitor.track_response_time(
    endpoint="/api/meals",
    duration=0.5
)

quality_monitor.track_error(
    error_type="validation"
)

quality_monitor.track_request(
    endpoint="/api/meals"
)

# Analyse de la qualité
quality_analysis = quality_monitor.analyze_data_quality()

# Analyse des performances
performance_analysis = quality_monitor.analyze_performance()

# Génération d'insights
quality_insights = quality_monitor.generate_quality_insights()
performance_insights = quality_monitor.generate_performance_insights()

# Génération rapport
report = quality_monitor.generate_quality_report()
"""
