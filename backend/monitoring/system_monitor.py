from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import psutil
import os
import numpy as np
import pandas as pd

class SystemMonitor:
    def __init__(self):
        # Métriques CPU
        self.cpu_usage = Gauge(
            'nutrition_cpu_usage',
            'Utilisation CPU',
            ['core']
        )
        
        self.cpu_temperature = Gauge(
            'nutrition_cpu_temperature',
            'Température CPU',
            ['core']
        )
        
        # Métriques Mémoire
        self.memory_usage = Gauge(
            'nutrition_memory_usage',
            'Utilisation mémoire',
            ['type']
        )
        
        self.memory_available = Gauge(
            'nutrition_memory_available',
            'Mémoire disponible',
            ['type']
        )
        
        # Métriques Disque
        self.disk_usage = Gauge(
            'nutrition_disk_usage',
            'Utilisation disque',
            ['mount_point']
        )
        
        self.disk_io = Counter(
            'nutrition_disk_io_total',
            'Opérations IO disque',
            ['operation']
        )
        
        # Métriques Réseau
        self.network_traffic = Counter(
            'nutrition_network_traffic_total',
            'Trafic réseau',
            ['direction']
        )
        
        self.network_errors = Counter(
            'nutrition_network_error_total',
            'Erreurs réseau',
            ['type']
        )
        
        # Métriques Application
        self.app_threads = Gauge(
            'nutrition_app_threads',
            'Threads application',
            ['state']
        )
        
        self.app_connections = Gauge(
            'nutrition_app_connections',
            'Connexions application',
            ['type']
        )

        self.logger = logging.getLogger(__name__)

    def monitor_cpu(self):
        """Surveille l'utilisation CPU"""
        try:
            # Utilisation par core
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
                self.cpu_usage.labels(core=f"core_{i}").set(percentage)
            
            # Température si disponible
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for i, entry in enumerate(entries):
                            self.cpu_temperature.labels(
                                core=f"{name}_{i}"
                            ).set(entry.current)
                            
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring CPU: {str(e)}")

    def monitor_memory(self):
        """Surveille l'utilisation mémoire"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Mémoire virtuelle
            self.memory_usage.labels(type="virtual").set(
                memory.percent
            )
            self.memory_available.labels(type="virtual").set(
                memory.available
            )
            
            # Mémoire swap
            self.memory_usage.labels(type="swap").set(
                swap.percent
            )
            self.memory_available.labels(type="swap").set(
                swap.free
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring mémoire: {str(e)}")

    def monitor_disk(self):
        """Surveille l'utilisation disque"""
        try:
            # Utilisation par point de montage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    self.disk_usage.labels(
                        mount_point=partition.mountpoint
                    ).set(usage.percent)
                except Exception:
                    continue
            
            # IO disque
            io_counters = psutil.disk_io_counters()
            if io_counters:
                self.disk_io.labels(operation="read").inc(
                    io_counters.read_count
                )
                self.disk_io.labels(operation="write").inc(
                    io_counters.write_count
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring disque: {str(e)}")

    def monitor_network(self):
        """Surveille le trafic réseau"""
        try:
            net_counters = psutil.net_io_counters()
            
            # Trafic
            self.network_traffic.labels(direction="sent").inc(
                net_counters.bytes_sent
            )
            self.network_traffic.labels(direction="received").inc(
                net_counters.bytes_recv
            )
            
            # Erreurs
            self.network_errors.labels(type="in").inc(
                net_counters.errin
            )
            self.network_errors.labels(type="out").inc(
                net_counters.errout
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring réseau: {str(e)}")

    def monitor_application(self):
        """Surveille l'état de l'application"""
        try:
            current_process = psutil.Process()
            
            # Threads
            threads = current_process.threads()
            running_threads = sum(1 for t in threads if t.status == "running")
            waiting_threads = len(threads) - running_threads
            
            self.app_threads.labels(state="running").set(running_threads)
            self.app_threads.labels(state="waiting").set(waiting_threads)
            
            # Connexions
            connections = current_process.connections()
            established = sum(1 for c in connections if c.status == "ESTABLISHED")
            listening = sum(1 for c in connections if c.status == "LISTEN")
            
            self.app_connections.labels(type="established").set(established)
            self.app_connections.labels(type="listening").set(listening)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du monitoring application: {str(e)}")

    def analyze_system_health(self) -> Dict:
        """Analyse la santé du système"""
        try:
            return {
                "cpu": {
                    "usage": {
                        f"core_{i}": self.cpu_usage.labels(
                            core=f"core_{i}"
                        )._value.get()
                        for i in range(psutil.cpu_count())
                    },
                    "temperature": {
                        core: self.cpu_temperature.labels(
                            core=core
                        )._value.get()
                        for core in ["cpu_0", "cpu_1"]  # Exemple
                    }
                },
                "memory": {
                    "virtual": {
                        "usage": self.memory_usage.labels(
                            type="virtual"
                        )._value.get(),
                        "available": self.memory_available.labels(
                            type="virtual"
                        )._value.get()
                    },
                    "swap": {
                        "usage": self.memory_usage.labels(
                            type="swap"
                        )._value.get(),
                        "available": self.memory_available.labels(
                            type="swap"
                        )._value.get()
                    }
                },
                "disk": {
                    "usage": {
                        mount: self.disk_usage.labels(
                            mount_point=mount
                        )._value.get()
                        for mount in ["/", "/home"]  # Exemple
                    },
                    "io": {
                        "read": self.disk_io.labels(
                            operation="read"
                        )._value.get(),
                        "write": self.disk_io.labels(
                            operation="write"
                        )._value.get()
                    }
                },
                "network": {
                    "traffic": {
                        "sent": self.network_traffic.labels(
                            direction="sent"
                        )._value.get(),
                        "received": self.network_traffic.labels(
                            direction="received"
                        )._value.get()
                    },
                    "errors": {
                        "in": self.network_errors.labels(
                            type="in"
                        )._value.get(),
                        "out": self.network_errors.labels(
                            type="out"
                        )._value.get()
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse système: {str(e)}")
            return {}

    def generate_system_insights(self) -> List[Dict]:
        """Génère des insights système"""
        insights = []
        try:
            # Analyse CPU
            for i in range(psutil.cpu_count()):
                usage = self.cpu_usage.labels(
                    core=f"core_{i}"
                )._value.get()
                if usage > 80:
                    insights.append({
                        "type": "cpu",
                        "severity": "high",
                        "message": f"Utilisation CPU élevée sur core_{i}",
                        "value": usage
                    })

            # Analyse Mémoire
            mem_usage = self.memory_usage.labels(
                type="virtual"
            )._value.get()
            if mem_usage > 90:
                insights.append({
                    "type": "memory",
                    "severity": "high",
                    "message": "Utilisation mémoire critique",
                    "value": mem_usage
                })

            # Analyse Disque
            for mount in ["/", "/home"]:  # Exemple
                usage = self.disk_usage.labels(
                    mount_point=mount
                )._value.get()
                if usage > 85:
                    insights.append({
                        "type": "disk",
                        "severity": "medium",
                        "message": f"Espace disque faible sur {mount}",
                        "value": usage
                    })

            # Analyse Réseau
            error_rate = (
                self.network_errors.labels(type="in")._value.get() +
                self.network_errors.labels(type="out")._value.get()
            )
            if error_rate > 100:
                insights.append({
                    "type": "network",
                    "severity": "high",
                    "message": "Taux d'erreurs réseau élevé",
                    "value": error_rate
                })

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération d'insights: {str(e)}")

        return insights

    def generate_system_report(self) -> Dict:
        """Génère un rapport système complet"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": self.analyze_system_health(),
                "insights": self.generate_system_insights(),
                "recommendations": self._generate_system_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_system_recommendations(self) -> List[Dict]:
        """Génère des recommandations système"""
        recommendations = []
        try:
            system_health = self.analyze_system_health()
            
            # Recommandations CPU
            high_cpu_cores = [
                core for core, usage 
                in system_health["cpu"]["usage"].items()
                if usage > 80
            ]
            if high_cpu_cores:
                recommendations.append({
                    "type": "cpu",
                    "priority": "high",
                    "message": "Optimiser l'utilisation CPU",
                    "actions": [
                        "Identifier les processus gourmands",
                        "Optimiser le code des fonctions intensives",
                        "Considérer la mise à l'échelle horizontale"
                    ]
                })

            # Recommandations Mémoire
            if system_health["memory"]["virtual"]["usage"] > 90:
                recommendations.append({
                    "type": "memory",
                    "priority": "high",
                    "message": "Optimiser l'utilisation mémoire",
                    "actions": [
                        "Implémenter du caching",
                        "Optimiser les requêtes database",
                        "Augmenter la mémoire disponible"
                    ]
                })

            # Recommandations Disque
            high_disk_mounts = [
                mount for mount, usage 
                in system_health["disk"]["usage"].items()
                if usage > 85
            ]
            if high_disk_mounts:
                recommendations.append({
                    "type": "disk",
                    "priority": "medium",
                    "message": "Gérer l'espace disque",
                    "actions": [
                        "Nettoyer les fichiers temporaires",
                        "Archiver les anciennes données",
                        "Augmenter l'espace disque"
                    ]
                })

            # Recommandations Réseau
            if system_health["network"]["errors"]["in"] > 100:
                recommendations.append({
                    "type": "network",
                    "priority": "high",
                    "message": "Améliorer la stabilité réseau",
                    "actions": [
                        "Vérifier la configuration réseau",
                        "Optimiser les connexions",
                        "Mettre à jour les pilotes"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la génération des recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
system_monitor = SystemMonitor()

# Monitoring continu
while True:
    try:
        # Monitoring des ressources
        system_monitor.monitor_cpu()
        system_monitor.monitor_memory()
        system_monitor.monitor_disk()
        system_monitor.monitor_network()
        system_monitor.monitor_application()
        
        # Analyse et rapports
        health_analysis = system_monitor.analyze_system_health()
        insights = system_monitor.generate_system_insights()
        report = system_monitor.generate_system_report()
        
        # Attente avant prochain cycle
        time.sleep(60)
        
    except Exception as e:
        logging.error(f"Erreur dans le cycle de monitoring: {str(e)}")
        time.sleep(5)
"""
