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
import os

class TracingConfig:
    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "nutrition-app")
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.jaeger_host = os.getenv("JAEGER_HOST", "localhost")
        self.jaeger_port = int(os.getenv("JAEGER_PORT", "6831"))

    def setup_tracer(self):
        """Configure et initialise le traceur OpenTelemetry"""
        resource = Resource.create({
            "service.name": self.service_name,
            "environment": self.environment
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.jaeger_host,
            agent_port=self.jaeger_port,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        return trace.get_tracer(__name__)

class TracingManager:
    def __init__(self):
        self.config = TracingConfig()
        self.tracer = self.config.setup_tracer()

    def init_app(self, app, db=None, redis_client=None):
        """Initialise le tracing pour une application Flask"""
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()
        
        if db:
            SQLAlchemyInstrumentor().instrument(
                engine=db.engine,
                service=self.config.service_name,
            )
            
        if redis_client:
            RedisInstrumentor().instrument()

    def trace_function(self, name=None):
        """Décorateur pour tracer une fonction"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                operation_name = name or func.__name__
                with self.tracer.start_as_current_span(operation_name) as span:
                    # Ajoute les arguments comme attributs du span
                    for i, arg in enumerate(args):
                        span.set_attribute(f"arg_{i}", str(arg))
                    for key, value in kwargs.items():
                        span.set_attribute(f"kwarg_{key}", str(value))
                    
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        span.set_attribute("error", True)
                        span.set_attribute("error.message", str(e))
                        raise
            return wrapper
        return decorator

    def trace_meal_creation(self, user_id, meal_data):
        """Trace la création d'un repas"""
        with self.tracer.start_as_current_span("create_meal") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("meal.calories", meal_data.get("calories", 0))
            span.set_attribute("meal.type", meal_data.get("type", "unknown"))
            return span

    def trace_user_activity(self, user_id, activity_type):
        """Trace l'activité d'un utilisateur"""
        with self.tracer.start_as_current_span("user_activity") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("activity.type", activity_type)
            return span

    def trace_nutrition_calculation(self, user_id, calculation_type):
        """Trace les calculs nutritionnels"""
        with self.tracer.start_as_current_span("nutrition_calculation") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("calculation.type", calculation_type)
            return span

# Création d'une instance globale du gestionnaire de tracing
tracing_manager = TracingManager()

# Exemple d'utilisation des décorateurs
@tracing_manager.trace_function("process_meal")
def process_meal(user_id, meal_data):
    # Logique de traitement des repas
    pass

@tracing_manager.trace_function("calculate_daily_calories")
def calculate_daily_calories(user_id):
    # Logique de calcul des calories
    pass
