from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class NutritionMetrics:
    def __init__(self):
        # Métriques d'objectifs
        self.goals_achieved = Counter(
            'nutrition_goals_achieved_total',
            'Nombre total d\'objectifs atteints',
            ['goal_type']
        )
        
        self.goals_progress = Gauge(
            'nutrition_goals_progress',
            'Progression vers les objectifs',
            ['goal_type', 'user_id']
        )
        
        # Métriques de repas
        self.meal_tracking = Counter(
            'nutrition_meals_tracked_total',
            'Nombre total de repas enregistrés',
            ['meal_type']
        )
        
        self.calorie_intake = Histogram(
            'nutrition_calorie_intake',
            'Distribution des apports caloriques',
            ['meal_type']
        )
        
        # Métriques de santé
        self.weight_tracking = Gauge(
            'nutrition_user_weight',
            'Suivi du poids des utilisateurs',
            ['user_id']
        )
        
        self.bmi_tracking = Gauge(
            'nutrition_user_bmi',
            'Suivi de l\'IMC des utilisateurs',
            ['user_id']
        )
        
        # Métriques d'engagement
        self.streak_tracking = Gauge(
            'nutrition_user_streak',
            'Suivi des séries d\'utilisation',
            ['user_id']
        )
        
        self.daily_engagement = Counter(
            'nutrition_daily_engagement_total',
            'Engagement quotidien total',
            ['activity_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_goal_achievement(
        self,
        user_id: str,
        goal_type: str,
        achieved: bool,
        progress: float
    ):
        """Suit la réalisation des objectifs"""
        try:
            if achieved:
                self.goals_achieved.labels(goal_type=goal_type).inc()
            
            self.goals_progress.labels(
                goal_type=goal_type,
                user_id=user_id
            ).set(progress)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi d'objectif: {str(e)}")

    def track_meal(
        self,
        meal_type: str,
        calories: float,
        nutrients: Dict[str, float]
    ):
        """Suit les repas et leur composition"""
        try:
            self.meal_tracking.labels(meal_type=meal_type).inc()
            self.calorie_intake.labels(meal_type=meal_type).observe(calories)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de repas: {str(e)}")

    def track_health_metrics(
        self,
        user_id: str,
        weight: Optional[float] = None,
        height: Optional[float] = None
    ):
        """Suit les métriques de santé"""
        try:
            if weight:
                self.weight_tracking.labels(user_id=user_id).set(weight)
            
            if weight and height:
                bmi = weight / ((height/100) ** 2)
                self.bmi_tracking.labels(user_id=user_id).set(bmi)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi santé: {str(e)}")

    def track_engagement(
        self,
        user_id: str,
        activity_type: str,
        streak_days: Optional[int] = None
    ):
        """Suit l'engagement utilisateur"""
        try:
            self.daily_engagement.labels(
                activity_type=activity_type
            ).inc()
            
            if streak_days is not None:
                self.streak_tracking.labels(
                    user_id=user_id
                ).set(streak_days)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi engagement: {str(e)}")

    def analyze_nutrition_trends(
        self,
        user_id: str,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse les tendances nutritionnelles"""
        try:
            return {
                "goals": self._analyze_goals(user_id, timeframe_days),
                "meals": self._analyze_meals(user_id, timeframe_days),
                "health": self._analyze_health(user_id, timeframe_days),
                "engagement": self._analyze_engagement(user_id, timeframe_days),
                "recommendations": self._generate_recommendations(user_id)
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des tendances: {str(e)}")
            return {}

    def _analyze_goals(self, user_id: str, timeframe_days: int) -> Dict:
        """Analyse la progression des objectifs"""
        try:
            goals_analysis = {
                "achievement_rate": self.goals_achieved._value.get(),
                "current_progress": self.goals_progress.labels(
                    user_id=user_id
                )._value.get(),
                "trend": "improving"  # À calculer selon l'historique
            }
            return goals_analysis
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des objectifs: {str(e)}")
            return {}

    def _analyze_meals(self, user_id: str, timeframe_days: int) -> Dict:
        """Analyse les habitudes alimentaires"""
        try:
            meals_analysis = {
                "total_meals": self.meal_tracking._value.get(),
                "average_calories": self.calorie_intake._sum.get() / 
                                  max(self.calorie_intake._count.get(), 1),
                "meal_distribution": {
                    "breakfast": 0.3,  # À calculer selon les données
                    "lunch": 0.4,
                    "dinner": 0.3
                }
            }
            return meals_analysis
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des repas: {str(e)}")
            return {}

    def _analyze_health(self, user_id: str, timeframe_days: int) -> Dict:
        """Analyse les métriques de santé"""
        try:
            health_analysis = {
                "current_weight": self.weight_tracking.labels(
                    user_id=user_id
                )._value.get(),
                "current_bmi": self.bmi_tracking.labels(
                    user_id=user_id
                )._value.get(),
                "weight_trend": "stable"  # À calculer selon l'historique
            }
            return health_analysis
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse santé: {str(e)}")
            return {}

    def _analyze_engagement(self, user_id: str, timeframe_days: int) -> Dict:
        """Analyse l'engagement utilisateur"""
        try:
            engagement_analysis = {
                "current_streak": self.streak_tracking.labels(
                    user_id=user_id
                )._value.get(),
                "daily_activities": self.daily_engagement._value.get(),
                "engagement_score": 0.8  # À calculer selon plusieurs métriques
            }
            return engagement_analysis
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse engagement: {str(e)}")
            return {}

    def _generate_recommendations(self, user_id: str) -> List[str]:
        """Génère des recommandations personnalisées"""
        recommendations = []
        try:
            # Analyse des objectifs
            progress = self.goals_progress.labels(
                user_id=user_id
            )._value.get()
            if progress < 0.5:
                recommendations.append(
                    "Progression lente vers les objectifs. Considérer un ajustement."
                )

            # Analyse des repas
            avg_calories = (
                self.calorie_intake._sum.get() /
                max(self.calorie_intake._count.get(), 1)
            )
            if avg_calories > 2500:  # Seuil arbitraire
                recommendations.append(
                    "Apport calorique élevé. Revoir les portions."
                )

            # Analyse de l'engagement
            streak = self.streak_tracking.labels(user_id=user_id)._value.get()
            if streak < 3:
                recommendations.append(
                    "Série courte. Maintenir une routine régulière."
                )

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la génération des recommandations: {str(e)}"
            )

        return recommendations

    def generate_health_report(self, user_id: str) -> Dict:
        """Génère un rapport complet sur la santé"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "metrics": {
                    "goals": {
                        "achieved": self.goals_achieved._value.get(),
                        "progress": self.goals_progress.labels(
                            user_id=user_id
                        )._value.get()
                    },
                    "nutrition": {
                        "meals_tracked": self.meal_tracking._value.get(),
                        "average_calories": self.calorie_intake._sum.get() / 
                                         max(self.calorie_intake._count.get(), 1)
                    },
                    "health": {
                        "weight": self.weight_tracking.labels(
                            user_id=user_id
                        )._value.get(),
                        "bmi": self.bmi_tracking.labels(
                            user_id=user_id
                        )._value.get()
                    },
                    "engagement": {
                        "streak": self.streak_tracking.labels(
                            user_id=user_id
                        )._value.get(),
                        "daily_activities": self.daily_engagement._value.get()
                    }
                },
                "analysis": self.analyze_nutrition_trends(user_id),
                "recommendations": self._generate_recommendations(user_id)
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

# Exemple d'utilisation:
"""
nutrition_metrics = NutritionMetrics()

# Suivi d'un objectif
nutrition_metrics.track_goal_achievement(
    user_id="123",
    goal_type="weight_loss",
    achieved=True,
    progress=1.0
)

# Suivi d'un repas
nutrition_metrics.track_meal(
    meal_type="lunch",
    calories=800,
    nutrients={
        "protein": 30,
        "carbs": 100,
        "fat": 25
    }
)

# Suivi métriques santé
nutrition_metrics.track_health_metrics(
    user_id="123",
    weight=70,
    height=175
)

# Suivi engagement
nutrition_metrics.track_engagement(
    user_id="123",
    activity_type="meal_logging",
    streak_days=5
)

# Analyse des tendances
trends = nutrition_metrics.analyze_nutrition_trends(
    user_id="123",
    timeframe_days=30
)

# Génération rapport
report = nutrition_metrics.generate_health_report(user_id="123")
"""
