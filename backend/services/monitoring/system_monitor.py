import psutil
import os
import logging
import json
from datetime import datetime, timedelta
from collections import deque
import threading
import time
from prometheus_client import Gauge, Counter, start_http_server

logger = logging.getLogger(__name__)

# Métriques Prometheus
SYSTEM_CPU = Gauge('system_cpu_percent', 'Utilisation CPU système')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'Utilisation mémoire système')
SYSTEM_DISK = Gauge('system_disk_percent', 'Utilisation disque système')
SYSTEM_NETWORK_IN = Counter('system_network_bytes_in', 'Bytes reçus')
SYSTEM_NETWORK_OUT = Counter('system_network_bytes_out', 'Bytes envoyés')

class SystemMonitor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.history_size = 3600  # 1 heure de données
        self.sampling_interval = 1  # 1 seconde
        
        # Historique des métriques
        self.cpu_history = deque(maxlen=self.history_size)
        self.memory_history = deque(maxlen=self.history_size)
        self.disk_history = deque(maxlen=self.history_size)
        self.network_history = deque(maxlen=self.history_size)
        
        # Démarrage du monitoring
        self.running = False
        self.monitor_thread = None
        
        # Démarrage du serveur Prometheus
        start_http_server(8000)
        
        self._initialized = True
        self.start_monitoring()

    def start_monitoring(self):
        """Démarre le monitoring système"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Arrête le monitoring système"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        """Boucle principale de monitoring"""
        while self.running:
            try:
                metrics = self.collect_metrics()
                self._update_history(metrics)
                self._update_prometheus_metrics(metrics)
                
                # Log des alertes si nécessaire
                self._check_alerts(metrics)
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring: {str(e)}")

    def collect_metrics(self):
        """Collecte les métriques système"""
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            'timestamp': datetime.now(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'errin': network.errin,
                'errout': network.errout,
                'dropin': network.dropin,
                'dropout': network.dropout
            }
        }

    def _update_history(self, metrics):
        """Met à jour l'historique des métriques"""
        self.cpu_history.append((metrics['timestamp'], metrics['cpu']))
        self.memory_history.append((metrics['timestamp'], metrics['memory']))
        self.disk_history.append((metrics['timestamp'], metrics['disk']))
        self.network_history.append((metrics['timestamp'], metrics['network']))

    def _update_prometheus_metrics(self, metrics):
        """Met à jour les métriques Prometheus"""
        SYSTEM_CPU.set(metrics['cpu']['percent'])
        SYSTEM_MEMORY.set(metrics['memory']['percent'])
        SYSTEM_DISK.set(metrics['disk']['percent'])
        SYSTEM_NETWORK_IN.inc(metrics['network']['bytes_recv'])
        SYSTEM_NETWORK_OUT.inc(metrics['network']['bytes_sent'])

    def _check_alerts(self, metrics):
        """Vérifie les seuils d'alerte"""
        # CPU > 80%
        if metrics['cpu']['percent'] > 80:
            logger.warning(f"Alerte CPU: {metrics['cpu']['percent']}%")
            
        # Mémoire > 85%
        if metrics['memory']['percent'] > 85:
            logger.warning(f"Alerte Mémoire: {metrics['memory']['percent']}%")
            
        # Disque > 90%
        if metrics['disk']['percent'] > 90:
            logger.warning(f"Alerte Disque: {metrics['disk']['percent']}%")

    def get_metrics(self, duration=None):
        """Retourne les métriques pour une durée donnée"""
        if duration is None:
            # Dernières métriques
            return self.collect_metrics()
            
        # Calcul de la date de début
        start_time = datetime.now() - duration
        
        # Filtrage des métriques par période
        cpu_data = [m for m in self.cpu_history if m[0] >= start_time]
        memory_data = [m for m in self.memory_history if m[0] >= start_time]
        disk_data = [m for m in self.disk_history if m[0] >= start_time]
        network_data = [m for m in self.network_history if m[0] >= start_time]
        
        return {
            'cpu': cpu_data,
            'memory': memory_data,
            'disk': disk_data,
            'network': network_data
        }

    def get_system_health(self):
        """Retourne l'état de santé du système"""
        metrics = self.collect_metrics()
        
        return {
            'status': self._calculate_health_status(metrics),
            'metrics': metrics,
            'alerts': self._get_current_alerts(metrics)
        }

    def _calculate_health_status(self, metrics):
        """Calcule le statut de santé global"""
        if (metrics['cpu']['percent'] > 90 or
            metrics['memory']['percent'] > 90 or
            metrics['disk']['percent'] > 95):
            return 'critical'
            
        if (metrics['cpu']['percent'] > 80 or
            metrics['memory']['percent'] > 85 or
            metrics['disk']['percent'] > 90):
            return 'warning'
            
        return 'healthy'

    def _get_current_alerts(self, metrics):
        """Retourne les alertes actuelles"""
        alerts = []
        
        if metrics['cpu']['percent'] > 80:
            alerts.append({
                'type': 'cpu',
                'level': 'warning' if metrics['cpu']['percent'] <= 90 else 'critical',
                'value': metrics['cpu']['percent']
            })
            
        if metrics['memory']['percent'] > 85:
            alerts.append({
                'type': 'memory',
                'level': 'warning' if metrics['memory']['percent'] <= 90 else 'critical',
                'value': metrics['memory']['percent']
            })
            
        if metrics['disk']['percent'] > 90:
            alerts.append({
                'type': 'disk',
                'level': 'warning' if metrics['disk']['percent'] <= 95 else 'critical',
                'value': metrics['disk']['percent']
            })
            
        return alerts

    def export_metrics(self, file_path, duration=None):
        """Exporte les métriques vers un fichier"""
        metrics = self.get_metrics(duration)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(metrics, f, default=str)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export des métriques: {str(e)}")
            return False
