import boto3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import jinja2
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.s3 = boto3.client('s3')
        self.template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        self.template_env = jinja2.Environment(loader=self.template_loader)
        
    def get_metric_data(self, metric_name: str, dimensions: List[Dict], 
                       start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Récupère les données métriques de CloudWatch"""
        try:
            response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'data',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'NutritionApp',
                                'MetricName': metric_name,
                                'Dimensions': dimensions
                            },
                            'Period': 3600,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            timestamps = response['MetricDataResults'][0]['Timestamps']
            values = response['MetricDataResults'][0]['Values']
            
            return pd.DataFrame({
                'timestamp': timestamps,
                'value': values
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques: {e}")
            return pd.DataFrame()
    
    def create_usage_chart(self, data: pd.DataFrame) -> str:
        """Crée un graphique d'utilisation avec Plotly"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['value'],
            mode='lines+markers',
            name='Usage'
        ))
        
        fig.update_layout(
            title='Utilisation de l\'application',
            xaxis_title='Date',
            yaxis_title='Nombre d\'utilisations'
        )
        
        return fig.to_html(full_html=False)
    
    def generate_daily_report(self) -> str:
        """Génère le rapport quotidien"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        # Récupération des métriques
        api_calls = self.get_metric_data(
            'ApiCall',
            [{'Name': 'StatusCode', 'Value': '200'}],
            start_time,
            end_time
        )
        
        errors = self.get_metric_data(
            'Error',
            [],
            start_time,
            end_time
        )
        
        meal_entries = self.get_metric_data(
            'MealCalories',
            [],
            start_time,
            end_time
        )
        
        # Création des graphiques
        api_chart = self.create_usage_chart(api_calls)
        error_chart = self.create_usage_chart(errors)
        meal_chart = self.create_usage_chart(meal_entries)
        
        # Calcul des statistiques
        stats = {
            'total_api_calls': api_calls['value'].sum(),
            'total_errors': errors['value'].sum(),
            'total_meals': meal_entries['value'].count(),
            'avg_calories': meal_entries['value'].mean() if not meal_entries.empty else 0
        }
        
        # Génération du rapport HTML
        template = self.template_env.get_template('daily_report.html')
        return template.render(
            date=end_time.strftime('%Y-%m-%d'),
            stats=stats,
            api_chart=api_chart,
            error_chart=error_chart,
            meal_chart=meal_chart
        )
    
    def save_report(self, html_content: str, report_type: str):
        """Sauvegarde le rapport dans S3"""
        try:
            date_str = datetime.utcnow().strftime('%Y-%m-%d')
            key = f'reports/{report_type}/{date_str}.html'
            
            self.s3.put_object(
                Bucket='nutrition-app-reports',
                Key=key,
                Body=html_content,
                ContentType='text/html'
            )
            
            # Génère une URL signée pour accéder au rapport
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'nutrition-app-reports',
                    'Key': key
                },
                ExpiresIn=604800  # 7 jours
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            return None

    def send_report_notification(self, report_url: str):
        """Envoie une notification avec le lien du rapport"""
        sns = boto3.client('sns')
        try:
            sns.publish(
                TopicArn=os.environ['REPORT_SNS_TOPIC'],
                Subject='Rapport quotidien disponible',
                Message=f'Le rapport quotidien est disponible ici: {report_url}'
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification: {e}")

# Exemple d'utilisation:
"""
if __name__ == '__main__':
    generator = ReportGenerator()
    report_content = generator.generate_daily_report()
    report_url = generator.save_report(report_content, 'daily')
    if report_url:
        generator.send_report_notification(report_url)
"""
