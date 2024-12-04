from flask import request, g
from functools import wraps
import time
from .custom_metrics import metrics, MetricData

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
        self.init_metrics_hooks()
    
    def init_metrics_hooks(self):
        @self.app.before_request
        def start_timer():
            g.start_time = time.time()
        
        @self.app.after_request
        def log_request(response):
            # Temps de réponse
            duration = time.time() - g.start_time
            metrics.add_metric(MetricData(
                name="RequestDuration",
                value=duration,
                unit="Seconds",
                dimensions={
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "status": str(response.status_code)
                }
            ))
            
            # Compteur de requêtes
            metrics.add_metric(MetricData(
                name="RequestCount",
                value=1,
                unit="Count",
                dimensions={
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "status": str(response.status_code)
                }
            ))
            
            return response
        
        @self.app.teardown_request
        def flush_metrics(exception=None):
            if exception:
                metrics.add_metric(MetricData(
                    name="RequestError",
                    value=1,
                    unit="Count",
                    dimensions={
                        "endpoint": request.endpoint,
                        "error_type": type(exception).__name__
                    }
                ))
            metrics.flush()

def track_endpoint_metrics(name=None):
    """Décorateur pour suivre les métriques d'un endpoint spécifique"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            endpoint_name = name or f.__name__
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                metrics.add_metric(MetricData(
                    name="EndpointDuration",
                    value=duration,
                    unit="Seconds",
                    dimensions={
                        "endpoint": endpoint_name,
                        "status": "success"
                    }
                ))
                
                return result
                
            except Exception as e:
                metrics.add_metric(MetricData(
                    name="EndpointError",
                    value=1,
                    unit="Count",
                    dimensions={
                        "endpoint": endpoint_name,
                        "error_type": type(e).__name__
                    }
                ))
                raise
                
        return wrapped
    return decorator

# Exemple d'utilisation:
"""
from flask import Flask
from monitoring.metrics_middleware import MetricsMiddleware, track_endpoint_metrics

app = Flask(__name__)
MetricsMiddleware(app)

@app.route('/meals', methods=['POST'])
@track_endpoint_metrics('create_meal')
def create_meal():
    # Logique de l'endpoint
    return {"status": "success"}
"""
