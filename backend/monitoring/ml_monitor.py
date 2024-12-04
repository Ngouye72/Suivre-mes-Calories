import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import logging
import json
from evidently.dashboard import Dashboard
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.metric_preset import (
    DataDriftPreset,
    TargetDriftPreset,
    DataQualityPreset,
    RegressionPreset
)

class MLMonitor:
    def __init__(self, model_name: str, tracking_uri: str = "http://localhost:5000"):
        self.model_name = model_name
        self.client = MlflowClient(tracking_uri)
        
        # Configuration MLflow
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(f"nutrition_{model_name}")

        # Métriques Prometheus
        self.prediction_counter = Counter(
            'nutrition_ml_predictions_total',
            'Nombre total de prédictions',
            ['model_name', 'prediction_type']
        )
        
        self.prediction_latency = Histogram(
            'nutrition_ml_prediction_latency_seconds',
            'Latence des prédictions',
            ['model_name']
        )
        
        self.prediction_accuracy = Gauge(
            'nutrition_ml_prediction_accuracy',
            'Précision des prédictions',
            ['model_name', 'metric_type']
        )
        
        self.feature_drift = Gauge(
            'nutrition_ml_feature_drift',
            'Drift des features',
            ['model_name', 'feature_name']
        )

        self.logger = logging.getLogger(__name__)
        self.baseline_stats = {}
        self.current_model_version = self._get_production_model_version()

    def _get_production_model_version(self) -> Optional[str]:
        """Récupère la version du modèle en production"""
        try:
            for mv in self.client.search_model_versions(f"name='{self.model_name}'"):
                if mv.current_stage == "Production":
                    return mv.version
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de la version: {str(e)}")
        return None

    def log_prediction(
        self,
        features: Dict[str, Any],
        prediction: Any,
        actual: Optional[Any] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log une prédiction individuelle"""
        try:
            start_time = datetime.now()
            
            # Log MLflow
            with mlflow.start_run(nested=True):
                mlflow.log_params(features)
                mlflow.log_metric("prediction", float(prediction))
                if actual is not None:
                    mlflow.log_metric("actual", float(actual))
                if metadata:
                    mlflow.log_params(metadata)

            # Métriques Prometheus
            self.prediction_counter.labels(
                model_name=self.model_name,
                prediction_type="nutrition"
            ).inc()
            
            duration = (datetime.now() - start_time).total_seconds()
            self.prediction_latency.labels(
                model_name=self.model_name
            ).observe(duration)

            # Log pour analyse de drift
            self._update_feature_statistics(features)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du log de prédiction: {str(e)}")

    def _update_feature_statistics(self, features: Dict[str, Any]) -> None:
        """Met à jour les statistiques des features"""
        try:
            for feature_name, value in features.items():
                if feature_name not in self.baseline_stats:
                    self.baseline_stats[feature_name] = {
                        "mean": value,
                        "variance": 0,
                        "count": 1
                    }
                else:
                    stats = self.baseline_stats[feature_name]
                    n = stats["count"]
                    old_mean = stats["mean"]
                    
                    # Mise à jour moyenne mobile
                    new_mean = old_mean + (value - old_mean) / (n + 1)
                    new_variance = (
                        (n * stats["variance"] + (value - old_mean) * (value - new_mean))
                        / (n + 1)
                    )
                    
                    self.baseline_stats[feature_name].update({
                        "mean": new_mean,
                        "variance": new_variance,
                        "count": n + 1
                    })
                    
                    # Calcul du drift
                    if n > 100:  # Seuil minimum pour le calcul
                        zscore = abs(value - new_mean) / np.sqrt(new_variance)
                        self.feature_drift.labels(
                            model_name=self.model_name,
                            feature_name=feature_name
                        ).set(zscore)
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des stats: {str(e)}")

    def evaluate_model(
        self,
        test_features: pd.DataFrame,
        test_labels: pd.Series,
        model: Any
    ) -> Dict[str, float]:
        """Évalue les performances du modèle"""
        try:
            predictions = model.predict(test_features)
            
            metrics = {}
            if self._is_classification():
                metrics.update({
                    "accuracy": accuracy_score(test_labels, predictions),
                    "precision": precision_score(
                        test_labels, predictions, average='weighted'
                    ),
                    "recall": recall_score(test_labels, predictions, average='weighted'),
                    "f1": f1_score(test_labels, predictions, average='weighted')
                })
            else:
                metrics.update({
                    "mse": mean_squared_error(test_labels, predictions),
                    "mae": mean_absolute_error(test_labels, predictions),
                    "r2": r2_score(test_labels, predictions)
                })

            # Log MLflow
            with mlflow.start_run():
                mlflow.log_metrics(metrics)
                
            # Mise à jour Prometheus
            for metric_name, value in metrics.items():
                self.prediction_accuracy.labels(
                    model_name=self.model_name,
                    metric_type=metric_name
                ).set(value)

            return metrics
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation du modèle: {str(e)}")
            return {}

    def _is_classification(self) -> bool:
        """Détermine si le modèle est de classification"""
        # À implémenter selon votre logique métier
        return False

    def analyze_predictions(
        self,
        predictions: List[Dict],
        timeframe_hours: int = 24
    ) -> Dict:
        """Analyse les prédictions récentes"""
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(predictions)
            
            analysis = {
                "total_predictions": len(predictions),
                "timeframe_hours": timeframe_hours,
                "accuracy_metrics": {},
                "drift_analysis": {},
                "performance_metrics": {}
            }

            # Métriques de précision
            if "actual" in df.columns:
                analysis["accuracy_metrics"] = self._calculate_accuracy_metrics(df)

            # Analyse de drift
            analysis["drift_analysis"] = self._analyze_drift(df)

            # Métriques de performance
            analysis["performance_metrics"] = {
                "mean_latency": self.prediction_latency._sum.get() / 
                              max(self.prediction_latency._count.get(), 1),
                "prediction_rate": len(predictions) / timeframe_hours
            }

            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des prédictions: {str(e)}")
            return {}

    def _calculate_accuracy_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcule les métriques de précision"""
        try:
            metrics = {}
            if self._is_classification():
                metrics.update({
                    "accuracy": accuracy_score(
                        df["actual"], df["prediction"]
                    ),
                    "precision": precision_score(
                        df["actual"], df["prediction"], average='weighted'
                    ),
                    "recall": recall_score(
                        df["actual"], df["prediction"], average='weighted'
                    ),
                    "f1": f1_score(
                        df["actual"], df["prediction"], average='weighted'
                    )
                })
            else:
                metrics.update({
                    "mse": mean_squared_error(df["actual"], df["prediction"]),
                    "mae": mean_absolute_error(df["actual"], df["prediction"]),
                    "r2": r2_score(df["actual"], df["prediction"])
                })
            return metrics
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
            return {}

    def _analyze_drift(self, df: pd.DataFrame) -> Dict:
        """Analyse le drift des données"""
        try:
            drift_analysis = {}
            
            # Configuration Evidently
            data_drift_dashboard = Dashboard(tabs=[
                DataDriftPreset(),
                TargetDriftPreset(),
                DataQualityPreset(),
                RegressionPreset()
            ])

            # Analyse avec Evidently
            if len(df) > 0:
                reference_data = df.iloc[:len(df)//2]  # Première moitié comme référence
                current_data = df.iloc[len(df)//2:]    # Seconde moitié comme données actuelles
                
                column_mapping = ColumnMapping()
                column_mapping.target = "prediction"
                if "actual" in df.columns:
                    column_mapping.prediction = "actual"
                
                data_drift_dashboard.calculate(
                    reference_data,
                    current_data,
                    column_mapping=column_mapping
                )
                
                # Extraction des métriques de drift
                for metric in data_drift_dashboard.metrics:
                    drift_analysis[metric.name] = metric.value
                
            return drift_analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du drift: {str(e)}")
            return {}

    def generate_model_report(self) -> Dict:
        """Génère un rapport complet sur le modèle"""
        try:
            return {
                "model_info": {
                    "name": self.model_name,
                    "version": self.current_model_version,
                    "timestamp": datetime.now().isoformat()
                },
                "performance_metrics": {
                    "accuracy": self.prediction_accuracy._value.get(),
                    "latency": self.prediction_latency._sum.get() / 
                              max(self.prediction_latency._count.get(), 1)
                },
                "prediction_stats": {
                    "total": self.prediction_counter._value.get(),
                    "feature_drift": {
                        feature: stats
                        for feature, stats in self.baseline_stats.items()
                    }
                },
                "recommendations": self._generate_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les métriques"""
        recommendations = []
        
        try:
            # Analyse de la précision
            accuracy = self.prediction_accuracy._value.get()
            if accuracy < 0.8:
                recommendations.append(
                    "La précision du modèle est faible. Envisager un retraining."
                )

            # Analyse de la latence
            avg_latency = (
                self.prediction_latency._sum.get() /
                max(self.prediction_latency._count.get(), 1)
            )
            if avg_latency > 0.1:  # 100ms
                recommendations.append(
                    "La latence des prédictions est élevée. Optimiser le modèle."
                )

            # Analyse du drift
            for feature, stats in self.baseline_stats.items():
                if stats.get("count", 0) > 100:
                    zscore = abs(
                        stats["mean"] - stats.get("initial_mean", stats["mean"])
                    ) / np.sqrt(stats["variance"])
                    if zscore > 3:
                        recommendations.append(
                            f"Drift significatif détecté pour {feature}."
                        )

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des recommandations: {str(e)}")

        return recommendations

# Exemple d'utilisation:
"""
ml_monitor = MLMonitor("nutrition_recommender")

# Log d'une prédiction
features = {
    "age": 30,
    "weight": 70,
    "height": 175,
    "activity_level": "moderate"
}
prediction = 2000  # calories recommandées
ml_monitor.log_prediction(features, prediction)

# Évaluation du modèle
test_features = pd.DataFrame(...)
test_labels = pd.Series(...)
metrics = ml_monitor.evaluate_model(test_features, test_labels, model)

# Analyse des prédictions
predictions = [...]  # liste de prédictions récentes
analysis = ml_monitor.analyze_predictions(predictions)

# Génération rapport
report = ml_monitor.generate_model_report()
"""
