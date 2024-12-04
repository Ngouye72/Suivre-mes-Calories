import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from datetime import datetime
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any, List, Optional
import logging

class MLMonitor:
    def __init__(self, experiment_name: str = "nutrition-predictions"):
        """Initialise le monitoring ML avec MLflow"""
        self.client = MlflowClient()
        self.experiment_name = experiment_name
        self._setup_experiment()
        self.logger = logging.getLogger(__name__)

    def _setup_experiment(self):
        """Configure l'expérience MLflow"""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(
                    self.experiment_name,
                    tags={"domain": "nutrition", "env": "production"}
                )
            else:
                self.experiment_id = experiment.experiment_id
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration MLflow: {str(e)}")
            raise

    def start_run(self, run_name: Optional[str] = None) -> str:
        """Démarre un nouveau run MLflow"""
        run = mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name or f"prediction-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        return run.info.run_id

    def log_model_metrics(self, 
                         y_true: np.ndarray, 
                         y_pred: np.ndarray, 
                         prefix: str = "") -> Dict[str, float]:
        """Enregistre les métriques de performance du modèle"""
        metrics = {
            f"{prefix}mae": mean_absolute_error(y_true, y_pred),
            f"{prefix}mse": mean_squared_error(y_true, y_pred),
            f"{prefix}rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            f"{prefix}r2": r2_score(y_true, y_pred)
        }
        
        mlflow.log_metrics(metrics)
        return metrics

    def log_prediction_drift(self, 
                           predictions: np.ndarray, 
                           reference_data: np.ndarray) -> Dict[str, float]:
        """Surveille la dérive des prédictions"""
        drift_metrics = {
            "prediction_mean_drift": np.mean(predictions) - np.mean(reference_data),
            "prediction_std_drift": np.std(predictions) - np.std(reference_data),
            "prediction_range_drift": (np.ptp(predictions) - np.ptp(reference_data))
        }
        
        mlflow.log_metrics(drift_metrics)
        return drift_metrics

    def log_feature_importance(self, 
                             feature_names: List[str], 
                             importance_values: np.ndarray):
        """Enregistre l'importance des features"""
        for name, value in zip(feature_names, importance_values):
            mlflow.log_metric(f"feature_importance_{name}", float(value))

    def log_nutrition_specific_metrics(self, 
                                     predictions: Dict[str, Any], 
                                     actuals: Dict[str, Any]) -> Dict[str, float]:
        """Enregistre les métriques spécifiques à la nutrition"""
        nutrition_metrics = {
            "calorie_prediction_error": np.mean(
                np.abs(predictions["calories"] - actuals["calories"])
            ),
            "protein_prediction_error": np.mean(
                np.abs(predictions["protein"] - actuals["protein"])
            ),
            "carbs_prediction_error": np.mean(
                np.abs(predictions["carbs"] - actuals["carbs"])
            ),
            "fat_prediction_error": np.mean(
                np.abs(predictions["fat"] - actuals["fat"])
            )
        }
        
        mlflow.log_metrics(nutrition_metrics)
        return nutrition_metrics

    def log_model_artifacts(self, 
                          model: Any, 
                          feature_names: List[str], 
                          model_name: str):
        """Enregistre le modèle et ses artefacts"""
        try:
            # Enregistrer le modèle
            mlflow.sklearn.log_model(model, model_name)
            
            # Enregistrer les feature names
            mlflow.log_dict(
                {"feature_names": feature_names}, 
                "feature_names.json"
            )
            
            # Si disponible, enregistrer l'importance des features
            if hasattr(model, "feature_importances_"):
                self.log_feature_importance(
                    feature_names, 
                    model.feature_importances_
                )
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des artefacts: {str(e)}")
            raise

    def monitor_prediction_latency(self, latency_ms: float):
        """Surveille la latence des prédictions"""
        mlflow.log_metric("prediction_latency_ms", latency_ms)

    def log_prediction_confidence(self, 
                                confidences: np.ndarray, 
                                threshold: float = 0.8):
        """Surveille la confiance des prédictions"""
        confidence_metrics = {
            "mean_confidence": np.mean(confidences),
            "min_confidence": np.min(confidences),
            "low_confidence_ratio": np.mean(confidences < threshold)
        }
        
        mlflow.log_metrics(confidence_metrics)
        return confidence_metrics

    def log_nutrition_goals_metrics(self, 
                                  predicted_goals: Dict[str, Any], 
                                  actual_goals: Dict[str, Any]):
        """Surveille la précision des objectifs nutritionnels"""
        goals_metrics = {
            "weight_goal_error": abs(
                predicted_goals["weight"] - actual_goals["weight"]
            ),
            "calorie_goal_error": abs(
                predicted_goals["daily_calories"] - actual_goals["daily_calories"]
            ),
            "protein_goal_error": abs(
                predicted_goals["daily_protein"] - actual_goals["daily_protein"]
            )
        }
        
        mlflow.log_metrics(goals_metrics)
        return goals_metrics

# Exemple d'utilisation:
"""
# Initialisation
ml_monitor = MLMonitor()

# Démarrer un run
with mlflow.start_run():
    # Enregistrer les métriques de base
    metrics = ml_monitor.log_model_metrics(y_true, y_pred)
    
    # Surveiller la dérive
    drift = ml_monitor.log_prediction_drift(predictions, reference_data)
    
    # Métriques spécifiques à la nutrition
    nutrition_metrics = ml_monitor.log_nutrition_specific_metrics(
        predictions={"calories": pred_calories, "protein": pred_protein},
        actuals={"calories": true_calories, "protein": true_protein}
    )
    
    # Enregistrer le modèle et ses artefacts
    ml_monitor.log_model_artifacts(
        model=trained_model,
        feature_names=feature_names,
        model_name="nutrition_predictor"
    )
    
    # Surveiller la latence
    ml_monitor.monitor_prediction_latency(prediction_time_ms)
    
    # Surveiller la confiance
    confidence_metrics = ml_monitor.log_prediction_confidence(
        prediction_confidences
    )
"""
