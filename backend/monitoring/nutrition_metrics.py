from prometheus_client import Counter, Histogram, Gauge, Summary
from functools import wraps
import time

# Métriques pour le suivi des repas
MEAL_COUNTER = Counter(
    'nutrition_meals_total',
    'Total number of meals logged',
    ['meal_type', 'user_id']
)

CALORIES_HISTOGRAM = Histogram(
    'nutrition_calories_per_meal',
    'Distribution of calories per meal',
    ['meal_type'],
    buckets=(0, 200, 400, 600, 800, 1000, 1500, 2000)
)

# Métriques pour le suivi des objectifs
GOAL_PROGRESS_GAUGE = Gauge(
    'nutrition_goal_progress_percent',
    'Progress towards nutritional goals',
    ['goal_type', 'user_id']
)

WEIGHT_TRACKING = Histogram(
    'nutrition_weight_tracking',
    'User weight measurements',
    ['user_id'],
    buckets=(40, 50, 60, 70, 80, 90, 100, 120)
)

# Métriques de performance des calculs nutritionnels
NUTRITION_CALC_DURATION = Summary(
    'nutrition_calculation_duration_seconds',
    'Time spent performing nutrition calculations',
    ['calculation_type']
)

# Métriques d'engagement utilisateur
USER_STREAK_GAUGE = Gauge(
    'nutrition_user_streak_days',
    'Current streak of consecutive days with logged meals',
    ['user_id']
)

DAILY_LOGGING_COUNTER = Counter(
    'nutrition_daily_logs_total',
    'Total number of daily nutrition logs',
    ['log_type', 'user_id']
)

def track_meal(meal_type):
    """Décorateur pour suivre les métriques des repas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user_id=None, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            
            # Incrémenter le compteur de repas
            MEAL_COUNTER.labels(
                meal_type=meal_type,
                user_id=user_id
            ).inc()
            
            # Enregistrer les calories si présentes
            if hasattr(result, 'calories'):
                CALORIES_HISTOGRAM.labels(
                    meal_type=meal_type
                ).observe(result.calories)
            
            # Mesurer le temps de calcul
            duration = time.time() - start_time
            NUTRITION_CALC_DURATION.labels(
                calculation_type=f'meal_{meal_type}'
            ).observe(duration)
            
            return result
        return wrapper
    return decorator

def update_goal_progress(user_id, goal_type, progress):
    """Mettre à jour la progression vers les objectifs"""
    GOAL_PROGRESS_GAUGE.labels(
        goal_type=goal_type,
        user_id=user_id
    ).set(progress)

def track_weight(user_id, weight):
    """Enregistrer une mesure de poids"""
    WEIGHT_TRACKING.labels(
        user_id=user_id
    ).observe(weight)

def update_user_streak(user_id, streak_days):
    """Mettre à jour la série de jours consécutifs"""
    USER_STREAK_GAUGE.labels(
        user_id=user_id
    ).set(streak_days)

def log_daily_nutrition(user_id, log_type):
    """Enregistrer une entrée quotidienne"""
    DAILY_LOGGING_COUNTER.labels(
        log_type=log_type,
        user_id=user_id
    ).inc()

class NutritionMetricsMiddleware:
    """Middleware pour collecter automatiquement les métriques"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Mesurer le temps de réponse
        request_start = time.time()
        
        def custom_start_response(status, headers, exc_info=None):
            # Collecter les métriques de réponse
            duration = time.time() - request_start
            status_code = int(status.split()[0])
            
            # Enregistrer la durée dans le summary approprié
            NUTRITION_CALC_DURATION.labels(
                calculation_type='http_request'
            ).observe(duration)
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Exemples d'utilisation:
"""
@track_meal('breakfast')
def log_breakfast(user_id, meal_data):
    # Logique de journalisation du petit-déjeuner
    pass

# Dans une route Flask
@app.route('/log/weight', methods=['POST'])
def log_weight():
    user_id = get_current_user_id()
    weight = request.json['weight']
    track_weight(user_id, weight)
    return jsonify({'status': 'success'})

# Dans le calcul quotidien des objectifs
def update_daily_goals():
    for user in get_active_users():
        progress = calculate_user_progress(user.id)
        update_goal_progress(user.id, 'daily_calories', progress)
        
# Dans le middleware de l'application
app.wsgi_app = NutritionMetricsMiddleware(app.wsgi_app)
"""
