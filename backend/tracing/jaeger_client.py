from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from functools import wraps
import time

class TracingManager:
    def __init__(self, app_name="nutrition-app"):
        self.app_name = app_name
        self.setup_tracer()
        
    def setup_tracer(self):
        """Configure le traceur OpenTelemetry avec Jaeger"""
        resource = Resource.create({"service.name": self.app_name})
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        self.tracer = trace.get_tracer(__name__)
    
    def init_app(self, app, db=None, redis_client=None):
        """Initialise le tracing pour une application Flask"""
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        
        if db:
            SQLAlchemyInstrumentor().instrument(
                engine=db.engine,
                service="nutrition-db",
            )
            
        if redis_client:
            RedisInstrumentor().instrument(
                tracer_provider=trace.get_tracer_provider(),
            )
    
    def trace_function(self, name=None, attributes=None):
        """Décorateur pour tracer une fonction"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                function_name = name or func.__name__
                with self.tracer.start_as_current_span(
                    function_name,
                    attributes=attributes
                ) as span:
                    try:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        # Ajouter des attributs de performance
                        span.set_attribute("duration_seconds", duration)
                        
                        # Ajouter des attributs spécifiques à la nutrition
                        if "meal" in function_name.lower():
                            if hasattr(result, "calories"):
                                span.set_attribute("meal.calories", result.calories)
                            if hasattr(result, "meal_type"):
                                span.set_attribute("meal.type", result.meal_type)
                        
                        return result
                    except Exception as e:
                        # Enregistrer l'erreur dans la trace
                        span.set_status(trace.Status(
                            trace.StatusCode.ERROR,
                            str(e)
                        ))
                        span.record_exception(e)
                        raise
            return wrapper
        return decorator

    def trace_meal_calculation(self, meal_type, user_id):
        """Trace spécifique pour les calculs de repas"""
        return self.trace_function(
            name="calculate_meal_nutrition",
            attributes={
                "meal.type": meal_type,
                "user.id": user_id,
                "calculation.type": "nutrition"
            }
        )

    def trace_user_activity(self, activity_type):
        """Trace pour les activités utilisateur"""
        return self.trace_function(
            name=f"user_activity_{activity_type}",
            attributes={
                "activity.type": activity_type,
                "activity.timestamp": time.time()
            }
        )

# Exemple d'utilisation:
"""
tracing = TracingManager()

# Dans votre application Flask
app = Flask(__name__)
tracing.init_app(app, db, redis_client)

# Tracer une fonction
@tracing.trace_function(name="create_meal")
def create_meal(meal_data):
    # Logique de création de repas
    pass

# Tracer un calcul de repas
@tracing.trace_meal_calculation(meal_type="breakfast", user_id="123")
def calculate_breakfast_nutrition(meal_data):
    # Calculs nutritionnels
    pass

# Tracer une activité utilisateur
@tracing.trace_user_activity("weight_log")
def log_user_weight(weight_data):
    # Enregistrement du poids
    pass
"""
