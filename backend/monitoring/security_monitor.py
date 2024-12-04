from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import hashlib
import re
import jwt
from cryptography.fernet import Fernet
import numpy as np

class SecurityMonitor:
    def __init__(self):
        # Métriques d'authentification
        self.auth_attempts = Counter(
            'nutrition_auth_attempts_total',
            'Tentatives d\'authentification',
            ['status']
        )
        
        self.active_sessions = Gauge(
            'nutrition_active_sessions',
            'Sessions actives',
            ['user_type']
        )
        
        # Métriques de sécurité
        self.security_incidents = Counter(
            'nutrition_security_incidents_total',
            'Incidents de sécurité',
            ['incident_type']
        )
        
        self.vulnerability_score = Gauge(
            'nutrition_vulnerability_score',
            'Score de vulnérabilité',
            ['component']
        )
        
        # Métriques de confidentialité
        self.data_access = Counter(
            'nutrition_data_access_total',
            'Accès aux données',
            ['data_type', 'access_type']
        )
        
        self.pii_exposure = Counter(
            'nutrition_pii_exposure_total',
            'Exposition PII',
            ['data_type']
        )
        
        # Métriques de conformité
        self.gdpr_compliance = Gauge(
            'nutrition_gdpr_compliance',
            'Conformité GDPR',
            ['requirement']
        )
        
        self.data_retention = Gauge(
            'nutrition_data_retention',
            'Rétention des données',
            ['data_type']
        )

        self.logger = logging.getLogger(__name__)
        
        # Patterns pour la détection PII
        self.pii_patterns = {
            'email': r'[^@]+@[^@]+\.[^@]+',
            'phone': r'\b\d{10}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }

    def monitor_authentication(
        self,
        user_id: str,
        success: bool,
        user_type: str = 'standard'
    ):
        """Surveille les tentatives d'authentification"""
        try:
            status = 'success' if success else 'failure'
            self.auth_attempts.labels(status=status).inc()
            
            if success:
                self.active_sessions.labels(
                    user_type=user_type
                ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur monitoring auth: {str(e)}")

    def monitor_security_incident(
        self,
        incident_type: str,
        severity: str,
        details: Dict
    ):
        """Surveille les incidents de sécurité"""
        try:
            self.security_incidents.labels(
                incident_type=incident_type
            ).inc()
            
            # Mise à jour du score de vulnérabilité
            severity_score = {
                'low': 0.3,
                'medium': 0.6,
                'high': 1.0
            }.get(severity, 0.5)
            
            self.vulnerability_score.labels(
                component=details.get('component', 'unknown')
            ).set(severity_score)
            
        except Exception as e:
            self.logger.error(f"Erreur monitoring incident: {str(e)}")

    def monitor_data_access(
        self,
        data_type: str,
        access_type: str,
        user_id: str,
        data_content: str
    ):
        """Surveille l'accès aux données"""
        try:
            self.data_access.labels(
                data_type=data_type,
                access_type=access_type
            ).inc()
            
            # Vérification PII
            pii_found = self._check_pii(data_content)
            if pii_found:
                self.pii_exposure.labels(
                    data_type=data_type
                ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur monitoring accès: {str(e)}")

    def monitor_gdpr_compliance(
        self,
        requirement: str,
        status: bool,
        details: Dict
    ):
        """Surveille la conformité GDPR"""
        try:
            compliance_score = 1.0 if status else 0.0
            self.gdpr_compliance.labels(
                requirement=requirement
            ).set(compliance_score)
            
            # Mise à jour rétention
            if 'retention_days' in details:
                self.data_retention.labels(
                    data_type=details.get('data_type', 'unknown')
                ).set(details['retention_days'])
            
        except Exception as e:
            self.logger.error(f"Erreur monitoring GDPR: {str(e)}")

    def _check_pii(self, content: str) -> bool:
        """Vérifie la présence de PII"""
        try:
            for pattern_name, pattern in self.pii_patterns.items():
                if re.search(pattern, content):
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur vérification PII: {str(e)}")
            return False

    def analyze_security_status(self) -> Dict:
        """Analyse l'état de la sécurité"""
        try:
            return {
                "authentication": {
                    "success_rate": (
                        self.auth_attempts.labels(
                            status="success"
                        )._value.get() /
                        max(self.auth_attempts._value.get(), 1)
                    ),
                    "active_sessions": {
                        user_type: self.active_sessions.labels(
                            user_type=user_type
                        )._value.get()
                        for user_type in ["standard", "admin"]
                    }
                },
                "incidents": {
                    incident_type: self.security_incidents.labels(
                        incident_type=incident_type
                    )._value.get()
                    for incident_type in [
                        "unauthorized_access",
                        "data_leak",
                        "brute_force"
                    ]
                },
                "vulnerabilities": {
                    component: self.vulnerability_score.labels(
                        component=component
                    )._value.get()
                    for component in ["api", "database", "auth"]
                },
                "data_protection": {
                    "pii_exposures": {
                        data_type: self.pii_exposure.labels(
                            data_type=data_type
                        )._value.get()
                        for data_type in ["user", "health", "payment"]
                    },
                    "gdpr_compliance": {
                        req: self.gdpr_compliance.labels(
                            requirement=req
                        )._value.get()
                        for req in [
                            "consent",
                            "access_right",
                            "deletion_right"
                        ]
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse sécurité: {str(e)}")
            return {}

    def generate_security_insights(self) -> List[Dict]:
        """Génère des insights de sécurité"""
        insights = []
        try:
            security_status = self.analyze_security_status()
            
            # Analyse authentification
            if security_status["authentication"]["success_rate"] < 0.95:
                insights.append({
                    "type": "authentication",
                    "severity": "high",
                    "message": "Taux d'échec d'authentification élevé",
                    "recommendation": "Vérifier les tentatives suspectes"
                })

            # Analyse incidents
            total_incidents = sum(
                security_status["incidents"].values()
            )
            if total_incidents > 10:
                insights.append({
                    "type": "security",
                    "severity": "high",
                    "message": "Nombre élevé d'incidents de sécurité",
                    "recommendation": "Audit de sécurité recommandé"
                })

            # Analyse vulnérabilités
            high_vuln_components = [
                comp for comp, score 
                in security_status["vulnerabilities"].items()
                if score > 0.7
            ]
            if high_vuln_components:
                insights.append({
                    "type": "vulnerability",
                    "severity": "high",
                    "message": f"Vulnérabilités détectées: {high_vuln_components}",
                    "recommendation": "Corriger les vulnérabilités"
                })

            # Analyse GDPR
            non_compliant = [
                req for req, score 
                in security_status["data_protection"]["gdpr_compliance"].items()
                if score < 1.0
            ]
            if non_compliant:
                insights.append({
                    "type": "compliance",
                    "severity": "high",
                    "message": f"Non-conformité GDPR: {non_compliant}",
                    "recommendation": "Mettre en conformité GDPR"
                })

        except Exception as e:
            self.logger.error(f"Erreur génération insights: {str(e)}")

        return insights

    def generate_security_report(self) -> Dict:
        """Génère un rapport de sécurité complet"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "security_status": self.analyze_security_status(),
                "insights": self.generate_security_insights(),
                "recommendations": self._generate_security_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_security_recommendations(self) -> List[Dict]:
        """Génère des recommandations de sécurité"""
        recommendations = []
        try:
            security_status = self.analyze_security_status()
            
            # Recommandations authentification
            if security_status["authentication"]["success_rate"] < 0.95:
                recommendations.append({
                    "type": "authentication",
                    "priority": "high",
                    "message": "Renforcer la sécurité d'authentification",
                    "actions": [
                        "Implémenter 2FA",
                        "Limiter les tentatives de connexion",
                        "Analyser les patterns d'échec"
                    ]
                })

            # Recommandations vulnérabilités
            high_vuln_count = sum(
                1 for score in security_status["vulnerabilities"].values()
                if score > 0.7
            )
            if high_vuln_count > 0:
                recommendations.append({
                    "type": "vulnerability",
                    "priority": "high",
                    "message": "Corriger les vulnérabilités critiques",
                    "actions": [
                        "Mettre à jour les dépendances",
                        "Corriger les failles de sécurité",
                        "Effectuer des tests de pénétration"
                    ]
                })

            # Recommandations protection données
            if any(
                exposures > 0 
                for exposures in security_status["data_protection"]["pii_exposures"].values()
            ):
                recommendations.append({
                    "type": "data_protection",
                    "priority": "high",
                    "message": "Améliorer la protection des données",
                    "actions": [
                        "Renforcer le chiffrement",
                        "Améliorer la détection PII",
                        "Mettre à jour les politiques d'accès"
                    ]
                })

            # Recommandations conformité
            non_compliant_count = sum(
                1 for score in security_status["data_protection"]["gdpr_compliance"].values()
                if score < 1.0
            )
            if non_compliant_count > 0:
                recommendations.append({
                    "type": "compliance",
                    "priority": "high",
                    "message": "Assurer la conformité GDPR",
                    "actions": [
                        "Mettre à jour les processus de consentement",
                        "Implémenter les droits d'accès",
                        "Documenter les processus de protection"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
security_monitor = SecurityMonitor()

# Monitoring authentification
security_monitor.monitor_authentication(
    user_id="123",
    success=True,
    user_type="standard"
)

# Monitoring incident
security_monitor.monitor_security_incident(
    incident_type="unauthorized_access",
    severity="high",
    details={"component": "api"}
)

# Monitoring accès données
security_monitor.monitor_data_access(
    data_type="health",
    access_type="read",
    user_id="123",
    data_content="Données de santé sensibles"
)

# Monitoring GDPR
security_monitor.monitor_gdpr_compliance(
    requirement="consent",
    status=True,
    details={
        "data_type": "health",
        "retention_days": 365
    }
)

# Analyse sécurité
security_status = security_monitor.analyze_security_status()

# Génération insights
insights = security_monitor.generate_security_insights()

# Génération rapport
report = security_monitor.generate_security_report()
"""
