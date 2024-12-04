from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import threading
import time

from .monitoring_manager import MonitoringManager

app = Flask(__name__)
monitoring_manager = MonitoringManager()

# Cache pour stocker les données
metrics_cache = {
    'last_update': None,
    'data': None,
    'cache_duration': timedelta(seconds=30)
}

def get_cached_metrics():
    """Récupère les métriques du cache ou les met à jour si nécessaire"""
    now = datetime.now()
    if (not metrics_cache['last_update'] or 
        now - metrics_cache['last_update'] > metrics_cache['cache_duration']):
        metrics_cache['data'] = monitoring_manager.generate_monitoring_report()
        metrics_cache['last_update'] = now
    return metrics_cache['data']

@app.route('/')
def dashboard():
    """Page principale du dashboard"""
    return render_template('monitoring_dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Endpoint API pour récupérer les métriques"""
    return jsonify(get_cached_metrics())

@app.route('/api/health')
def get_health():
    """Endpoint API pour la santé du système"""
    health_data = monitoring_manager.analyze_system_health()
    return jsonify(health_data)

@app.route('/api/alerts')
def get_alerts():
    """Endpoint API pour les alertes actives"""
    alerts = monitoring_manager.get_active_alerts()
    return jsonify(alerts)

def start_metrics_collection():
    """Démarre la collecte périodique des métriques"""
    def collect_metrics():
        while True:
            try:
                get_cached_metrics()  # Force cache update
                time.sleep(30)  # Attente 30 secondes
            except Exception as e:
                print(f"Error collecting metrics: {str(e)}")

    collection_thread = threading.Thread(
        target=collect_metrics,
        daemon=True
    )
    collection_thread.start()

def run_dashboard(host='0.0.0.0', port=5000):
    """Démarre le serveur dashboard"""
    monitoring_manager.start_monitoring()
    start_metrics_collection()
    app.run(host=host, port=port)

if __name__ == '__main__':
    run_dashboard()
