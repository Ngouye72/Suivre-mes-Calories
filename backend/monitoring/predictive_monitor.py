import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
import joblib
import logging
from typing import Dict, List, Optional, Tuple
import threading
import time

class PredictiveMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'history_window': 24 * 7,  # 1 semaine
            'prediction_window': 24,   # 24 heures
            'anomaly_threshold': -0.5,
            'model_path': 'models/anomaly_detector.joblib',
            'metrics_history': []
        }
        
        # Initialisation modèles
        self.models = {
            'anomaly_detector': self._init_anomaly_detector(),
            'trend_analyzer': self._init_trend_analyzer(),
            'performance_predictor': self._init_performance_predictor()
        }
        
        # Démarrage collection
        self._start_collection()

    def _init_anomaly_detector(self):
        """Initialise le détecteur d'anomalies"""
        try:
            return IsolationForest(
                contamination=0.1,
                random_state=42
            )
        except Exception as e:
            self.logger.error(f"Error initializing anomaly detector: {str(e)}")
            return None

    def _init_trend_analyzer(self):
        """Initialise l'analyseur de tendances"""
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            return ExponentialSmoothing
        except Exception as e:
            self.logger.error(f"Error initializing trend analyzer: {str(e)}")
            return None

    def _init_performance_predictor(self):
        """Initialise le prédicteur de performance"""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            return GradientBoostingRegressor(
                n_estimators=100,
                random_state=42
            )
        except Exception as e:
            self.logger.error(
                f"Error initializing performance predictor: {str(e)}"
            )
            return None

    def _start_collection(self):
        """Démarre la collecte périodique des métriques"""
        def collect_metrics():
            while True:
                try:
                    metrics = self._collect_current_metrics()
                    self._update_history(metrics)
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    self.logger.error(f"Error collecting metrics: {str(e)}")

        collection_thread = threading.Thread(
            target=collect_metrics,
            daemon=True
        )
        collection_thread.start()

    def _collect_current_metrics(self) -> Dict:
        """Collecte les métriques actuelles"""
        try:
            # Exemple de métriques à collecter
            return {
                'timestamp': datetime.now(),
                'cpu_usage': self._get_cpu_usage(),
                'memory_usage': self._get_memory_usage(),
                'response_time': self._get_response_time(),
                'error_rate': self._get_error_rate(),
                'request_rate': self._get_request_rate()
            }
        except Exception as e:
            self.logger.error(f"Error collecting current metrics: {str(e)}")
            return {}

    def _update_history(self, metrics: Dict):
        """Met à jour l'historique des métriques"""
        try:
            self.config['metrics_history'].append(metrics)
            
            # Limite taille historique
            if len(self.config['metrics_history']) > self.config['history_window']:
                self.config['metrics_history'] = self.config['metrics_history'][
                    -self.config['history_window']:
                ]
        except Exception as e:
            self.logger.error(f"Error updating history: {str(e)}")

    def detect_anomalies(self) -> List[Dict]:
        """Détecte les anomalies dans les métriques"""
        try:
            if not self.config['metrics_history']:
                return []

            # Préparation données
            df = pd.DataFrame(self.config['metrics_history'])
            features = ['cpu_usage', 'memory_usage', 'response_time', 
                       'error_rate', 'request_rate']
            X = df[features].values
            
            # Normalisation
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Détection
            predictions = self.models['anomaly_detector'].fit_predict(X_scaled)
            
            # Identification anomalies
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred < self.config['anomaly_threshold']:
                    anomalies.append({
                        'timestamp': df['timestamp'].iloc[i],
                        'metrics': {
                            feature: df[feature].iloc[i]
                            for feature in features
                        },
                        'score': pred
                    })
            
            return anomalies

        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return []

    def analyze_trends(self) -> Dict:
        """Analyse les tendances des métriques"""
        try:
            if not self.config['metrics_history']:
                return {}

            df = pd.DataFrame(self.config['metrics_history'])
            trends = {}
            
            for metric in ['cpu_usage', 'memory_usage', 'response_time']:
                # Analyse tendance
                model = self.models['trend_analyzer'](
                    df[metric],
                    seasonal_periods=24
                ).fit()
                
                # Prédiction
                forecast = model.forecast(self.config['prediction_window'])
                
                trends[metric] = {
                    'current': df[metric].iloc[-1],
                    'trend': 'increasing' if forecast[-1] > df[metric].iloc[-1]
                            else 'decreasing',
                    'forecast': forecast.tolist()
                }
            
            return trends

        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def predict_performance(self) -> Dict:
        """Prédit les performances futures"""
        try:
            if not self.config['metrics_history']:
                return {}

            df = pd.DataFrame(self.config['metrics_history'])
            
            # Préparation features
            features = ['cpu_usage', 'memory_usage', 'request_rate']
            target = 'response_time'
            
            X = df[features].values
            y = df[target].values
            
            # Entraînement modèle
            self.models['performance_predictor'].fit(X, y)
            
            # Prédiction
            latest_features = X[-1].reshape(1, -1)
            prediction = self.models['performance_predictor'].predict(
                latest_features
            )[0]
            
            return {
                'current_response_time': y[-1],
                'predicted_response_time': prediction,
                'change_percent': ((prediction - y[-1]) / y[-1]) * 100
            }

        except Exception as e:
            self.logger.error(f"Error predicting performance: {str(e)}")
            return {}

    def generate_insights(self) -> Dict:
        """Génère des insights basés sur les analyses"""
        try:
            insights = {
                'timestamp': datetime.now().isoformat(),
                'anomalies': self.detect_anomalies(),
                'trends': self.analyze_trends(),
                'performance_prediction': self.predict_performance(),
                'recommendations': []
            }
            
            # Analyse anomalies
            if insights['anomalies']:
                insights['recommendations'].append({
                    'type': 'anomaly',
                    'priority': 'high',
                    'message': f"Detected {len(insights['anomalies'])} anomalies",
                    'details': [
                        f"Anomaly at {a['timestamp']}: {a['metrics']}"
                        for a in insights['anomalies']
                    ]
                })
            
            # Analyse tendances
            for metric, trend in insights['trends'].items():
                if trend['trend'] == 'increasing' and metric in [
                    'cpu_usage', 'memory_usage', 'response_time'
                ]:
                    insights['recommendations'].append({
                        'type': 'trend',
                        'priority': 'medium',
                        'message': f"Increasing trend in {metric}",
                        'details': [
                            f"Current: {trend['current']}",
                            f"Forecast: {trend['forecast'][-1]}"
                        ]
                    })
            
            # Analyse performance
            perf_pred = insights['performance_prediction']
            if perf_pred.get('change_percent', 0) > 10:
                insights['recommendations'].append({
                    'type': 'performance',
                    'priority': 'high',
                    'message': "Performance degradation predicted",
                    'details': [
                        f"Current: {perf_pred['current_response_time']}ms",
                        f"Predicted: {perf_pred['predicted_response_time']}ms",
                        f"Change: {perf_pred['change_percent']}%"
                    ]
                })
            
            return insights

        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {}

    def _get_cpu_usage(self) -> float:
        """Récupère l'utilisation CPU"""
        try:
            import psutil
            return psutil.cpu_percent()
        except:
            return np.random.uniform(20, 80)

    def _get_memory_usage(self) -> float:
        """Récupère l'utilisation mémoire"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return np.random.uniform(30, 90)

    def _get_response_time(self) -> float:
        """Récupère le temps de réponse moyen"""
        return np.random.uniform(50, 200)

    def _get_error_rate(self) -> float:
        """Récupère le taux d'erreur"""
        return np.random.uniform(0, 5)

    def _get_request_rate(self) -> float:
        """Récupère le taux de requêtes"""
        return np.random.uniform(10, 100)

# Exemple d'utilisation:
"""
monitor = PredictiveMonitor()

# Attendre collecte données
time.sleep(300)

# Générer insights
insights = monitor.generate_insights()

# Analyser résultats
print("Anomalies:", len(insights['anomalies']))
print("Trends:", insights['trends'])
print("Performance Prediction:", insights['performance_prediction'])
print("Recommendations:", insights['recommendations'])
"""
