import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
import traceback
import sys
import pkg_resources
import requests
from datetime import datetime
import json

class ErrorMonitor:
    def __init__(self, environment: str = "production"):
        # Configuration Sentry
        sentry_sdk.init(
            dsn="your-sentry-dsn",
            environment=environment,
            traces_sample_rate=1.0,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration()
            ],
            before_send=self._before_send
        )

        # Métriques Prometheus
        self.error_counter = Counter(
            'nutrition_app_errors_total',
            'Nombre total d\'erreurs',
            ['error_type', 'component']
        )
        
        self.error_severity = Counter(
            'nutrition_error_severity_total',
            'Distribution des erreurs par sévérité',
            ['severity']
        )
        
        self.dependency_health = Gauge(
            'nutrition_dependency_health',
            'Santé des dépendances',
            ['dependency', 'version']
        )
        
        self.error_resolution_time = Histogram(
            'nutrition_error_resolution_time_seconds',
            'Temps de résolution des erreurs',
            ['error_type']
        )

        self.logger = logging.getLogger(__name__)
        self.known_issues = set()
        self.dependency_versions = self._get_dependency_versions()

    def _before_send(self, event: Dict, hint: Dict) -> Optional[Dict]:
        """Prétraitement des événements Sentry"""
        try:
            # Filtrage des données sensibles
            if 'request' in event:
                if 'headers' in event['request']:
                    sensitive_headers = ['Authorization', 'Cookie']
                    for header in sensitive_headers:
                        if header in event['request']['headers']:
                            event['request']['headers'][header] = '[FILTERED]'

                if 'data' in event['request']:
                    sensitive_fields = ['password', 'token', 'api_key']
                    for field in sensitive_fields:
                        if field in event['request']['data']:
                            event['request']['data'][field] = '[FILTERED]'

            # Enrichissement des données
            if 'extra' not in event:
                event['extra'] = {}
            
            event['extra']['dependency_versions'] = self.dependency_versions
            
            return event
        except Exception as e:
            self.logger.error(f"Erreur lors du prétraitement Sentry: {str(e)}")
            return event

    def _get_dependency_versions(self) -> Dict[str, str]:
        """Récupère les versions des dépendances"""
        try:
            return {
                pkg.key: pkg.version
                for pkg in pkg_resources.working_set
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des versions: {str(e)}")
            return {}

    def track_error(self, error: Exception, component: str, severity: str = "error"):
        """Suit une erreur"""
        try:
            error_type = type(error).__name__
            
            # Incrémentation des compteurs
            self.error_counter.labels(
                error_type=error_type,
                component=component
            ).inc()
            
            self.error_severity.labels(severity=severity).inc()

            # Capture dans Sentry
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("component", component)
                scope.set_tag("severity", severity)
                scope.set_extra("error_details", {
                    "traceback": traceback.format_exc(),
                    "component": component,
                    "timestamp": datetime.now().isoformat()
                })
                sentry_sdk.capture_exception(error)

            # Logging local
            self.logger.error(
                f"Erreur dans {component}: {str(error)}",
                extra={
                    "error_type": error_type,
                    "severity": severity,
                    "traceback": traceback.format_exc()
                }
            )
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi d'erreur: {str(e)}")

    def check_dependencies(self) -> List[Dict]:
        """Vérifie l'état des dépendances"""
        try:
            issues = []
            for pkg_name, current_version in self.dependency_versions.items():
                try:
                    # Vérification des versions PyPI
                    response = requests.get(
                        f"https://pypi.org/pypi/{pkg_name}/json"
                    )
                    if response.status_code == 200:
                        pypi_data = response.json()
                        latest_version = pypi_data["info"]["version"]
                        
                        # Mise à jour de la métrique
                        self.dependency_health.labels(
                            dependency=pkg_name,
                            version=current_version
                        ).set(1 if current_version == latest_version else 0)
                        
                        if current_version != latest_version:
                            issues.append({
                                "package": pkg_name,
                                "current_version": current_version,
                                "latest_version": latest_version,
                                "type": "outdated"
                            })
                            
                        # Vérification des vulnérabilités
                        if "vulnerabilities" in pypi_data:
                            for vuln in pypi_data["vulnerabilities"]:
                                issues.append({
                                    "package": pkg_name,
                                    "type": "vulnerability",
                                    "details": vuln
                                })
                except Exception as e:
                    self.logger.warning(
                        f"Erreur lors de la vérification de {pkg_name}: {str(e)}"
                    )
                    
            return issues
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des dépendances: {str(e)}")
            return []

    def analyze_error_patterns(self, timeframe_hours: int = 24) -> Dict:
        """Analyse les patterns d'erreurs"""
        try:
            # Récupération des événements Sentry
            events = sentry_sdk.Hub.current.client.events
            
            patterns = {
                "frequent_errors": [],
                "error_spikes": [],
                "correlated_errors": []
            }
            
            # Analyse de fréquence
            error_counts = {}
            for event in events:
                error_type = event.get("type", "unknown")
                if error_type in error_counts:
                    error_counts[error_type] += 1
                else:
                    error_counts[error_type] = 1
            
            # Identification des erreurs fréquentes
            for error_type, count in error_counts.items():
                if count > 10:  # Seuil arbitraire
                    patterns["frequent_errors"].append({
                        "type": error_type,
                        "count": count
                    })
            
            return patterns
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des patterns: {str(e)}")
            return {}

    def generate_error_report(self) -> Dict:
        """Génère un rapport d'erreurs"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "error_metrics": {
                    "total_errors": self.error_counter._value.get(),
                    "error_severity": self.error_severity._value.get(),
                    "resolution_times": self.error_resolution_time._value.get()
                },
                "dependency_status": {
                    "versions": self.dependency_versions,
                    "issues": self.check_dependencies()
                },
                "error_patterns": self.analyze_error_patterns(),
                "recommendations": self._generate_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les erreurs"""
        recommendations = []
        
        # Analyse des erreurs fréquentes
        if self.error_counter._value.get() > 100:
            recommendations.append(
                "Volume d'erreurs élevé - Examiner les patterns d'erreurs"
            )
        
        # Analyse des dépendances
        dependency_issues = self.check_dependencies()
        if dependency_issues:
            recommendations.append(
                f"Mettre à jour {len(dependency_issues)} dépendances obsolètes"
            )
        
        return recommendations

# Exemple d'utilisation:
"""
error_monitor = ErrorMonitor()

# Suivi d'erreur
try:
    # Code qui peut générer une erreur
    raise ValueError("Données invalides")
except Exception as e:
    error_monitor.track_error(e, "data_validation", "error")

# Vérification des dépendances
issues = error_monitor.check_dependencies()

# Analyse des patterns
patterns = error_monitor.analyze_error_patterns()

# Génération rapport
report = error_monitor.generate_error_report()
"""
