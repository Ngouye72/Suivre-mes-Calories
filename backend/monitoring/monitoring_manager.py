from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import threading
import schedule
import time

from .health_metrics import HealthMetricsMonitor
from .goals_monitor import GoalsMonitor
from .behavior_monitor import BehaviorMonitor
from .quality_monitor import QualityMonitor
from .system_monitor import SystemMonitor
from .security_monitor import SecurityMonitor
from .api_monitor import APIMonitor
from .alert_manager import AlertManager
from .log_monitor import LogMonitor
from .performance_monitor import PerformanceMonitor
from .prediction_monitor import PredictionMonitor
from .test_monitor import TestMonitor

class MonitoringManager:
    def __init__(self):
        # Initialisation des composants
        self.health_monitor = HealthMetricsMonitor()
        self.goals_monitor = GoalsMonitor()
        self.behavior_monitor = BehaviorMonitor()
        self.quality_monitor = QualityMonitor()
        self.system_monitor = SystemMonitor()
        self.security_monitor = SecurityMonitor()
        self.api_monitor = APIMonitor()
        self.alert_manager = AlertManager()
        self.log_monitor = LogMonitor()
        self.performance_monitor = PerformanceMonitor()
        self.prediction_monitor = PredictionMonitor()
        self.test_monitor = TestMonitor()

        # Métriques globales
        self.global_health = Gauge(
            'nutrition_global_health',
            'Santé globale du système',
            ['component']
        )
        
        self.alert_status = Gauge(
            'nutrition_alert_status',
            'Statut des alertes',
            ['severity']
        )
        
        self.system_status = Gauge(
            'nutrition_system_status',
            'Statut du système',
            ['component']
        )

        self.logger = logging.getLogger(__name__)

        # Configuration du monitoring
        self.monitoring_config = {
            'metrics_port': 9090,
            'collection_interval': 60,  # secondes
            'retention_days': 30,
            'alert_threshold': 0.8
        }

    def start_monitoring(self):
        """Démarre tous les composants de monitoring"""
        try:
            # Démarrage serveur Prometheus
            start_http_server(self.monitoring_config['metrics_port'])
            
            # Démarrage collecte périodique
            self._start_periodic_collection()
            
            # Démarrage gestionnaire d'alertes
            self._start_alert_manager()
            
            self.logger.info("Monitoring system started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {str(e)}")
            raise

    def _start_periodic_collection(self):
        """Démarre la collecte périodique des métriques"""
        def run_periodic_tasks():
            while True:
                try:
                    self.collect_all_metrics()
                    self.analyze_system_health()
                    time.sleep(self.monitoring_config['collection_interval'])
                except Exception as e:
                    self.logger.error(f"Error in periodic collection: {str(e)}")

        collection_thread = threading.Thread(
            target=run_periodic_tasks,
            daemon=True
        )
        collection_thread.start()

    def _start_alert_manager(self):
        """Démarre le gestionnaire d'alertes"""
        def run_alert_manager():
            while True:
                try:
                    self.check_alerts()
                    time.sleep(30)  # Vérifie toutes les 30 secondes
                except Exception as e:
                    self.logger.error(f"Error in alert manager: {str(e)}")

        alert_thread = threading.Thread(
            target=run_alert_manager,
            daemon=True
        )
        alert_thread.start()

    def collect_all_metrics(self):
        """Collecte toutes les métriques"""
        try:
            metrics = {
                'health': self.health_monitor.collect_metrics(),
                'goals': self.goals_monitor.collect_metrics(),
                'behavior': self.behavior_monitor.collect_metrics(),
                'quality': self.quality_monitor.collect_metrics(),
                'system': self.system_monitor.collect_metrics(),
                'security': self.security_monitor.collect_metrics(),
                'api': self.api_monitor.collect_metrics(),
                'performance': self.performance_monitor.collect_metrics(),
                'prediction': self.prediction_monitor.collect_metrics(),
                'test': self.test_monitor.collect_metrics()
            }

            self._update_global_metrics(metrics)
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            return {}

    def _update_global_metrics(self, metrics: Dict):
        """Met à jour les métriques globales"""
        try:
            for component, component_metrics in metrics.items():
                # Calcul santé composant
                health_score = self._calculate_component_health(
                    component_metrics
                )
                self.global_health.labels(
                    component=component
                ).set(health_score)

                # Mise à jour statut
                self.system_status.labels(
                    component=component
                ).set(1 if health_score > 0.7 else 0)

        except Exception as e:
            self.logger.error(f"Error updating global metrics: {str(e)}")

    def _calculate_component_health(
        self,
        component_metrics: Dict
    ) -> float:
        """Calcule le score de santé d'un composant"""
        try:
            if not component_metrics:
                return 0.0

            # Exemple simple de calcul
            error_rate = component_metrics.get('error_rate', 0)
            performance = component_metrics.get('performance', 1)
            availability = component_metrics.get('availability', 1)

            health_score = (
                (1 - error_rate) * 0.4 +
                performance * 0.3 +
                availability * 0.3
            )

            return max(0.0, min(1.0, health_score))

        except Exception as e:
            self.logger.error(f"Error calculating health: {str(e)}")
            return 0.0

    def analyze_system_health(self) -> Dict:
        """Analyse la santé globale du système"""
        try:
            metrics = self.collect_all_metrics()
            
            health_analysis = {
                component: {
                    'health_score': self._calculate_component_health(
                        component_metrics
                    ),
                    'status': 'healthy' if self._calculate_component_health(
                        component_metrics
                    ) > 0.7 else 'degraded',
                    'metrics': component_metrics
                }
                for component, component_metrics in metrics.items()
            }

            return {
                'timestamp': datetime.now().isoformat(),
                'overall_health': sum(
                    analysis['health_score']
                    for analysis in health_analysis.values()
                ) / len(health_analysis),
                'component_health': health_analysis,
                'alerts': self.get_active_alerts(),
                'recommendations': self._generate_health_recommendations(
                    health_analysis
                )
            }

        except Exception as e:
            self.logger.error(f"Error analyzing health: {str(e)}")
            return {}

    def check_alerts(self):
        """Vérifie et gère les alertes"""
        try:
            # Collecte métriques
            metrics = self.collect_all_metrics()
            
            # Vérifie chaque composant
            for component, component_metrics in metrics.items():
                health_score = self._calculate_component_health(
                    component_metrics
                )
                
                if health_score < self.monitoring_config['alert_threshold']:
                    self.alert_manager.process_alerts([{
                        'type': 'health',
                        'component': component,
                        'severity': 'high' if health_score < 0.5 else 'medium',
                        'message': f"Component health degraded: {component}",
                        'value': health_score
                    }])

            # Met à jour statut alertes
            active_alerts = self.get_active_alerts()
            for severity in ['critical', 'high', 'medium', 'low']:
                count = len([
                    alert for alert in active_alerts
                    if alert['severity'] == severity
                ])
                self.alert_status.labels(severity=severity).set(count)

        except Exception as e:
            self.logger.error(f"Error checking alerts: {str(e)}")

    def get_active_alerts(self) -> List[Dict]:
        """Récupère les alertes actives"""
        try:
            return self.alert_manager._get_active_alerts()
        except Exception as e:
            self.logger.error(f"Error getting alerts: {str(e)}")
            return []

    def _generate_health_recommendations(
        self,
        health_analysis: Dict
    ) -> List[Dict]:
        """Génère des recommandations de santé"""
        recommendations = []
        try:
            # Analyse composants dégradés
            degraded_components = [
                component
                for component, analysis in health_analysis.items()
                if analysis['status'] == 'degraded'
            ]

            if degraded_components:
                recommendations.append({
                    "type": "health",
                    "priority": "high",
                    "message": "Améliorer santé composants",
                    "components": degraded_components,
                    "actions": [
                        "Investiguer causes",
                        "Optimiser performance",
                        "Réduire erreurs"
                    ]
                })

            # Analyse performance
            low_performance = [
                component
                for component, analysis in health_analysis.items()
                if analysis['metrics'].get('performance', 1) < 0.7
            ]

            if low_performance:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "message": "Optimiser performance",
                    "components": low_performance,
                    "actions": [
                        "Analyser bottlenecks",
                        "Optimiser ressources",
                        "Améliorer scalabilité"
                    ]
                })

            # Analyse disponibilité
            low_availability = [
                component
                for component, analysis in health_analysis.items()
                if analysis['metrics'].get('availability', 1) < 0.9
            ]

            if low_availability:
                recommendations.append({
                    "type": "availability",
                    "priority": "high",
                    "message": "Améliorer disponibilité",
                    "components": low_availability,
                    "actions": [
                        "Ajouter redondance",
                        "Améliorer résilience",
                        "Optimiser recovery"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Error generating recommendations: {str(e)}"
            )

        return recommendations

    def generate_monitoring_report(self) -> Dict:
        """Génère un rapport complet de monitoring"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "health_analysis": self.analyze_system_health(),
                "alerts": {
                    "active": self.get_active_alerts(),
                    "status": {
                        severity: self.alert_status.labels(
                            severity=severity
                        )._value.get()
                        for severity in ['critical', 'high', 'medium', 'low']
                    }
                },
                "metrics": self.collect_all_metrics(),
                "recommendations": self._generate_health_recommendations(
                    self.analyze_system_health()['component_health']
                )
            }
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {}

# Exemple d'utilisation:
"""
monitoring_manager = MonitoringManager()

# Démarrage monitoring
monitoring_manager.start_monitoring()

# Collecte métriques
metrics = monitoring_manager.collect_all_metrics()

# Analyse santé
health_analysis = monitoring_manager.analyze_system_health()

# Vérification alertes
monitoring_manager.check_alerts()

# Génération rapport
report = monitoring_manager.generate_monitoring_report()
"""
