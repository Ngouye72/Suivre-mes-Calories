import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import jinja2
import pdfkit

class AdvancedAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'correlation_threshold': 0.7,
            'pattern_sensitivity': 0.8,
            'seasonality_period': 24,
            'report_template': 'templates/analytics_report.html',
            'analysis_window': '30d'
        }
        
        # Templates
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates/')
        )

    def analyze_correlations(self, metrics_data: Dict) -> Dict:
        """Analyse les corrélations entre métriques"""
        try:
            # Préparation données
            df = pd.DataFrame(metrics_data)
            
            # Calcul corrélations
            correlations = df.corr()
            
            # Identification corrélations significatives
            significant_corrs = []
            for i in range(len(correlations.columns)):
                for j in range(i + 1, len(correlations.columns)):
                    corr = correlations.iloc[i, j]
                    if abs(corr) > self.config['correlation_threshold']:
                        significant_corrs.append({
                            'metric1': correlations.columns[i],
                            'metric2': correlations.columns[j],
                            'correlation': corr,
                            'type': 'positive' if corr > 0 else 'negative',
                            'strength': self._get_correlation_strength(corr)
                        })
            
            # Analyse temporelle
            time_correlations = self._analyze_time_correlations(df)
            
            return {
                'correlations': significant_corrs,
                'time_correlations': time_correlations,
                'insights': self._generate_correlation_insights(
                    significant_corrs,
                    time_correlations
                )
            }

        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {str(e)}")
            return {}

    def detect_patterns(self, metrics_data: Dict) -> Dict:
        """Détecte les patterns dans les métriques"""
        try:
            patterns = {
                'seasonal': self._detect_seasonal_patterns(metrics_data),
                'cyclic': self._detect_cyclic_patterns(metrics_data),
                'trends': self._detect_trend_patterns(metrics_data),
                'anomalies': self._detect_anomaly_patterns(metrics_data),
                'clusters': self._detect_metric_clusters(metrics_data)
            }
            
            return {
                'patterns': patterns,
                'insights': self._generate_pattern_insights(patterns)
            }

        except Exception as e:
            self.logger.error(f"Error detecting patterns: {str(e)}")
            return {}

    def generate_automated_report(
        self,
        metrics_data: Dict,
        report_type: str = 'pdf'
    ) -> str:
        """Génère un rapport automatique"""
        try:
            # Analyses
            analyses = {
                'correlations': self.analyze_correlations(metrics_data),
                'patterns': self.detect_patterns(metrics_data),
                'statistics': self._generate_statistics(metrics_data),
                'predictions': self._generate_predictions(metrics_data)
            }
            
            # Génération rapport
            if report_type == 'pdf':
                return self._generate_pdf_report(analyses)
            elif report_type == 'html':
                return self._generate_html_report(analyses)
            else:
                raise ValueError(f"Unknown report type: {report_type}")

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return ""

    def _analyze_time_correlations(self, df: pd.DataFrame) -> List[Dict]:
        """Analyse les corrélations temporelles"""
        try:
            time_correlations = []
            
            for column in df.columns:
                if column != 'timestamp':
                    # Test stationnarité
                    adf_result = adfuller(df[column].dropna())
                    
                    # Décomposition temporelle
                    decomposition = seasonal_decompose(
                        df[column],
                        period=self.config['seasonality_period']
                    )
                    
                    time_correlations.append({
                        'metric': column,
                        'stationary': adf_result[1] < 0.05,
                        'trend_strength': np.std(decomposition.trend),
                        'seasonal_strength': np.std(decomposition.seasonal),
                        'period': self._detect_dominant_period(df[column])
                    })
            
            return time_correlations

        except Exception as e:
            self.logger.error(f"Error analyzing time correlations: {str(e)}")
            return []

    def _detect_seasonal_patterns(self, metrics_data: Dict) -> List[Dict]:
        """Détecte les patterns saisonniers"""
        try:
            seasonal_patterns = []
            df = pd.DataFrame(metrics_data)
            
            for column in df.columns:
                if column != 'timestamp':
                    # Décomposition
                    decomposition = seasonal_decompose(
                        df[column],
                        period=self.config['seasonality_period']
                    )
                    
                    # Analyse saisonnalité
                    seasonal_strength = np.std(decomposition.seasonal)
                    if seasonal_strength > self.config['pattern_sensitivity']:
                        seasonal_patterns.append({
                            'metric': column,
                            'strength': seasonal_strength,
                            'period': self.config['seasonality_period'],
                            'pattern': decomposition.seasonal.tolist()
                        })
            
            return seasonal_patterns

        except Exception as e:
            self.logger.error(f"Error detecting seasonal patterns: {str(e)}")
            return []

    def _detect_cyclic_patterns(self, metrics_data: Dict) -> List[Dict]:
        """Détecte les patterns cycliques"""
        try:
            cyclic_patterns = []
            df = pd.DataFrame(metrics_data)
            
            for column in df.columns:
                if column != 'timestamp':
                    # Analyse spectrale
                    frequencies = np.fft.fftfreq(len(df[column]))
                    spectrum = np.abs(np.fft.fft(df[column]))
                    
                    # Identification cycles dominants
                    dominant_freq_idx = np.argsort(spectrum)[-3:]
                    
                    cycles = [{
                        'frequency': abs(frequencies[idx]),
                        'amplitude': spectrum[idx]
                    } for idx in dominant_freq_idx if frequencies[idx] != 0]
                    
                    if cycles:
                        cyclic_patterns.append({
                            'metric': column,
                            'cycles': cycles
                        })
            
            return cyclic_patterns

        except Exception as e:
            self.logger.error(f"Error detecting cyclic patterns: {str(e)}")
            return []

    def _detect_anomaly_patterns(self, metrics_data: Dict) -> List[Dict]:
        """Détecte les patterns d'anomalies"""
        try:
            anomaly_patterns = []
            df = pd.DataFrame(metrics_data)
            
            for column in df.columns:
                if column != 'timestamp':
                    # Calcul statistiques
                    mean = df[column].mean()
                    std = df[column].std()
                    
                    # Détection anomalies
                    anomalies = df[
                        (df[column] > mean + 3*std) |
                        (df[column] < mean - 3*std)
                    ]
                    
                    if not anomalies.empty:
                        anomaly_patterns.append({
                            'metric': column,
                            'count': len(anomalies),
                            'timestamps': anomalies.index.tolist(),
                            'values': anomalies[column].tolist()
                        })
            
            return anomaly_patterns

        except Exception as e:
            self.logger.error(f"Error detecting anomaly patterns: {str(e)}")
            return []

    def _detect_metric_clusters(self, metrics_data: Dict) -> List[Dict]:
        """Détecte les clusters de métriques"""
        try:
            df = pd.DataFrame(metrics_data)
            
            # Normalisation
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df.drop('timestamp', axis=1))
            
            # Réduction dimensionnalité
            pca = PCA(n_components=2)
            reduced_data = pca.fit_transform(scaled_data)
            
            # Clustering
            dbscan = DBSCAN(eps=0.3, min_samples=5)
            clusters = dbscan.fit_predict(reduced_data)
            
            # Analyse clusters
            cluster_info = []
            for cluster_id in set(clusters):
                if cluster_id != -1:  # Ignore noise
                    mask = clusters == cluster_id
                    cluster_info.append({
                        'id': cluster_id,
                        'size': sum(mask),
                        'metrics': df.columns[mask].tolist(),
                        'centroid': reduced_data[mask].mean(axis=0).tolist()
                    })
            
            return cluster_info

        except Exception as e:
            self.logger.error(f"Error detecting metric clusters: {str(e)}")
            return []

    def _generate_correlation_insights(
        self,
        correlations: List[Dict],
        time_correlations: List[Dict]
    ) -> List[Dict]:
        """Génère des insights basés sur les corrélations"""
        try:
            insights = []
            
            # Analyse corrélations fortes
            strong_correlations = [
                c for c in correlations
                if abs(c['correlation']) > 0.8
            ]
            if strong_correlations:
                insights.append({
                    'type': 'strong_correlation',
                    'description': 'Corrélations fortes détectées',
                    'details': strong_correlations
                })
            
            # Analyse patterns temporels
            seasonal_metrics = [
                tc for tc in time_correlations
                if tc['seasonal_strength'] > 0.5
            ]
            if seasonal_metrics:
                insights.append({
                    'type': 'seasonality',
                    'description': 'Patterns saisonniers détectés',
                    'details': seasonal_metrics
                })
            
            return insights

        except Exception as e:
            self.logger.error(f"Error generating correlation insights: {str(e)}")
            return []

    def _generate_pattern_insights(self, patterns: Dict) -> List[Dict]:
        """Génère des insights basés sur les patterns"""
        try:
            insights = []
            
            # Analyse patterns saisonniers
            if patterns['seasonal']:
                insights.append({
                    'type': 'seasonal_patterns',
                    'description': 'Patterns saisonniers significatifs',
                    'details': patterns['seasonal']
                })
            
            # Analyse anomalies
            if patterns['anomalies']:
                insights.append({
                    'type': 'anomaly_patterns',
                    'description': 'Patterns d\'anomalies détectés',
                    'details': patterns['anomalies']
                })
            
            # Analyse clusters
            if patterns['clusters']:
                insights.append({
                    'type': 'metric_clusters',
                    'description': 'Groupes de métriques corrélées',
                    'details': patterns['clusters']
                })
            
            return insights

        except Exception as e:
            self.logger.error(f"Error generating pattern insights: {str(e)}")
            return []

    def _generate_pdf_report(self, analyses: Dict) -> str:
        """Génère un rapport PDF"""
        try:
            # Chargement template
            template = self.template_env.get_template('analytics_report.html')
            
            # Génération HTML
            html = template.render(
                analyses=analyses,
                timestamp=datetime.now().isoformat()
            )
            
            # Conversion PDF
            output_file = f"reports/analytics_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            pdfkit.from_string(html, output_file)
            
            return output_file

        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            return ""

    def _get_correlation_strength(self, correlation: float) -> str:
        """Détermine la force d'une corrélation"""
        abs_corr = abs(correlation)
        if abs_corr > 0.8:
            return 'very_strong'
        elif abs_corr > 0.6:
            return 'strong'
        elif abs_corr > 0.4:
            return 'moderate'
        else:
            return 'weak'

# Exemple d'utilisation:
"""
analytics = AdvancedAnalytics()

# Données exemple
metrics_data = {
    'timestamp': pd.date_range(start='2024-01-01', periods=1000, freq='H'),
    'cpu_usage': np.random.normal(60, 10, 1000),
    'memory_usage': np.random.normal(70, 15, 1000),
    'response_time': np.random.normal(200, 50, 1000),
    'active_users': np.random.normal(500, 100, 1000)
}

# Analyse corrélations
correlations = analytics.analyze_correlations(metrics_data)

# Détection patterns
patterns = analytics.detect_patterns(metrics_data)

# Génération rapport
report = analytics.generate_automated_report(metrics_data, 'pdf')
"""
