import time
from functools import wraps
from dataclasses import dataclass
from typing import List, Dict, Any
import boto3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    name: str
    value: float
    unit: str
    dimensions: Dict[str, str]
    timestamp: datetime = None

class CloudWatchMetrics:
    def __init__(self, namespace: str = "NutritionApp"):
        self.namespace = namespace
        self.client = boto3.client('cloudwatch')
        self.metrics_buffer: List[MetricData] = []
        
    def add_metric(self, metric: MetricData):
        """Ajoute une métrique au buffer"""
        if not metric.timestamp:
            metric.timestamp = datetime.utcnow()
        self.metrics_buffer.append(metric)
        
        # Envoi automatique si le buffer est plein
        if len(self.metrics_buffer) >= 20:
            self.flush()
    
    def flush(self):
        """Envoie toutes les métriques en attente à CloudWatch"""
        if not self.metrics_buffer:
            return
            
        try:
            metric_data = [
                {
                    'MetricName': metric.name,
                    'Value': metric.value,
                    'Unit': metric.unit,
                    'Dimensions': [
                        {'Name': k, 'Value': v}
                        for k, v in metric.dimensions.items()
                    ],
                    'Timestamp': metric.timestamp
                }
                for metric in self.metrics_buffer
            ]
            
            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=metric_data
            )
            self.metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des métriques: {e}")

# Instance globale
metrics = CloudWatchMetrics()

def track_time(name: str, dimensions: Dict[str, str] = None):
    """Décorateur pour mesurer le temps d'exécution d'une fonction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            metrics.add_metric(MetricData(
                name=f"{name}_duration",
                value=duration,
                unit="Seconds",
                dimensions=dimensions or {}
            ))
            return result
        return wrapper
    return decorator

def track_user_activity(user_id: str, activity_type: str):
    """Suit l'activité utilisateur"""
    metrics.add_metric(MetricData(
        name="UserActivity",
        value=1,
        unit="Count",
        dimensions={
            "UserId": user_id,
            "ActivityType": activity_type
        }
    ))

def track_meal_metrics(user_id: str, calories: float, meal_type: str):
    """Suit les métriques des repas"""
    metrics.add_metric(MetricData(
        name="MealCalories",
        value=calories,
        unit="Count",
        dimensions={
            "UserId": user_id,
            "MealType": meal_type
        }
    ))

def track_api_call(endpoint: str, method: str, status_code: int):
    """Suit les appels API"""
    metrics.add_metric(MetricData(
        name="ApiCall",
        value=1,
        unit="Count",
        dimensions={
            "Endpoint": endpoint,
            "Method": method,
            "StatusCode": str(status_code)
        }
    ))

def track_error(error_type: str, component: str):
    """Suit les erreurs"""
    metrics.add_metric(MetricData(
        name="Error",
        value=1,
        unit="Count",
        dimensions={
            "ErrorType": error_type,
            "Component": component
        }
    ))

def track_cache_operation(operation: str, success: bool):
    """Suit les opérations de cache"""
    metrics.add_metric(MetricData(
        name="CacheOperation",
        value=1,
        unit="Count",
        dimensions={
            "Operation": operation,
            "Success": str(success)
        }
    ))

# Exemple d'utilisation:
"""
@track_time("meal_creation", {"service": "meal_service"})
def create_meal(user_id: str, meal_data: Dict[str, Any]):
    # Logique de création de repas
    track_user_activity(user_id, "create_meal")
    track_meal_metrics(user_id, meal_data["calories"], meal_data["type"])
    return meal_data

@track_time("api_endpoint", {"endpoint": "/meals"})
def handle_meal_request():
    try:
        # Logique de l'endpoint
        track_api_call("/meals", "POST", 200)
    except Exception as e:
        track_error("api_error", "meal_endpoint")
        raise
"""
