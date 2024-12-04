from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from prometheus_client import Counter, Gauge

class AlertManager:
    def __init__(self):
        # Métriques d'alertes
        self.alert_count = Counter(
            'nutrition_alert_total',
            'Nombre total d\'alertes',
            ['alert_type', 'severity']
        )
        
        self.active_alerts = Gauge(
            'nutrition_active_alerts',
            'Alertes actives',
            ['alert_type']
        )
        
        # Configuration
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'error_rate': 0.05,
            'response_time': 1.0,
            'disk_usage': 90.0
        }
        
        self.severity_levels = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }

        self.logger = logging.getLogger(__name__)

    def check_system_metrics(
        self,
        metrics: Dict[str, float]
    ) -> List[Dict]:
        """Vérifie les métriques système"""
        alerts = []
        try:
            # CPU
            if metrics.get('cpu_usage', 0) > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'system',
                    'subtype': 'cpu',
                    'severity': 'high',
                    'message': f"CPU usage high: {metrics['cpu_usage']}%",
                    'value': metrics['cpu_usage']
                })

            # Mémoire
            if metrics.get('memory_usage', 0) > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'system',
                    'subtype': 'memory',
                    'severity': 'high',
                    'message': f"Memory usage high: {metrics['memory_usage']}%",
                    'value': metrics['memory_usage']
                })

            # Disque
            if metrics.get('disk_usage', 0) > self.alert_thresholds['disk_usage']:
                alerts.append({
                    'type': 'system',
                    'subtype': 'disk',
                    'severity': 'medium',
                    'message': f"Disk usage high: {metrics['disk_usage']}%",
                    'value': metrics['disk_usage']
                })

        except Exception as e:
            self.logger.error(f"Erreur vérification système: {str(e)}")

        return alerts

    def check_application_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> List[Dict]:
        """Vérifie les métriques application"""
        alerts = []
        try:
            # Taux d'erreur
            if metrics.get('error_rate', 0) > self.alert_thresholds['error_rate']:
                alerts.append({
                    'type': 'application',
                    'subtype': 'errors',
                    'severity': 'critical',
                    'message': f"High error rate: {metrics['error_rate']}",
                    'value': metrics['error_rate']
                })

            # Temps de réponse
            if metrics.get('response_time', 0) > self.alert_thresholds['response_time']:
                alerts.append({
                    'type': 'application',
                    'subtype': 'performance',
                    'severity': 'high',
                    'message': f"Slow response time: {metrics['response_time']}s",
                    'value': metrics['response_time']
                })

        except Exception as e:
            self.logger.error(f"Erreur vérification application: {str(e)}")

        return alerts

    def check_security_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> List[Dict]:
        """Vérifie les métriques sécurité"""
        alerts = []
        try:
            # Tentatives auth
            if metrics.get('failed_auth_attempts', 0) > 10:
                alerts.append({
                    'type': 'security',
                    'subtype': 'authentication',
                    'severity': 'critical',
                    'message': "Multiple failed auth attempts detected",
                    'value': metrics['failed_auth_attempts']
                })

            # Exposition PII
            if metrics.get('pii_exposure', False):
                alerts.append({
                    'type': 'security',
                    'subtype': 'privacy',
                    'severity': 'critical',
                    'message': "PII exposure detected",
                    'value': True
                })

        except Exception as e:
            self.logger.error(f"Erreur vérification sécurité: {str(e)}")

        return alerts

    def process_alerts(
        self,
        alerts: List[Dict]
    ):
        """Traite les alertes"""
        try:
            for alert in alerts:
                # Incrémente compteur
                self.alert_count.labels(
                    alert_type=alert['type'],
                    severity=alert['severity']
                ).inc()

                # Met à jour alertes actives
                self.active_alerts.labels(
                    alert_type=alert['type']
                ).inc()

                # Envoie notifications
                self._send_notifications(alert)

                # Log alerte
                self._log_alert(alert)

        except Exception as e:
            self.logger.error(f"Erreur traitement alertes: {str(e)}")

    def _send_notifications(
        self,
        alert: Dict
    ):
        """Envoie les notifications"""
        try:
            # Email
            if alert['severity'] in ['critical', 'high']:
                self._send_email_alert(alert)

            # Slack
            if alert['severity'] != 'low':
                self._send_slack_alert(alert)

            # SMS
            if alert['severity'] == 'critical':
                self._send_sms_alert(alert)

        except Exception as e:
            self.logger.error(f"Erreur envoi notifications: {str(e)}")

    def _send_email_alert(
        self,
        alert: Dict
    ):
        """Envoie alerte par email"""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"Alert: {alert['type']} - {alert['severity']}"
            msg['From'] = "monitoring@nutrition-app.com"
            msg['To'] = "admin@nutrition-app.com"

            body = f"""
            Alert Details:
            Type: {alert['type']}
            Subtype: {alert['subtype']}
            Severity: {alert['severity']}
            Message: {alert['message']}
            Value: {alert['value']}
            Timestamp: {datetime.now().isoformat()}
            """

            msg.attach(MIMEText(body, 'plain'))

            # Configuration SMTP à implémenter
            """
            with smtplib.SMTP('smtp.server.com', 587) as server:
                server.starttls()
                server.login('user', 'password')
                server.send_message(msg)
            """

        except Exception as e:
            self.logger.error(f"Erreur envoi email: {str(e)}")

    def _send_slack_alert(
        self,
        alert: Dict
    ):
        """Envoie alerte sur Slack"""
        try:
            message = {
                "text": f"*Alert: {alert['type']} - {alert['severity']}*\n"
                       f"Subtype: {alert['subtype']}\n"
                       f"Message: {alert['message']}\n"
                       f"Value: {alert['value']}"
            }

            # Configuration Slack à implémenter
            """
            webhook_url = "https://hooks.slack.com/services/xxx/yyy/zzz"
            requests.post(webhook_url, json=message)
            """

        except Exception as e:
            self.logger.error(f"Erreur envoi Slack: {str(e)}")

    def _send_sms_alert(
        self,
        alert: Dict
    ):
        """Envoie alerte par SMS"""
        try:
            message = (
                f"CRITICAL ALERT: {alert['type']}\n"
                f"{alert['message']}"
            )

            # Configuration SMS à implémenter
            """
            twilio_client = Client(account_sid, auth_token)
            message = twilio_client.messages.create(
                body=message,
                from_='+1234567890',
                to='+0987654321'
            )
            """

        except Exception as e:
            self.logger.error(f"Erreur envoi SMS: {str(e)}")

    def _log_alert(
        self,
        alert: Dict
    ):
        """Log l'alerte"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "alert": alert
            }
            
            self.logger.warning(
                f"Alert triggered: {json.dumps(log_entry, indent=2)}"
            )

        except Exception as e:
            self.logger.error(f"Erreur logging alerte: {str(e)}")

    def analyze_alerts(
        self,
        timeframe_hours: int = 24
    ) -> Dict:
        """Analyse les alertes"""
        try:
            return {
                "count_by_type": {
                    alert_type: self.alert_count.labels(
                        alert_type=alert_type,
                        severity='ALL'
                    )._value.get()
                    for alert_type in ['system', 'application', 'security']
                },
                "count_by_severity": {
                    severity: self.alert_count.labels(
                        alert_type='ALL',
                        severity=severity
                    )._value.get()
                    for severity in ['critical', 'high', 'medium', 'low']
                },
                "active_alerts": {
                    alert_type: self.active_alerts.labels(
                        alert_type=alert_type
                    )._value.get()
                    for alert_type in ['system', 'application', 'security']
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse alertes: {str(e)}")
            return {}

    def generate_alert_report(self) -> Dict:
        """Génère un rapport d'alertes"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "alert_analysis": self.analyze_alerts(),
                "active_alerts": self._get_active_alerts(),
                "recommendations": self._generate_alert_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _get_active_alerts(self) -> List[Dict]:
        """Récupère les alertes actives"""
        active_alerts = []
        try:
            for alert_type in ['system', 'application', 'security']:
                count = self.active_alerts.labels(
                    alert_type=alert_type
                )._value.get()
                if count > 0:
                    active_alerts.append({
                        "type": alert_type,
                        "count": count
                    })
        except Exception as e:
            self.logger.error(f"Erreur récupération alertes: {str(e)}")

        return active_alerts

    def _generate_alert_recommendations(self) -> List[Dict]:
        """Génère des recommandations"""
        recommendations = []
        try:
            alert_analysis = self.analyze_alerts()

            # Recommandations système
            if alert_analysis["count_by_type"].get("system", 0) > 10:
                recommendations.append({
                    "type": "system",
                    "priority": "high",
                    "message": "Optimiser les ressources système",
                    "actions": [
                        "Augmenter les ressources",
                        "Optimiser l'utilisation",
                        "Mettre en place de l'auto-scaling"
                    ]
                })

            # Recommandations application
            if alert_analysis["count_by_type"].get("application", 0) > 5:
                recommendations.append({
                    "type": "application",
                    "priority": "high",
                    "message": "Améliorer la stabilité application",
                    "actions": [
                        "Optimiser le code",
                        "Améliorer la gestion d'erreurs",
                        "Mettre en place du monitoring détaillé"
                    ]
                })

            # Recommandations sécurité
            if alert_analysis["count_by_type"].get("security", 0) > 0:
                recommendations.append({
                    "type": "security",
                    "priority": "critical",
                    "message": "Renforcer la sécurité",
                    "actions": [
                        "Audit de sécurité",
                        "Mise à jour des systèmes",
                        "Formation équipe"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
alert_manager = AlertManager()

# Vérification métriques système
system_metrics = {
    'cpu_usage': 85.0,
    'memory_usage': 90.0,
    'disk_usage': 95.0
}
system_alerts = alert_manager.check_system_metrics(system_metrics)

# Vérification métriques application
app_metrics = {
    'error_rate': 0.06,
    'response_time': 1.5
}
app_alerts = alert_manager.check_application_metrics(app_metrics)

# Vérification métriques sécurité
security_metrics = {
    'failed_auth_attempts': 15,
    'pii_exposure': True
}
security_alerts = alert_manager.check_security_metrics(security_metrics)

# Traitement des alertes
all_alerts = system_alerts + app_alerts + security_alerts
alert_manager.process_alerts(all_alerts)

# Analyse des alertes
alert_analysis = alert_manager.analyze_alerts()

# Génération rapport
report = alert_manager.generate_alert_report()
"""
