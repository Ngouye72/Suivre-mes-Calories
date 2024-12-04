import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import threading
import time
import queue
from collections import deque

class RealtimeVisualization:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'update_interval': 5,  # secondes
            'window_size': 100,    # points
            'alert_thresholds': {
                'cpu_usage': 80,
                'memory_usage': 85,
                'response_time': 500,
                'error_rate': 5
            },
            'comparison_window': '24h'
        }
        
        # Buffers temps réel
        self.buffers = {
            'timestamps': deque(maxlen=self.config['window_size']),
            'metrics': {},
            'alerts': deque(maxlen=50)
        }
        
        # File d'attente mise à jour
        self.update_queue = queue.Queue()
        
        # Démarrage collecte
        self._start_collection()

    def _start_collection(self):
        """Démarre la collecte en temps réel"""
        def collect_data():
            while True:
                try:
                    # Collecte données
                    data = self._collect_metrics()
                    
                    # Mise à jour buffers
                    self._update_buffers(data)
                    
                    # Vérification alertes
                    self._check_alerts(data)
                    
                    # Notification mise à jour
                    self.update_queue.put(data)
                    
                    time.sleep(self.config['update_interval'])
                    
                except Exception as e:
                    self.logger.error(f"Error collecting data: {str(e)}")

        collection_thread = threading.Thread(
            target=collect_data,
            daemon=True
        )
        collection_thread.start()

    def _collect_metrics(self) -> Dict:
        """Collecte les métriques en temps réel"""
        try:
            metrics = {
                'timestamp': datetime.now(),
                'system': self._collect_system_metrics(),
                'user': self._collect_user_metrics(),
                'nutrition': self._collect_nutrition_metrics(),
                'performance': self._collect_performance_metrics()
            }
            
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            return {}

    def _update_buffers(self, data: Dict):
        """Met à jour les buffers de données"""
        try:
            # Ajout timestamp
            self.buffers['timestamps'].append(data['timestamp'])
            
            # Mise à jour métriques
            for category, metrics in data.items():
                if category != 'timestamp':
                    if category not in self.buffers['metrics']:
                        self.buffers['metrics'][category] = {}
                        
                    for metric, value in metrics.items():
                        if metric not in self.buffers['metrics'][category]:
                            self.buffers['metrics'][category][metric] = deque(
                                maxlen=self.config['window_size']
                            )
                        self.buffers['metrics'][category][metric].append(value)

        except Exception as e:
            self.logger.error(f"Error updating buffers: {str(e)}")

    def create_realtime_dashboard(self) -> Dict:
        """Crée un dashboard temps réel"""
        try:
            dashboard = {
                'system': self._create_system_dashboard(),
                'user': self._create_user_dashboard(),
                'nutrition': self._create_nutrition_dashboard(),
                'performance': self._create_performance_dashboard(),
                'alerts': self._create_alerts_dashboard()
            }
            
            return dashboard

        except Exception as e:
            self.logger.error(f"Error creating realtime dashboard: {str(e)}")
            return {}

    def _create_system_dashboard(self) -> Dict:
        """Crée le dashboard système"""
        try:
            # Création subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'CPU Usage', 'Memory Usage',
                    'Disk Usage', 'Network Traffic'
                )
            )
            
            # CPU Usage
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=self._get_latest_value('system', 'cpu_usage'),
                    delta={
                        'reference': self._get_previous_value('system', 'cpu_usage')
                    },
                    gauge={'axis': {'range': [0, 100]}},
                    title={'text': "CPU %"}
                ),
                row=1, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=self._get_latest_value('system', 'memory_usage'),
                    delta={
                        'reference': self._get_previous_value(
                            'system',
                            'memory_usage'
                        )
                    },
                    gauge={'axis': {'range': [0, 100]}},
                    title={'text': "Memory %"}
                ),
                row=1, col=2
            )
            
            # Disk Usage
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=self._get_latest_value('system', 'disk_usage'),
                    delta={
                        'reference': self._get_previous_value('system', 'disk_usage')
                    },
                    gauge={'axis': {'range': [0, 100]}},
                    title={'text': "Disk %"}
                ),
                row=2, col=1
            )
            
            # Network Traffic
            fig.add_trace(
                go.Scatter(
                    x=list(self.buffers['timestamps']),
                    y=self._get_metric_values('system', 'network_traffic'),
                    mode='lines',
                    name='Network'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                showlegend=False,
                title_text="System Metrics"
            )
            
            return {
                'figure': fig,
                'alerts': self._get_system_alerts(),
                'comparisons': self._get_system_comparisons()
            }

        except Exception as e:
            self.logger.error(f"Error creating system dashboard: {str(e)}")
            return {}

    def _create_alerts_dashboard(self) -> Dict:
        """Crée le dashboard des alertes"""
        try:
            # Création figure
            fig = go.Figure()
            
            # Timeline alertes
            alerts = list(self.buffers['alerts'])
            fig.add_trace(go.Scatter(
                x=[alert['timestamp'] for alert in alerts],
                y=[alert['value'] for alert in alerts],
                mode='markers',
                marker=dict(
                    size=12,
                    color=[self._get_alert_color(alert['severity'])
                           for alert in alerts],
                    symbol=[self._get_alert_symbol(alert['type'])
                           for alert in alerts]
                ),
                text=[self._format_alert_text(alert) for alert in alerts],
                hoverinfo='text'
            ))
            
            fig.update_layout(
                title='Alert Timeline',
                xaxis_title='Time',
                yaxis_title='Value',
                showlegend=False
            )
            
            return {
                'figure': fig,
                'active_alerts': self._get_active_alerts(),
                'alert_stats': self._get_alert_stats()
            }

        except Exception as e:
            self.logger.error(f"Error creating alerts dashboard: {str(e)}")
            return {}

    def _check_alerts(self, data: Dict):
        """Vérifie et génère les alertes"""
        try:
            for category, metrics in data.items():
                if category != 'timestamp':
                    for metric, value in metrics.items():
                        threshold = self.config['alert_thresholds'].get(
                            f"{category}_{metric}"
                        )
                        if threshold and value > threshold:
                            self._add_alert({
                                'timestamp': data['timestamp'],
                                'type': f"{category}_{metric}",
                                'severity': self._get_severity(value, threshold),
                                'value': value,
                                'threshold': threshold,
                                'message': f"{metric} above threshold: {value}"
                            })

        except Exception as e:
            self.logger.error(f"Error checking alerts: {str(e)}")

    def _add_alert(self, alert: Dict):
        """Ajoute une alerte"""
        try:
            self.buffers['alerts'].append(alert)
        except Exception as e:
            self.logger.error(f"Error adding alert: {str(e)}")

    def get_comparative_analysis(
        self,
        metric: str,
        period: str = '24h'
    ) -> Dict:
        """Génère une analyse comparative"""
        try:
            current_data = self._get_metric_values('all', metric)
            previous_data = self._get_historical_data(metric, period)
            
            analysis = {
                'current': {
                    'mean': np.mean(current_data),
                    'std': np.std(current_data),
                    'min': np.min(current_data),
                    'max': np.max(current_data)
                },
                'previous': {
                    'mean': np.mean(previous_data),
                    'std': np.std(previous_data),
                    'min': np.min(previous_data),
                    'max': np.max(previous_data)
                },
                'change': {
                    'absolute': np.mean(current_data) - np.mean(previous_data),
                    'percentage': ((np.mean(current_data) - np.mean(previous_data))
                                 / np.mean(previous_data) * 100)
                },
                'trends': self._analyze_trends(current_data, previous_data)
            }
            
            return analysis

        except Exception as e:
            self.logger.error(f"Error generating comparative analysis: {str(e)}")
            return {}

    def _analyze_trends(
        self,
        current_data: List[float],
        previous_data: List[float]
    ) -> Dict:
        """Analyse les tendances"""
        try:
            return {
                'direction': 'up' if np.mean(current_data) > np.mean(previous_data)
                            else 'down',
                'volatility': np.std(current_data) / np.mean(current_data),
                'acceleration': self._calculate_acceleration(current_data),
                'seasonality': self._detect_seasonality(current_data)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _get_severity(self, value: float, threshold: float) -> str:
        """Détermine la sévérité d'une alerte"""
        try:
            ratio = value / threshold
            if ratio > 1.5:
                return 'critical'
            elif ratio > 1.2:
                return 'high'
            elif ratio > 1:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            self.logger.error(f"Error getting severity: {str(e)}")
            return 'unknown'

    def _get_alert_color(self, severity: str) -> str:
        """Retourne la couleur d'une alerte"""
        return {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'green'
        }.get(severity, 'gray')

    def _get_alert_symbol(self, alert_type: str) -> str:
        """Retourne le symbole d'une alerte"""
        return {
            'system_cpu': 'circle',
            'system_memory': 'square',
            'performance_response': 'diamond',
            'user_activity': 'star'
        }.get(alert_type, 'circle')

    def _format_alert_text(self, alert: Dict) -> str:
        """Formate le texte d'une alerte"""
        return f"""
            Type: {alert['type']}
            Severity: {alert['severity']}
            Value: {alert['value']}
            Threshold: {alert['threshold']}
            Time: {alert['timestamp']}
        """

# Exemple d'utilisation:
"""
viz = RealtimeVisualization()

# Création dashboard temps réel
dashboard = viz.create_realtime_dashboard()

# Analyse comparative
analysis = viz.get_comparative_analysis('cpu_usage', '24h')

# Boucle mise à jour
while True:
    try:
        # Attente nouvelle donnée
        data = viz.update_queue.get()
        
        # Mise à jour dashboard
        dashboard = viz.create_realtime_dashboard()
        
        # Mise à jour analyse
        analysis = viz.get_comparative_analysis('cpu_usage', '24h')
        
        time.sleep(5)
        
    except Exception as e:
        print(f"Error updating: {str(e)}")
"""
