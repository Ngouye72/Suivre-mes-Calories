import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass
class UserMetrics:
    total_users: int
    active_users: int
    new_users: int
    retention_rate: float
    average_session_duration: float

@dataclass
class NutritionMetrics:
    total_meals_logged: int
    average_calories_per_day: float
    users_meeting_goals: int
    most_common_foods: List[str]
    average_weight_change: float

class BusinessMetricsManager:
    def __init__(self, region: str = 'eu-west-1'):
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.namespace = 'NutritionApp/Business'
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def track_user_metrics(self, metrics: UserMetrics):
        """Enregistre les métriques utilisateurs"""
        try:
            metric_data = [
                {
                    'MetricName': 'TotalUsers',
                    'Value': metrics.total_users,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'ActiveUsers',
                    'Value': metrics.active_users,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'NewUsers',
                    'Value': metrics.new_users,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'RetentionRate',
                    'Value': metrics.retention_rate,
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'AverageSessionDuration',
                    'Value': metrics.average_session_duration,
                    'Unit': 'Seconds'
                }
            ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=metric_data
            )
            
            return {
                'status': 'success',
                'message': 'Métriques utilisateurs enregistrées'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des métriques utilisateurs: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def track_nutrition_metrics(self, metrics: NutritionMetrics):
        """Enregistre les métriques nutritionnelles"""
        try:
            metric_data = [
                {
                    'MetricName': 'TotalMealsLogged',
                    'Value': metrics.total_meals_logged,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'AverageCaloriesPerDay',
                    'Value': metrics.average_calories_per_day,
                    'Unit': 'None'
                },
                {
                    'MetricName': 'UsersMeetingGoals',
                    'Value': metrics.users_meeting_goals,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'AverageWeightChange',
                    'Value': metrics.average_weight_change,
                    'Unit': 'None'
                }
            ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=metric_data
            )
            
            # Enregistrement des aliments les plus communs
            for i, food in enumerate(metrics.most_common_foods[:5]):
                self.cloudwatch.put_metric_data(
                    Namespace=f"{self.namespace}/Foods",
                    MetricData=[{
                        'MetricName': f"CommonFood{i+1}",
                        'Value': 1,
                        'Unit': 'None',
                        'Dimensions': [{'Name': 'FoodName', 'Value': food}]
                    }]
                )
            
            return {
                'status': 'success',
                'message': 'Métriques nutritionnelles enregistrées'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des métriques nutritionnelles: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def calculate_user_engagement(self, days: int = 30) -> Dict[str, Any]:
        """Calcule les métriques d'engagement utilisateur"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Récupération des données
            response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'activeUsers',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': self.namespace,
                                'MetricName': 'ActiveUsers'
                            },
                            'Period': 86400,
                            'Stat': 'Average'
                        }
                    },
                    {
                        'Id': 'totalUsers',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': self.namespace,
                                'MetricName': 'TotalUsers'
                            },
                            'Period': 86400,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            # Analyse avec pandas
            df_active = pd.DataFrame({
                'timestamp': response['MetricDataResults'][0]['Timestamps'],
                'active_users': response['MetricDataResults'][0]['Values']
            })
            
            df_total = pd.DataFrame({
                'timestamp': response['MetricDataResults'][1]['Timestamps'],
                'total_users': response['MetricDataResults'][1]['Values']
            })
            
            # Calcul des métriques
            engagement_rate = (df_active['active_users'].mean() / df_total['total_users'].mean()) * 100
            trend = np.polyfit(range(len(df_active)), df_active['active_users'], 1)[0]
            
            return {
                'engagement_rate': engagement_rate,
                'trend': trend,
                'peak_active_users': df_active['active_users'].max(),
                'average_active_users': df_active['active_users'].mean()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de l'engagement: {str(e)}")
            return {}
            
    def calculate_nutrition_insights(self, days: int = 30) -> Dict[str, Any]:
        """Calcule les insights nutritionnels"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Récupération des données
            response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'calories',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': self.namespace,
                                'MetricName': 'AverageCaloriesPerDay'
                            },
                            'Period': 86400,
                            'Stat': 'Average'
                        }
                    },
                    {
                        'Id': 'weightChange',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': self.namespace,
                                'MetricName': 'AverageWeightChange'
                            },
                            'Period': 86400,
                            'Stat': 'Average'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            # Analyse avec pandas
            df_calories = pd.DataFrame({
                'timestamp': response['MetricDataResults'][0]['Timestamps'],
                'calories': response['MetricDataResults'][0]['Values']
            })
            
            df_weight = pd.DataFrame({
                'timestamp': response['MetricDataResults'][1]['Timestamps'],
                'weight_change': response['MetricDataResults'][1]['Values']
            })
            
            # Calcul des insights
            calories_trend = np.polyfit(range(len(df_calories)), df_calories['calories'], 1)[0]
            weight_trend = np.polyfit(range(len(df_weight)), df_weight['weight_change'], 1)[0]
            
            return {
                'average_daily_calories': df_calories['calories'].mean(),
                'calories_trend': calories_trend,
                'total_weight_change': df_weight['weight_change'].sum(),
                'weight_trend': weight_trend
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des insights: {str(e)}")
            return {}

if __name__ == "__main__":
    # Exemple d'utilisation
    metrics_manager = BusinessMetricsManager()
    
    # Enregistrement des métriques utilisateurs
    user_metrics = UserMetrics(
        total_users=1000,
        active_users=750,
        new_users=50,
        retention_rate=85.5,
        average_session_duration=1200
    )
    metrics_manager.track_user_metrics(user_metrics)
    
    # Enregistrement des métriques nutritionnelles
    nutrition_metrics = NutritionMetrics(
        total_meals_logged=5000,
        average_calories_per_day=2100.5,
        users_meeting_goals=600,
        most_common_foods=['Poulet', 'Riz', 'Salade', 'Yaourt', 'Banane'],
        average_weight_change=-0.5
    )
    metrics_manager.track_nutrition_metrics(nutrition_metrics)
    
    # Calcul des insights
    engagement = metrics_manager.calculate_user_engagement()
    nutrition = metrics_manager.calculate_nutrition_insights()
    
    print("Engagement:", engagement)
    print("Nutrition:", nutrition)
