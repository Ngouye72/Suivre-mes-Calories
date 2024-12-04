import logging
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime
import threading
import time
import queue

class AlertSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your-email@gmail.com',
                'password': 'your-app-password',
                'from_email': 'your-email@gmail.com',
                'to_emails': ['admin@example.com']
            },
            'slack': {
                'enabled': True,
                'webhook_url': 'your-slack-webhook-url',
                'channel': '#monitoring-alerts'
            },
            'sms': {
                'enabled': True,
                'twilio_sid': 'your-twilio-sid',
                'twilio_token': 'your-twilio-token',
                'from_number': '+1234567890',
                'to_numbers': ['+0987654321']
            },
            'telegram': {
                'enabled': True,
                'bot_token': 'your-bot-token',
                'chat_ids': ['your-chat-id']
            }
        }
        
        # File d'attente d'alertes
        self.alert_queue = queue.Queue()
        
        # Historique des alertes
        self.alert_history = []
        
        # Démarrage worker
        self._start_alert_worker()

    def _start_alert_worker(self):
        """Démarre le worker de traitement des alertes"""
        def process_alerts():
            while True:
                try:
                    # Récupération alerte
                    alert = self.alert_queue.get()
                    
                    # Traitement alerte
                    self._process_alert(alert)
                    
                    # Marquage comme traitée
                    self.alert_queue.task_done()
                    
                except Exception as e:
                    self.logger.error(f"Error processing alert: {str(e)}")
                
                time.sleep(1)  # Évite surcharge

        # Démarrage thread
        worker_thread = threading.Thread(
            target=process_alerts,
            daemon=True
        )
        worker_thread.start()

    def add_alert(self, alert: Dict):
        """Ajoute une alerte à la file d'attente"""
        try:
            # Enrichissement alerte
            alert['timestamp'] = datetime.now().isoformat()
            alert['status'] = 'pending'
            
            # Ajout à la file
            self.alert_queue.put(alert)
            
            # Ajout à l'historique
            self.alert_history.append(alert)
            
            # Limite taille historique
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error adding alert: {str(e)}")

    def _process_alert(self, alert: Dict):
        """Traite une alerte"""
        try:
            # Préparation message
            message = self._format_alert_message(alert)
            
            # Envoi notifications selon sévérité
            if alert['severity'] == 'critical':
                self._send_all_notifications(message, alert)
            elif alert['severity'] == 'high':
                self._send_email_notification(message, alert)
                self._send_slack_notification(message, alert)
            else:
                self._send_slack_notification(message, alert)
            
            # Mise à jour statut
            alert['status'] = 'sent'
            
        except Exception as e:
            self.logger.error(f"Error processing alert: {str(e)}")
            alert['status'] = 'failed'
            alert['error'] = str(e)

    def _format_alert_message(self, alert: Dict) -> str:
        """Formate le message d'alerte"""
        try:
            return f"""
🚨 ALERT: {alert['title']}
Severity: {alert['severity']}
Component: {alert['component']}
Message: {alert['message']}
Timestamp: {alert['timestamp']}
Details: {json.dumps(alert.get('details', {}), indent=2)}
"""
        except Exception as e:
            self.logger.error(f"Error formatting alert: {str(e)}")
            return str(alert)

    def _send_all_notifications(self, message: str, alert: Dict):
        """Envoie l'alerte sur tous les canaux"""
        try:
            self._send_email_notification(message, alert)
            self._send_slack_notification(message, alert)
            self._send_sms_notification(message, alert)
            self._send_telegram_notification(message, alert)
        except Exception as e:
            self.logger.error(f"Error sending all notifications: {str(e)}")

    def _send_email_notification(self, message: str, alert: Dict):
        """Envoie une notification par email"""
        if not self.config['email']['enabled']:
            return

        try:
            # Création message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = ', '.join(self.config['email']['to_emails'])
            msg['Subject'] = f"[{alert['severity'].upper()}] {alert['title']}"
            
            # Ajout contenu
            msg.attach(MIMEText(message, 'plain'))
            
            # Connexion SMTP
            with smtplib.SMTP(
                self.config['email']['smtp_server'],
                self.config['email']['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.config['email']['username'],
                    self.config['email']['password']
                )
                server.send_message(msg)
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            raise

    def _send_slack_notification(self, message: str, alert: Dict):
        """Envoie une notification Slack"""
        if not self.config['slack']['enabled']:
            return

        try:
            # Préparation payload
            payload = {
                'channel': self.config['slack']['channel'],
                'text': message,
                'attachments': [{
                    'color': self._get_alert_color(alert['severity']),
                    'fields': [
                        {
                            'title': key,
                            'value': str(value),
                            'short': True
                        }
                        for key, value in alert.get('details', {}).items()
                    ]
                }]
            }
            
            # Envoi requête
            response = requests.post(
                self.config['slack']['webhook_url'],
                json=payload
            )
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {str(e)}")
            raise

    def _send_sms_notification(self, message: str, alert: Dict):
        """Envoie une notification SMS via Twilio"""
        if not self.config['sms']['enabled']:
            return

        try:
            from twilio.rest import Client
            
            # Création client
            client = Client(
                self.config['sms']['twilio_sid'],
                self.config['sms']['twilio_token']
            )
            
            # Envoi SMS
            for number in self.config['sms']['to_numbers']:
                client.messages.create(
                    body=message,
                    from_=self.config['sms']['from_number'],
                    to=number
                )
                
        except Exception as e:
            self.logger.error(f"Error sending SMS: {str(e)}")
            raise

    def _send_telegram_notification(self, message: str, alert: Dict):
        """Envoie une notification Telegram"""
        if not self.config['telegram']['enabled']:
            return

        try:
            # URL API
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
            
            # Envoi message
            for chat_id in self.config['telegram']['chat_ids']:
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, json=payload)
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {str(e)}")
            raise

    def _get_alert_color(self, severity: str) -> str:
        """Retourne la couleur selon la sévérité"""
        return {
            'critical': '#FF0000',
            'high': '#FFA500',
            'medium': '#FFFF00',
            'low': '#00FF00'
        }.get(severity, '#808080')

    def get_active_alerts(self) -> List[Dict]:
        """Récupère les alertes actives"""
        return [
            alert for alert in self.alert_history
            if alert['status'] == 'pending'
        ]

    def get_alert_history(
        self,
        severity: Optional[str] = None,
        component: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Récupère l'historique des alertes avec filtres"""
        alerts = self.alert_history

        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
            
        if component:
            alerts = [a for a in alerts if a['component'] == component]
            
        return alerts[-limit:]

# Exemple d'utilisation:
"""
alert_system = AlertSystem()

# Création alerte
alert = {
    'title': 'High CPU Usage',
    'severity': 'critical',
    'component': 'web-server',
    'message': 'CPU usage above 90%',
    'details': {
        'cpu_usage': '95%',
        'process': 'nginx',
        'host': 'web-1'
    }
}

# Ajout alerte
alert_system.add_alert(alert)

# Récupération alertes
active_alerts = alert_system.get_active_alerts()
alert_history = alert_system.get_alert_history(severity='critical')
"""
