from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json
import re
from prometheus_client import Counter, Gauge, Histogram
import pandas as pd
from collections import defaultdict

class LogMonitor:
    def __init__(self):
        # Métriques de logs
        self.log_count = Counter(
            'nutrition_log_total',
            'Nombre total de logs',
            ['log_level', 'component']
        )
        
        self.error_count = Counter(
            'nutrition_error_log_total',
            'Nombre total d\'erreurs',
            ['error_type']
        )
        
        self.log_processing_time = Histogram(
            'nutrition_log_processing_seconds',
            'Temps de traitement des logs',
            ['operation']
        )

        # Patterns d'erreurs
        self.error_patterns = {
            'database': r'(database|sql|db).*error',
            'auth': r'(authentication|authorization|login).*failed',
            'validation': r'(validation|invalid|schema).*error',
            'network': r'(network|connection|timeout).*error',
            'security': r'(security|vulnerability|attack).*detected'
        }

        self.logger = logging.getLogger(__name__)

    def process_log_entry(
        self,
        log_entry: Dict
    ):
        """Traite une entrée de log"""
        try:
            # Incrémente compteurs
            self.log_count.labels(
                log_level=log_entry.get('level', 'unknown'),
                component=log_entry.get('component', 'unknown')
            ).inc()

            # Analyse erreurs
            if log_entry.get('level') in ['ERROR', 'CRITICAL']:
                error_type = self._classify_error(
                    log_entry.get('message', '')
                )
                self.error_count.labels(
                    error_type=error_type
                ).inc()

        except Exception as e:
            self.logger.error(f"Erreur traitement log: {str(e)}")

    def _classify_error(
        self,
        message: str
    ) -> str:
        """Classifie le type d'erreur"""
        try:
            message = message.lower()
            for error_type, pattern in self.error_patterns.items():
                if re.search(pattern, message):
                    return error_type
            return 'unknown'
        except Exception as e:
            self.logger.error(f"Erreur classification: {str(e)}")
            return 'unknown'

    def analyze_logs(
        self,
        timeframe_hours: int = 24
    ) -> Dict:
        """Analyse les logs"""
        try:
            return {
                "count_by_level": {
                    level: self.log_count.labels(
                        log_level=level,
                        component='ALL'
                    )._value.get()
                    for level in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
                },
                "count_by_component": {
                    component: self.log_count.labels(
                        log_level='ALL',
                        component=component
                    )._value.get()
                    for component in ['api', 'auth', 'db', 'core']
                },
                "errors_by_type": {
                    error_type: self.error_count.labels(
                        error_type=error_type
                    )._value.get()
                    for error_type in self.error_patterns.keys()
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse logs: {str(e)}")
            return {}

    def detect_anomalies(
        self,
        logs: List[Dict],
        window_minutes: int = 60
    ) -> List[Dict]:
        """Détecte les anomalies dans les logs"""
        anomalies = []
        try:
            # Convertit logs en DataFrame
            df = pd.DataFrame(logs)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Agrège par fenêtre temporelle
            window = f'{window_minutes}min'
            agg = df.set_index('timestamp').resample(window).agg({
                'level': 'count',
                'component': 'value_counts'
            })

            # Détecte pics d'erreurs
            error_df = df[df['level'].isin(['ERROR', 'CRITICAL'])]
            error_agg = error_df.set_index('timestamp').resample(window).count()
            
            mean = error_agg['level'].mean()
            std = error_agg['level'].std()
            threshold = mean + 2 * std

            spikes = error_agg[error_agg['level'] > threshold]
            
            for timestamp, count in spikes['level'].items():
                anomalies.append({
                    'type': 'error_spike',
                    'timestamp': timestamp.isoformat(),
                    'count': count,
                    'threshold': threshold
                })

            # Détecte patterns inhabituels
            for component in df['component'].unique():
                comp_df = df[df['component'] == component]
                comp_agg = comp_df.set_index('timestamp').resample(window).count()
                
                comp_mean = comp_agg['level'].mean()
                comp_std = comp_agg['level'].std()
                comp_threshold = comp_mean + 2 * comp_std

                comp_spikes = comp_agg[comp_agg['level'] > comp_threshold]
                
                for timestamp, count in comp_spikes['level'].items():
                    anomalies.append({
                        'type': 'component_spike',
                        'component': component,
                        'timestamp': timestamp.isoformat(),
                        'count': count,
                        'threshold': comp_threshold
                    })

        except Exception as e:
            self.logger.error(f"Erreur détection anomalies: {str(e)}")

        return anomalies

    def analyze_error_patterns(
        self,
        logs: List[Dict]
    ) -> Dict:
        """Analyse les patterns d'erreurs"""
        patterns = defaultdict(int)
        try:
            error_logs = [
                log for log in logs
                if log.get('level') in ['ERROR', 'CRITICAL']
            ]

            for log in error_logs:
                message = log.get('message', '').lower()
                
                # Analyse mots fréquents
                words = message.split()
                for word in words:
                    if len(word) > 3:  # Ignore mots courts
                        patterns[word] += 1

                # Analyse séquences
                for i in range(len(words) - 1):
                    sequence = f"{words[i]} {words[i+1]}"
                    patterns[sequence] += 1

        except Exception as e:
            self.logger.error(f"Erreur analyse patterns: {str(e)}")

        return dict(patterns)

    def generate_log_report(
        self,
        logs: List[Dict]
    ) -> Dict:
        """Génère un rapport de logs"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "log_analysis": self.analyze_logs(),
                "anomalies": self.detect_anomalies(logs),
                "error_patterns": self.analyze_error_patterns(logs),
                "insights": self._generate_log_insights(logs)
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_log_insights(
        self,
        logs: List[Dict]
    ) -> List[Dict]:
        """Génère des insights depuis les logs"""
        insights = []
        try:
            # Analyse distribution erreurs
            error_logs = [
                log for log in logs
                if log.get('level') in ['ERROR', 'CRITICAL']
            ]
            
            if len(error_logs) > 0:
                error_rate = len(error_logs) / len(logs)
                if error_rate > 0.1:
                    insights.append({
                        'type': 'error_rate',
                        'severity': 'high',
                        'message': f"Taux d'erreur élevé: {error_rate:.2%}",
                        'value': error_rate
                    })

            # Analyse composants problématiques
            component_errors = defaultdict(int)
            for log in error_logs:
                component = log.get('component', 'unknown')
                component_errors[component] += 1

            for component, count in component_errors.items():
                if count > 10:
                    insights.append({
                        'type': 'component_errors',
                        'severity': 'medium',
                        'message': f"Erreurs fréquentes dans {component}",
                        'value': count
                    })

            # Analyse patterns temporels
            df = pd.DataFrame(logs)
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour

                hourly_errors = df[
                    df['level'].isin(['ERROR', 'CRITICAL'])
                ]['hour'].value_counts()

                peak_hour = hourly_errors.index[0]
                peak_count = hourly_errors.iloc[0]

                if peak_count > 20:
                    insights.append({
                        'type': 'temporal_pattern',
                        'severity': 'medium',
                        'message': f"Pic d'erreurs à {peak_hour}h",
                        'value': peak_count
                    })

        except Exception as e:
            self.logger.error(f"Erreur génération insights: {str(e)}")

        return insights

    def get_error_summary(
        self,
        logs: List[Dict]
    ) -> Dict:
        """Génère un résumé des erreurs"""
        try:
            error_logs = [
                log for log in logs
                if log.get('level') in ['ERROR', 'CRITICAL']
            ]

            return {
                "total_errors": len(error_logs),
                "error_types": {
                    error_type: self.error_count.labels(
                        error_type=error_type
                    )._value.get()
                    for error_type in self.error_patterns.keys()
                },
                "recent_errors": [
                    {
                        "timestamp": log.get('timestamp'),
                        "component": log.get('component'),
                        "message": log.get('message')
                    }
                    for log in sorted(
                        error_logs,
                        key=lambda x: x.get('timestamp', ''),
                        reverse=True
                    )[:5]
                ],
                "error_components": defaultdict(
                    int,
                    {
                        log.get('component', 'unknown'): 1
                        for log in error_logs
                    }
                )
            }
        except Exception as e:
            self.logger.error(f"Erreur génération résumé: {str(e)}")
            return {}

# Exemple d'utilisation:
"""
log_monitor = LogMonitor()

# Traitement d'une entrée de log
log_entry = {
    'timestamp': '2024-01-20T10:30:00',
    'level': 'ERROR',
    'component': 'api',
    'message': 'Database connection error: timeout'
}
log_monitor.process_log_entry(log_entry)

# Analyse des logs
log_analysis = log_monitor.analyze_logs()

# Détection anomalies
logs = [
    # Liste d'entrées de log
]
anomalies = log_monitor.detect_anomalies(logs)

# Analyse patterns d'erreurs
error_patterns = log_monitor.analyze_error_patterns(logs)

# Génération rapport
report = log_monitor.generate_log_report(logs)

# Résumé erreurs
error_summary = log_monitor.get_error_summary(logs)
"""
