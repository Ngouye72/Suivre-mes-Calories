import boto3
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class AutoScalingManager:
    def __init__(self, 
                 cluster_name: str,
                 service_name: str,
                 region: str = 'eu-west-1'):
        self.cluster_name = cluster_name
        self.service_name = service_name
        self.ecs = boto3.client('ecs', region_name=region)
        self.autoscaling = boto3.client('application-autoscaling', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_service_autoscaling(self,
                                min_capacity: int,
                                max_capacity: int,
                                target_cpu_utilization: float = 75.0,
                                target_memory_utilization: float = 75.0) -> Dict[str, Any]:
        """Configure l'auto-scaling pour un service ECS"""
        try:
            # Enregistrement de la cible de scaling
            resource_id = f"service/{self.cluster_name}/{self.service_name}"
            
            self.autoscaling.register_scalable_target(
                ServiceNamespace='ecs',
                ResourceId=resource_id,
                ScalableDimension='ecs:service:DesiredCount',
                MinCapacity=min_capacity,
                MaxCapacity=max_capacity
            )
            
            # Configuration des politiques de scaling basées sur CPU
            self.autoscaling.put_scaling_policy(
                PolicyName=f"{self.service_name}-cpu-scaling",
                ServiceNamespace='ecs',
                ResourceId=resource_id,
                ScalableDimension='ecs:service:DesiredCount',
                PolicyType='TargetTrackingScaling',
                TargetTrackingScalingPolicyConfiguration={
                    'TargetValue': target_cpu_utilization,
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ECSServiceAverageCPUUtilization'
                    },
                    'ScaleOutCooldown': 300,
                    'ScaleInCooldown': 300
                }
            )
            
            # Configuration des politiques de scaling basées sur la mémoire
            self.autoscaling.put_scaling_policy(
                PolicyName=f"{self.service_name}-memory-scaling",
                ServiceNamespace='ecs',
                ResourceId=resource_id,
                ScalableDimension='ecs:service:DesiredCount',
                PolicyType='TargetTrackingScaling',
                TargetTrackingScalingPolicyConfiguration={
                    'TargetValue': target_memory_utilization,
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ECSServiceAverageMemoryUtilization'
                    },
                    'ScaleOutCooldown': 300,
                    'ScaleInCooldown': 300
                }
            )
            
            return {
                'status': 'success',
                'message': 'Auto-scaling configuré avec succès',
                'config': {
                    'min_capacity': min_capacity,
                    'max_capacity': max_capacity,
                    'cpu_target': target_cpu_utilization,
                    'memory_target': target_memory_utilization
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration de l'auto-scaling: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def create_custom_metric_alarm(self,
                                 metric_name: str,
                                 threshold: float,
                                 comparison_operator: str,
                                 evaluation_periods: int = 3,
                                 period: int = 300) -> Dict[str, Any]:
        """Crée une alarme CloudWatch personnalisée"""
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.service_name}-{metric_name}",
                ComparisonOperator=comparison_operator,
                EvaluationPeriods=evaluation_periods,
                MetricName=metric_name,
                Namespace='NutritionApp',
                Period=period,
                Statistic='Average',
                Threshold=threshold,
                ActionsEnabled=True,
                AlarmDescription=f'Alarme pour {metric_name}',
                Dimensions=[
                    {
                        'Name': 'ClusterName',
                        'Value': self.cluster_name
                    },
                    {
                        'Name': 'ServiceName',
                        'Value': self.service_name
                    }
                ]
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
            
    def update_service_capacity(self,
                              desired_count: int) -> Dict[str, Any]:
        """Met à jour manuellement la capacité du service"""
        try:
            self.ecs.update_service(
                cluster=self.cluster_name,
                service=self.service_name,
                desiredCount=desired_count
            )
            
            return {
                'status': 'success',
                'message': f'Capacité mise à jour: {desired_count}'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la capacité: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def get_scaling_activities(self) -> List[Dict[str, Any]]:
        """Récupère l'historique des activités de scaling"""
        try:
            resource_id = f"service/{self.cluster_name}/{self.service_name}"
            
            response = self.autoscaling.describe_scaling_activities(
                ServiceNamespace='ecs',
                ResourceId=resource_id,
                MaxResults=100
            )
            
            return response.get('ScalingActivities', [])
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des activités: {str(e)}")
            return []
            
    def get_service_metrics(self,
                          start_time: datetime,
                          end_time: datetime) -> Dict[str, Any]:
        """Récupère les métriques du service"""
        try:
            metrics = {}
            
            # CPU Utilization
            cpu_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'ClusterName',
                        'Value': self.cluster_name
                    },
                    {
                        'Name': 'ServiceName',
                        'Value': self.service_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            metrics['cpu'] = cpu_response['Datapoints']
            
            # Memory Utilization
            memory_response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='MemoryUtilization',
                Dimensions=[
                    {
                        'Name': 'ClusterName',
                        'Value': self.cluster_name
                    },
                    {
                        'Name': 'ServiceName',
                        'Value': self.service_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            metrics['memory'] = memory_response['Datapoints']
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques: {str(e)}")
            return {}

if __name__ == "__main__":
    # Exemple d'utilisation
    scaling_manager = AutoScalingManager(
        cluster_name='nutrition-cluster',
        service_name='nutrition-api'
    )
    
    # Configuration de l'auto-scaling
    result = scaling_manager.setup_service_autoscaling(
        min_capacity=2,
        max_capacity=10,
        target_cpu_utilization=70.0,
        target_memory_utilization=70.0
    )
    
    print(json.dumps(result, indent=2))
