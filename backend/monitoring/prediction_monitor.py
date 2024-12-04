from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from prometheus_client import Counter, Gauge, Histogram
from collections import defaultdict

class PredictionMonitor:
    def __init__(self):
        # Métriques prédiction
        self.prediction_accuracy = Gauge(
            'nutrition_prediction_accuracy',
            'Précision des prédictions',
            ['model_type']
        )
        
        self.prediction_latency = Histogram(
            'nutrition_prediction_latency',
            'Latence des prédictions',
            ['model_type']
        )
        
        self.prediction_count = Counter(
            'nutrition_prediction_count',
            'Nombre de prédictions',
            ['model_type', 'status']
        )
        
        # Métriques modèle
        self.model_performance = Gauge(
            'nutrition_model_performance',
            'Performance des modèles',
            ['model_type', 'metric']
        )
        
        self.feature_importance = Gauge(
            'nutrition_feature_importance',
            'Importance des features',
            ['model_type', 'feature']
        )
        
        # Métriques drift
        self.data_drift = Gauge(
            'nutrition_data_drift',
            'Drift des données',
            ['feature']
        )
        
        self.concept_drift = Gauge(
            'nutrition_concept_drift',
            'Drift conceptuel',
            ['model_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_prediction(
        self,
        model_type: str,
        prediction: float,
        actual: float,
        latency: float,
        features: Dict[str, float]
    ):
        """Suit une prédiction"""
        try:
            # Précision
            error = abs(prediction - actual)
            accuracy = 1 / (1 + error)
            self.prediction_accuracy.labels(
                model_type=model_type
            ).set(accuracy)

            # Latence
            self.prediction_latency.labels(
                model_type=model_type
            ).observe(latency)

            # Compteur
            status = 'success' if error < 0.1 else 'error'
            self.prediction_count.labels(
                model_type=model_type,
                status=status
            ).inc()

            # Drift features
            self._check_feature_drift(features)

        except Exception as e:
            self.logger.error(f"Erreur tracking prédiction: {str(e)}")

    def track_model_performance(
        self,
        model_type: str,
        metrics: Dict[str, float],
        feature_importance: Dict[str, float]
    ):
        """Suit la performance d'un modèle"""
        try:
            # Métriques
            for metric, value in metrics.items():
                self.model_performance.labels(
                    model_type=model_type,
                    metric=metric
                ).set(value)

            # Importance features
            for feature, importance in feature_importance.items():
                self.feature_importance.labels(
                    model_type=model_type,
                    feature=feature
                ).set(importance)

        except Exception as e:
            self.logger.error(f"Erreur tracking modèle: {str(e)}")

    def _check_feature_drift(
        self,
        features: Dict[str, float]
    ):
        """Vérifie le drift des features"""
        try:
            for feature, value in features.items():
                # Calcul drift (exemple simple)
                current_drift = self.data_drift.labels(
                    feature=feature
                )._value.get()
                
                new_drift = abs(value - current_drift) if current_drift else 0
                self.data_drift.labels(feature=feature).set(new_drift)

        except Exception as e:
            self.logger.error(f"Erreur check drift: {str(e)}")

    def analyze_predictions(
        self,
        predictions: List[Dict]
    ) -> Dict:
        """Analyse les prédictions"""
        try:
            df = pd.DataFrame(predictions)
            analysis = {}

            for model_type in df['model_type'].unique():
                model_df = df[df['model_type'] == model_type]
                
                # Métriques
                mse = mean_squared_error(
                    model_df['actual'],
                    model_df['prediction']
                )
                mae = mean_absolute_error(
                    model_df['actual'],
                    model_df['prediction']
                )
                
                analysis[model_type] = {
                    "mse": mse,
                    "mae": mae,
                    "count": len(model_df),
                    "accuracy": 1 / (1 + mae)
                }

            return analysis

        except Exception as e:
            self.logger.error(f"Erreur analyse prédictions: {str(e)}")
            return {}

    def analyze_model_drift(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse le drift des modèles"""
        try:
            drift_analysis = {
                "data_drift": {
                    feature: self.data_drift.labels(
                        feature=feature
                    )._value.get()
                    for feature in [
                        'weight', 'height', 'age',
                        'activity_level', 'meal_frequency'
                    ]
                },
                "concept_drift": {
                    model_type: self.concept_drift.labels(
                        model_type=model_type
                    )._value.get()
                    for model_type in [
                        'calorie_prediction',
                        'weight_prediction',
                        'goal_prediction'
                    ]
                }
            }

            return drift_analysis

        except Exception as e:
            self.logger.error(f"Erreur analyse drift: {str(e)}")
            return {}

    def detect_model_issues(self) -> List[Dict]:
        """Détecte les problèmes de modèles"""
        issues = []
        try:
            # Analyse drift
            drift_analysis = self.analyze_model_drift()
            
            # Problèmes data drift
            for feature, drift in drift_analysis["data_drift"].items():
                if drift > 0.3:
                    issues.append({
                        "type": "data_drift",
                        "component": feature,
                        "severity": "high",
                        "message": f"High data drift for {feature}: {drift:.2f}"
                    })

            # Problèmes concept drift
            for model, drift in drift_analysis["concept_drift"].items():
                if drift > 0.2:
                    issues.append({
                        "type": "concept_drift",
                        "component": model,
                        "severity": "high",
                        "message": f"High concept drift for {model}: {drift:.2f}"
                    })

            # Problèmes performance
            for model_type in ['calorie_prediction', 'weight_prediction']:
                accuracy = self.prediction_accuracy.labels(
                    model_type=model_type
                )._value.get()
                
                if accuracy < 0.8:
                    issues.append({
                        "type": "performance",
                        "component": model_type,
                        "severity": "medium",
                        "message": f"Low accuracy for {model_type}: {accuracy:.2f}"
                    })

        except Exception as e:
            self.logger.error(f"Erreur détection problèmes: {str(e)}")

        return issues

    def generate_prediction_report(
        self,
        predictions: List[Dict]
    ) -> Dict:
        """Génère un rapport de prédictions"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "prediction_analysis": self.analyze_predictions(predictions),
                "drift_analysis": self.analyze_model_drift(),
                "issues": self.detect_model_issues(),
                "recommendations": self._generate_model_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_model_recommendations(self) -> List[Dict]:
        """Génère des recommandations pour les modèles"""
        recommendations = []
        try:
            # Analyse problèmes
            issues = self.detect_model_issues()
            
            # Recommandations drift
            drift_issues = [
                issue for issue in issues
                if issue["type"] in ["data_drift", "concept_drift"]
            ]
            if drift_issues:
                recommendations.append({
                    "type": "drift",
                    "priority": "high",
                    "message": "Gérer le drift des modèles",
                    "actions": [
                        "Réentraîner modèles",
                        "Mettre à jour features",
                        "Ajuster seuils"
                    ]
                })

            # Recommandations performance
            performance_issues = [
                issue for issue in issues
                if issue["type"] == "performance"
            ]
            if performance_issues:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "message": "Améliorer performance modèles",
                    "actions": [
                        "Optimiser features",
                        "Ajuster hyperparamètres",
                        "Collecter plus de données"
                    ]
                })

            # Recommandations générales
            if len(issues) > 5:
                recommendations.append({
                    "type": "general",
                    "priority": "high",
                    "message": "Révision globale ML pipeline",
                    "actions": [
                        "Audit complet pipeline",
                        "Optimisation bout en bout",
                        "Documentation processus"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

    def analyze_feature_importance(
        self,
        model_type: str
    ) -> Dict[str, float]:
        """Analyse l'importance des features"""
        try:
            return {
                feature: self.feature_importance.labels(
                    model_type=model_type,
                    feature=feature
                )._value.get()
                for feature in [
                    'weight', 'height', 'age',
                    'activity_level', 'meal_frequency'
                ]
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse features: {str(e)}")
            return {}

    def get_model_metrics(
        self,
        model_type: str
    ) -> Dict[str, float]:
        """Récupère les métriques d'un modèle"""
        try:
            return {
                metric: self.model_performance.labels(
                    model_type=model_type,
                    metric=metric
                )._value.get()
                for metric in ['mse', 'mae', 'r2', 'rmse']
            }
        except Exception as e:
            self.logger.error(f"Erreur récupération métriques: {str(e)}")
            return {}

# Exemple d'utilisation:
"""
prediction_monitor = PredictionMonitor()

# Tracking prédiction
prediction_monitor.track_prediction(
    model_type='calorie_prediction',
    prediction=2000,
    actual=1950,
    latency=0.1,
    features={
        'weight': 70,
        'height': 175,
        'age': 30,
        'activity_level': 1.5
    }
)

# Tracking performance modèle
prediction_monitor.track_model_performance(
    model_type='calorie_prediction',
    metrics={
        'mse': 10000,
        'mae': 80,
        'r2': 0.85
    },
    feature_importance={
        'weight': 0.3,
        'height': 0.2,
        'age': 0.15,
        'activity_level': 0.35
    }
)

# Analyse prédictions
predictions = [
    # Liste de prédictions
]
prediction_analysis = prediction_monitor.analyze_predictions(predictions)

# Analyse drift
drift_analysis = prediction_monitor.analyze_model_drift()

# Détection problèmes
issues = prediction_monitor.detect_model_issues()

# Génération rapport
report = prediction_monitor.generate_prediction_report(predictions)

# Analyse features
feature_importance = prediction_monitor.analyze_feature_importance(
    'calorie_prediction'
)

# Métriques modèle
model_metrics = prediction_monitor.get_model_metrics(
    'calorie_prediction'
)
"""
