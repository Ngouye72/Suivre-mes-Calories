import boto3
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class CustomMetricsManager:
    def __init__(self, region: str = 'eu-west-1'):
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.namespace = 'NutritionApp'
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def put_metric(self,
                  metric_name: str,
                  value: float,
                  unit: str,
                  dimensions: List[Dict[str, str]],
                  timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Envoie une métrique personnalisée à CloudWatch"""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Dimensions': dimensions
            }
            
            if timestamp:
                metric_data['Timestamp'] = timestamp
                
            response = self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            
            return {
                'status': 'success',
                'message': f'Métrique {metric_name} envoyée avec succès'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de la métrique: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def track_api_latency(self,
                         endpoint: str,
                         latency: float,
                         status_code: int) -> Dict[str, Any]:
        """Suit la latence des endpoints API"""
        dimensions = [
            {
                'Name': 'Endpoint',
                'Value': endpoint
            },
            {
                'Name': 'StatusCode',
                'Value': str(status_code)
            }
        ]
        
        return self.put_metric(
            metric_name='APILatency',
            value=latency,
            unit='Milliseconds',
            dimensions=dimensions
        )
        
    def track_user_activity(self,
                          action: str,
                          user_id: str) -> Dict[str, Any]:
        """Suit l'activité des utilisateurs"""
        dimensions = [
            {
                'Name': 'Action',
                'Value': action
            },
            {
                'Name': 'UserId',
                'Value': user_id
            }
        ]
        
        return self.put_metric(
            metric_name='UserActivity',
            value=1,
            unit='Count',
            dimensions=dimensions
        )
        
    def track_database_metrics(self,
                             operation: str,
                             latency: float,
                             success: bool) -> Dict[str, Any]:
        """Suit les métriques de la base de données"""
        dimensions = [
            {
                'Name': 'Operation',
                'Value': operation
            },
            {
                'Name': 'Status',
                'Value': 'Success' if success else 'Failure'
            }
        ]
        
        return self.put_metric(
            metric_name='DatabaseLatency',
            value=latency,
            unit='Milliseconds',
            dimensions=dimensions
        )
        
    def track_error_rate(self,
                        error_type: str,
                        count: int = 1) -> Dict[str, Any]:
        """Suit le taux d'erreurs"""
        dimensions = [
            {
                'Name': 'ErrorType',
                'Value': error_type
            }
        ]
        
        return self.put_metric(
            metric_name='ErrorCount',
            value=count,
            unit='Count',
            dimensions=dimensions
        )
        
    def track_business_metrics(self,
                             metric_type: str,
                             value: float) -> Dict[str, Any]:
        """Suit les métriques business"""
        dimensions = [
            {
                'Name': 'MetricType',
                'Value': metric_type
            }
        ]
        
        return self.put_metric(
            metric_name='BusinessMetrics',
            value=value,
            unit='None',
            dimensions=dimensions
        )
        
    def get_metric_statistics(self,
                            metric_name: str,
                            dimensions: List[Dict[str, str]],
                            start_time: datetime,
                            end_time: datetime,
                            period: int = 300,
                            statistics: List[str] = ['Average', 'Maximum', 'Minimum']) -> Dict[str, Any]:
        """Récupère les statistiques d'une métrique"""
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace=self.namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics
            )
            
            return {
                'status': 'success',
                'datapoints': response['Datapoints']
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def create_metric_alarm(self,
                          metric_name: str,
                          alarm_name: str,
                          threshold: float,
                          comparison_operator: str,
                          dimensions: List[Dict[str, str]],
                          evaluation_periods: int = 3,
                          period: int = 300) -> Dict[str, Any]:
        """Crée une alarme pour une métrique"""
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator=comparison_operator,
                EvaluationPeriods=evaluation_periods,
                MetricName=metric_name,
                Namespace=self.namespace,
                Period=period,
                Statistic='Average',
                Threshold=threshold,
                ActionsEnabled=True,
                AlarmDescription=f'Alarme pour {metric_name}',
                Dimensions=dimensions
            )
            
            return {
                'status': 'success',
                'message': f'Alarme créée pour {metric_name}'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de l'alarme: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Exemple de décorateur pour suivre automatiquement les métriques API
def track_api_metrics(endpoint_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics_manager = CustomMetricsManager()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to ms
                
                # Track successful API call
                metrics_manager.track_api_latency(
                    endpoint=endpoint_name,
                    latency=latency,
                    status_code=200
                )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                
                # Track failed API call
                metrics_manager.track_api_latency(
                    endpoint=endpoint_name,
                    latency=latency,
                    status_code=500
                )
                
                # Track error
                metrics_manager.track_error_rate(
                    error_type=type(e).__name__
                )
                
                raise
                
        return wrapper
    return decorator

if __name__ == "__main__":
    # Exemple d'utilisation
    metrics_manager = CustomMetricsManager()
    
    # Tracking API latency
    metrics_manager.track_api_latency(
        endpoint='/api/nutrition/calculate',
        latency=150.5,
        status_code=200
    )
    
    # Tracking user activity
    metrics_manager.track_user_activity(
        action='login',
        user_id='user123'
    )
    
    # Creating an alarm
    metrics_manager.create_metric_alarm(
        metric_name='APILatency',
        alarm_name='high-latency-alarm',
        threshold=1000.0,
        comparison_operator='GreaterThanThreshold',
        dimensions=[
            {
                'Name': 'Endpoint',
                'Value': '/api/nutrition/calculate'
            }
        ]
    )
