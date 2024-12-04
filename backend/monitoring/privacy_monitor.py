from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional
import logging
import json
from datetime import datetime, timedelta
import hashlib
import re

class PrivacyMonitor:
    def __init__(self):
        # Métriques de conformité RGPD
        self.data_access_requests = Counter(
            'nutrition_gdpr_access_requests_total',
            'Nombre total de demandes d\'accès aux données',
            ['request_type', 'status']
        )
        
        self.data_deletion_requests = Counter(
            'nutrition_gdpr_deletion_requests_total',
            'Nombre total de demandes de suppression',
            ['status']
        )
        
        self.consent_tracking = Gauge(
            'nutrition_user_consent_status',
            'Statut des consentements utilisateur',
            ['consent_type']
        )

        # Métriques de protection des données
        self.data_encryption_status = Gauge(
            'nutrition_data_encryption_status',
            'Statut du chiffrement des données',
            ['data_type']
        )
        
        self.pii_detection = Counter(
            'nutrition_pii_detection_total',
            'Détection de données personnelles',
            ['data_type', 'severity']
        )

        # Métriques d'audit
        self.data_access_audit = Counter(
            'nutrition_data_access_audit_total',
            'Audit des accès aux données',
            ['user_type', 'data_type', 'access_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_data_request(self, request_type: str, status: str):
        """Suit les demandes d'accès aux données"""
        try:
            self.data_access_requests.labels(
                request_type=request_type,
                status=status
            ).inc()
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi des demandes: {str(e)}")

    def track_deletion_request(self, status: str):
        """Suit les demandes de suppression"""
        self.data_deletion_requests.labels(status=status).inc()

    def update_consent_status(self, consent_type: str, count: int):
        """Met à jour le statut des consentements"""
        self.consent_tracking.labels(consent_type=consent_type).set(count)

    def check_data_encryption(self, data_type: str) -> bool:
        """Vérifie le statut du chiffrement"""
        try:
            # Simulation de vérification
            is_encrypted = True  # À remplacer par une vraie vérification
            self.data_encryption_status.labels(data_type=data_type).set(
                1 if is_encrypted else 0
            )
            return is_encrypted
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du chiffrement: {str(e)}")
            return False

    def detect_pii(self, data: str, data_type: str) -> List[Dict]:
        """Détecte les informations personnelles"""
        pii_patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ssn': r'\d{3}-\d{2}-\d{4}',
            'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}'
        }

        findings = []
        for pii_type, pattern in pii_patterns.items():
            matches = re.finditer(pattern, data)
            for match in matches:
                self.pii_detection.labels(
                    data_type=data_type,
                    severity='high'
                ).inc()
                findings.append({
                    'type': pii_type,
                    'position': match.span(),
                    'severity': 'high'
                })

        return findings

    def audit_data_access(self, user_type: str, data_type: str, access_type: str):
        """Enregistre les accès aux données"""
        self.data_access_audit.labels(
            user_type=user_type,
            data_type=data_type,
            access_type=access_type
        ).inc()

    def check_data_retention(self, data: Dict) -> List[Dict]:
        """Vérifie la conformité de la rétention des données"""
        retention_policies = {
            'health_data': 365,  # jours
            'personal_info': 730,
            'activity_logs': 90,
            'analytics': 30
        }

        violations = []
        current_date = datetime.now()

        for data_type, max_days in retention_policies.items():
            if data_type in data:
                creation_date = datetime.fromisoformat(data[data_type]['created_at'])
                age_days = (current_date - creation_date).days

                if age_days > max_days:
                    violations.append({
                        'data_type': data_type,
                        'age_days': age_days,
                        'max_days': max_days,
                        'action_required': 'delete'
                    })

        return violations

    def anonymize_data(self, data: Dict) -> Dict:
        """Anonymise les données sensibles"""
        try:
            anonymized = data.copy()

            # Champs à anonymiser
            sensitive_fields = ['name', 'email', 'phone', 'address']
            
            for field in sensitive_fields:
                if field in anonymized:
                    # Utilisation de hachage pour l'anonymisation
                    value = str(anonymized[field])
                    hashed = hashlib.sha256(value.encode()).hexdigest()[:8]
                    anonymized[field] = f"ANON_{hashed}"

            return anonymized
        except Exception as e:
            self.logger.error(f"Erreur lors de l'anonymisation: {str(e)}")
            return data

    def generate_privacy_report(self) -> Dict:
        """Génère un rapport de conformité"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'data_requests': {
                        'access': self.data_access_requests._value.get(),
                        'deletion': self.data_deletion_requests._value.get()
                    },
                    'consent_status': self.consent_tracking._value.get(),
                    'encryption_status': self.data_encryption_status._value.get(),
                    'pii_detections': self.pii_detection._value.get(),
                    'data_accesses': self.data_access_audit._value.get()
                },
                'recommendations': self._generate_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les métriques"""
        recommendations = []
        
        # Analyse des demandes d'accès
        if self.data_access_requests._value.get() > 100:
            recommendations.append(
                "Volume élevé de demandes d'accès - Envisager l'automatisation"
            )

        # Analyse des détections PII
        if self.pii_detection._value.get() > 50:
            recommendations.append(
                "Nombre élevé de détections PII - Renforcer les contrôles de données"
            )

        # Analyse du chiffrement
        if self.data_encryption_status._value.get() < 1:
            recommendations.append(
                "Certaines données ne sont pas chiffrées - Mettre à jour le chiffrement"
            )

        return recommendations

# Exemple d'utilisation:
"""
privacy_monitor = PrivacyMonitor()

# Suivi des demandes RGPD
privacy_monitor.track_data_request('access', 'completed')
privacy_monitor.track_deletion_request('pending')

# Vérification du chiffrement
privacy_monitor.check_data_encryption('health_data')

# Détection PII
data = "Email: user@example.com, Tel: +1-234-567-8900"
findings = privacy_monitor.detect_pii(data, 'user_profile')

# Audit d'accès
privacy_monitor.audit_data_access('admin', 'health_data', 'read')

# Vérification rétention
data = {
    'health_data': {'created_at': '2023-01-01T00:00:00'},
    'analytics': {'created_at': '2023-12-01T00:00:00'}
}
violations = privacy_monitor.check_data_retention(data)

# Anonymisation
sensitive_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'health_data': {'weight': 70}
}
anonymized = privacy_monitor.anonymize_data(sensitive_data)

# Génération rapport
report = privacy_monitor.generate_privacy_report()
"""
