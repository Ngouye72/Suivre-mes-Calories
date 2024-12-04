import boto3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import requests
from dataclasses import dataclass

@dataclass
class BackupStatus:
    backup_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    size_bytes: int
    success: bool
    error_message: Optional[str]

class BackupMonitor:
    def __init__(self, 
                 bucket_name: str,
                 slack_webhook_url: Optional[str] = None,
                 region: str = 'eu-west-1'):
        self.bucket_name = bucket_name
        self.slack_webhook_url = slack_webhook_url
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def check_backup_status(self) -> List[BackupStatus]:
        """Vérifie le statut des backups récents"""
        try:
            # Liste des backups
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='backups/'
            )
            
            backup_statuses = []
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Récupération des metadata
                    head = self.s3.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
                    metadata = head.get('Metadata', {})
                    
                    status = BackupStatus(
                        backup_id=obj['Key'],
                        status='Completed',
                        start_time=metadata.get('start_time', obj['LastModified']),
                        end_time=obj['LastModified'],
                        size_bytes=obj['Size'],
                        success=True,
                        error_message=None
                    )
                    
                    backup_statuses.append(status)
                    
                    # Envoi des métriques CloudWatch
                    self._send_backup_metrics(status)
                    
                    # Notification Slack si configuré
                    if self.slack_webhook_url:
                        self._send_slack_notification(status)
            
            return backup_statuses
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des backups: {str(e)}")
            return []
            
    def _send_backup_metrics(self, status: BackupStatus):
        """Envoie les métriques de backup à CloudWatch"""
        try:
            # Métrique de taille
            self.cloudwatch.put_metric_data(
                Namespace='NutritionApp/Backups',
                MetricData=[
                    {
                        'MetricName': 'BackupSize',
                        'Value': status.size_bytes,
                        'Unit': 'Bytes',
                        'Timestamp': status.end_time
                    }
                ]
            )
            
            # Métrique de succès/échec
            self.cloudwatch.put_metric_data(
                Namespace='NutritionApp/Backups',
                MetricData=[
                    {
                        'MetricName': 'BackupSuccess',
                        'Value': 1 if status.success else 0,
                        'Unit': 'Count',
                        'Timestamp': status.end_time
                    }
                ]
            )
            
            # Métrique de durée
            if status.start_time and status.end_time:
                duration = (status.end_time - status.start_time).total_seconds()
                self.cloudwatch.put_metric_data(
                    Namespace='NutritionApp/Backups',
                    MetricData=[
                        {
                            'MetricName': 'BackupDuration',
                            'Value': duration,
                            'Unit': 'Seconds',
                            'Timestamp': status.end_time
                        }
                    ]
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi des métriques: {str(e)}")
            
    def _send_slack_notification(self, status: BackupStatus):
        """Envoie une notification Slack"""
        try:
            if not self.slack_webhook_url:
                return
                
            # Formatage du message
            message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📦 Statut du Backup"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*ID:*\n{status.backup_id}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{'✅ Succès' if status.success else '❌ Échec'}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Taille:*\n{self._format_size(status.size_bytes)}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Date:*\n{status.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # Ajout du message d'erreur si présent
            if status.error_message:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Erreur:*\n```{status.error_message}```"
                    }
                })
                
            # Envoi de la notification
            response = requests.post(
                self.slack_webhook_url,
                json=message
            )
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de la notification Slack: {str(e)}")
            
    def _format_size(self, size_bytes: int) -> str:
        """Formate la taille en format lisible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
        
    def create_backup_alarms(self):
        """Crée des alarmes pour les backups"""
        try:
            # Alarme pour backup manqué
            self.cloudwatch.put_metric_alarm(
                AlarmName='MissedBackupAlarm',
                ComparisonOperator='LessThanThreshold',
                EvaluationPeriods=1,
                MetricName='BackupSuccess',
                Namespace='NutritionApp/Backups',
                Period=86400,  # 24 heures
                Statistic='Sum',
                Threshold=1.0,
                ActionsEnabled=True,
                AlarmDescription='Alerte si aucun backup réussi dans les dernières 24h'
            )
            
            # Alarme pour durée excessive
            self.cloudwatch.put_metric_alarm(
                AlarmName='LongBackupDurationAlarm',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='BackupDuration',
                Namespace='NutritionApp/Backups',
                Period=3600,  # 1 heure
                Statistic='Maximum',
                Threshold=3600.0,  # 1 heure
                ActionsEnabled=True,
                AlarmDescription='Alerte si un backup prend plus d\'une heure'
            )
            
            # Alarme pour taille anormale
            self.cloudwatch.put_metric_alarm(
                AlarmName='AbnormalBackupSizeAlarm',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='BackupSize',
                Namespace='NutritionApp/Backups',
                Period=86400,
                Statistic='Maximum',
                Threshold=10 * 1024 * 1024 * 1024,  # 10 GB
                ActionsEnabled=True,
                AlarmDescription='Alerte si un backup dépasse 10 GB'
            )
            
            return {
                'status': 'success',
                'message': 'Alarmes créées avec succès'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création des alarmes: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

if __name__ == "__main__":
    # Exemple d'utilisation
    monitor = BackupMonitor(
        bucket_name='nutrition-app-backups',
        slack_webhook_url='https://hooks.slack.com/services/XXX/YYY/ZZZ'
    )
    
    # Vérification des backups
    statuses = monitor.check_backup_status()
    
    # Création des alarmes
    monitor.create_backup_alarms()
    
    # Affichage des résultats
    for status in statuses:
        print(f"Backup {status.backup_id}: {'✅' if status.success else '❌'}")
