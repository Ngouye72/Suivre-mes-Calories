from prometheus_client import Counter, Gauge, Histogram, Summary
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class BusinessMetricsCollector:
    def __init__(self):
        # Métriques utilisateurs
        self.active_users = Gauge(
            'nutrition_active_users_total',
            'Nombre total d\'utilisateurs actifs',
            ['timeframe']  # daily, weekly, monthly
        )
        
        self.user_retention = Gauge(
            'nutrition_user_retention_rate',
            'Taux de rétention des utilisateurs',
            ['cohort', 'period']
        )
        
        self.user_engagement = Gauge(
            'nutrition_user_engagement_score',
            'Score d\'engagement utilisateur',
            ['feature']
        )

        # Métriques objectifs
        self.goal_achievement = Gauge(
            'nutrition_goal_achievement_rate',
            'Taux de réussite des objectifs',
            ['goal_type']
        )
        
        self.goal_progress = Histogram(
            'nutrition_goal_progress_distribution',
            'Distribution des progrès vers les objectifs',
            ['goal_type'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )

        # Métriques repas
        self.meal_tracking = Counter(
            'nutrition_meal_logs_total',
            'Nombre total de repas enregistrés',
            ['meal_type']
        )
        
        self.calorie_adherence = Gauge(
            'nutrition_calorie_goal_adherence',
            'Adhérence aux objectifs caloriques',
            ['user_segment']
        )

        # Métriques santé
        self.weight_changes = Histogram(
            'nutrition_weight_changes_kg',
            'Distribution des changements de poids',
            ['goal_type'],
            buckets=[-10, -5, -2, -1, 0, 1, 2, 5, 10]
        )
        
        self.health_markers = Gauge(
            'nutrition_health_markers',
            'Indicateurs de santé',
            ['marker_type']
        )

        # Métriques ML
        self.prediction_accuracy = Gauge(
            'nutrition_ml_prediction_accuracy',
            'Précision des prédictions ML',
            ['model_type']
        )
        
        self.recommendation_adoption = Gauge(
            'nutrition_recommendation_adoption_rate',
            'Taux d\'adoption des recommandations',
            ['recommendation_type']
        )

        # Métriques business
        self.subscription_status = Gauge(
            'nutrition_subscription_status',
            'Statut des abonnements',
            ['plan_type', 'status']
        )
        
        self.revenue_metrics = Gauge(
            'nutrition_revenue_metrics',
            'Métriques de revenus',
            ['metric_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_user_activity(self, timeframe: str, count: int):
        """Suit l'activité des utilisateurs"""
        try:
            self.active_users.labels(timeframe=timeframe).set(count)
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de l'activité utilisateur: {str(e)}")

    def track_retention(self, cohort: str, period: str, rate: float):
        """Suit la rétention des utilisateurs"""
        self.user_retention.labels(cohort=cohort, period=period).set(rate)

    def track_engagement(self, feature: str, score: float):
        """Suit l'engagement par fonctionnalité"""
        self.user_engagement.labels(feature=feature).set(score)

    def track_goal_achievement(self, goal_type: str, rate: float):
        """Suit la réalisation des objectifs"""
        self.goal_achievement.labels(goal_type=goal_type).set(rate)

    def track_goal_progress(self, goal_type: str, progress: float):
        """Suit les progrès vers les objectifs"""
        self.goal_progress.labels(goal_type=goal_type).observe(progress)

    def track_meal(self, meal_type: str):
        """Enregistre un repas"""
        self.meal_tracking.labels(meal_type=meal_type).inc()

    def track_calorie_adherence(self, segment: str, adherence: float):
        """Suit l'adhérence aux objectifs caloriques"""
        self.calorie_adherence.labels(user_segment=segment).set(adherence)

    def track_weight_change(self, goal_type: str, change_kg: float):
        """Suit les changements de poids"""
        self.weight_changes.labels(goal_type=goal_type).observe(change_kg)

    def track_health_marker(self, marker_type: str, value: float):
        """Suit les indicateurs de santé"""
        self.health_markers.labels(marker_type=marker_type).set(value)

    def track_ml_accuracy(self, model_type: str, accuracy: float):
        """Suit la précision des modèles ML"""
        self.prediction_accuracy.labels(model_type=model_type).set(accuracy)

    def track_recommendation_adoption(self, rec_type: str, rate: float):
        """Suit l'adoption des recommandations"""
        self.recommendation_adoption.labels(recommendation_type=rec_type).set(rate)

    def track_subscription(self, plan_type: str, status: str, count: int):
        """Suit les abonnements"""
        self.subscription_status.labels(plan_type=plan_type, status=status).set(count)

    def track_revenue(self, metric_type: str, value: float):
        """Suit les métriques de revenus"""
        self.revenue_metrics.labels(metric_type=metric_type).set(value)

    def calculate_health_score(self, user_data: Dict) -> float:
        """Calcule un score de santé global"""
        try:
            weights = {
                'calorie_adherence': 0.3,
                'goal_progress': 0.3,
                'consistency': 0.2,
                'nutrition_balance': 0.2
            }
            
            score = (
                user_data.get('calorie_adherence', 0) * weights['calorie_adherence'] +
                user_data.get('goal_progress', 0) * weights['goal_progress'] +
                user_data.get('consistency', 0) * weights['consistency'] +
                user_data.get('nutrition_balance', 0) * weights['nutrition_balance']
            )
            
            return min(max(score, 0), 100)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du score de santé: {str(e)}")
            return 0

    def calculate_engagement_score(self, user_activities: Dict) -> float:
        """Calcule un score d'engagement"""
        try:
            weights = {
                'meal_logging': 0.4,
                'goal_setting': 0.2,
                'social_interaction': 0.2,
                'feature_usage': 0.2
            }
            
            score = (
                user_activities.get('meal_logging', 0) * weights['meal_logging'] +
                user_activities.get('goal_setting', 0) * weights['goal_setting'] +
                user_activities.get('social_interaction', 0) * weights['social_interaction'] +
                user_activities.get('feature_usage', 0) * weights['feature_usage']
            )
            
            return min(max(score, 0), 100)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du score d'engagement: {str(e)}")
            return 0

    def analyze_user_segments(self, user_data: List[Dict]) -> Dict[str, float]:
        """Analyse les segments d'utilisateurs"""
        try:
            segments = {
                'weight_loss': [],
                'muscle_gain': [],
                'maintenance': []
            }
            
            for user in user_data:
                goal = user.get('goal_type', 'maintenance')
                if goal in segments:
                    segments[goal].append(user.get('success_rate', 0))
            
            return {
                goal: sum(rates) / len(rates) if rates else 0
                for goal, rates in segments.items()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des segments: {str(e)}")
            return {}

# Exemple d'utilisation:
"""
metrics = BusinessMetricsCollector()

# Suivi activité utilisateur
metrics.track_user_activity('daily', 1000)
metrics.track_user_activity('weekly', 5000)
metrics.track_user_activity('monthly', 15000)

# Suivi objectifs
metrics.track_goal_achievement('weight_loss', 0.75)
metrics.track_goal_progress('weight_loss', 0.8)

# Suivi repas
metrics.track_meal('breakfast')
metrics.track_calorie_adherence('weight_loss', 0.9)

# Suivi santé
metrics.track_weight_change('weight_loss', -2.5)
metrics.track_health_marker('bmi', 24.5)

# Suivi ML
metrics.track_ml_accuracy('meal_recommender', 0.85)
metrics.track_recommendation_adoption('meal_plan', 0.7)

# Suivi business
metrics.track_subscription('premium', 'active', 500)
metrics.track_revenue('mrr', 15000)
"""
