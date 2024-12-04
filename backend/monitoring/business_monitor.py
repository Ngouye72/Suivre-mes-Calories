from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from prometheus_client import Counter, Gauge, Histogram
from collections import defaultdict

class BusinessMonitor:
    def __init__(self):
        # Métriques utilisateur
        self.active_users = Gauge(
            'nutrition_active_users',
            'Utilisateurs actifs',
            ['user_type']
        )
        
        self.user_engagement = Counter(
            'nutrition_user_engagement',
            'Engagement utilisateur',
            ['action_type']
        )
        
        self.user_retention = Gauge(
            'nutrition_user_retention',
            'Rétention utilisateur',
            ['timeframe']
        )
        
        # Métriques nutrition
        self.meal_logs = Counter(
            'nutrition_meal_logs',
            'Logs de repas',
            ['meal_type']
        )
        
        self.calorie_tracking = Histogram(
            'nutrition_calorie_tracking',
            'Suivi des calories',
            ['meal_type']
        )
        
        self.goal_progress = Gauge(
            'nutrition_goal_progress',
            'Progrès des objectifs',
            ['goal_type']
        )
        
        # Métriques comportement
        self.eating_patterns = Counter(
            'nutrition_eating_patterns',
            'Patterns alimentaires',
            ['pattern_type']
        )
        
        self.habit_tracking = Counter(
            'nutrition_habit_tracking',
            'Suivi des habitudes',
            ['habit_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_user_activity(
        self,
        user_type: str,
        action_type: str
    ):
        """Suit l'activité utilisateur"""
        try:
            # Active users
            self.active_users.labels(
                user_type=user_type
            ).inc()

            # Engagement
            self.user_engagement.labels(
                action_type=action_type
            ).inc()

        except Exception as e:
            self.logger.error(f"Erreur tracking activité: {str(e)}")

    def track_nutrition_metrics(
        self,
        meal_type: str,
        calories: float,
        goal_type: str,
        progress: float
    ):
        """Suit les métriques nutritionnelles"""
        try:
            # Meal logs
            self.meal_logs.labels(
                meal_type=meal_type
            ).inc()

            # Calories
            self.calorie_tracking.labels(
                meal_type=meal_type
            ).observe(calories)

            # Goal progress
            self.goal_progress.labels(
                goal_type=goal_type
            ).set(progress)

        except Exception as e:
            self.logger.error(f"Erreur tracking nutrition: {str(e)}")

    def track_behavior_metrics(
        self,
        pattern_type: str,
        habit_type: str
    ):
        """Suit les métriques comportementales"""
        try:
            # Eating patterns
            self.eating_patterns.labels(
                pattern_type=pattern_type
            ).inc()

            # Habits
            self.habit_tracking.labels(
                habit_type=habit_type
            ).inc()

        except Exception as e:
            self.logger.error(f"Erreur tracking comportement: {str(e)}")

    def analyze_user_metrics(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse les métriques utilisateur"""
        try:
            return {
                "active_users": {
                    user_type: self.active_users.labels(
                        user_type=user_type
                    )._value.get()
                    for user_type in ['free', 'premium']
                },
                "engagement": {
                    action: self.user_engagement.labels(
                        action_type=action
                    )._value.get()
                    for action in ['meal_log', 'weight_update', 'goal_check']
                },
                "retention": {
                    timeframe: self.user_retention.labels(
                        timeframe=timeframe
                    )._value.get()
                    for timeframe in ['7d', '30d', '90d']
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse utilisateur: {str(e)}")
            return {}

    def analyze_nutrition_metrics(self) -> Dict:
        """Analyse les métriques nutritionnelles"""
        try:
            return {
                "meal_logs": {
                    meal_type: self.meal_logs.labels(
                        meal_type=meal_type
                    )._value.get()
                    for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']
                },
                "calories": {
                    meal_type: self.calorie_tracking.labels(
                        meal_type=meal_type
                    )._sum.get() / max(
                        self.calorie_tracking.labels(
                            meal_type=meal_type
                        )._count.get(), 1
                    )
                    for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']
                },
                "goals": {
                    goal_type: self.goal_progress.labels(
                        goal_type=goal_type
                    )._value.get()
                    for goal_type in ['weight', 'calories', 'protein']
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse nutrition: {str(e)}")
            return {}

    def analyze_behavior_metrics(self) -> Dict:
        """Analyse les métriques comportementales"""
        try:
            return {
                "patterns": {
                    pattern: self.eating_patterns.labels(
                        pattern_type=pattern
                    )._value.get()
                    for pattern in ['regular', 'irregular', 'skipping']
                },
                "habits": {
                    habit: self.habit_tracking.labels(
                        habit_type=habit
                    )._value.get()
                    for habit in ['healthy', 'unhealthy']
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur analyse comportement: {str(e)}")
            return {}

    def detect_business_insights(self) -> List[Dict]:
        """Détecte les insights métier"""
        insights = []
        try:
            # Analyse métriques
            user_metrics = self.analyze_user_metrics()
            nutrition_metrics = self.analyze_nutrition_metrics()
            behavior_metrics = self.analyze_behavior_metrics()

            # Insights utilisateur
            premium_ratio = (
                user_metrics["active_users"].get("premium", 0) /
                max(sum(user_metrics["active_users"].values()), 1)
            )
            if premium_ratio < 0.2:
                insights.append({
                    "type": "user",
                    "category": "conversion",
                    "severity": "high",
                    "message": "Faible taux de conversion premium",
                    "value": premium_ratio
                })

            # Insights nutrition
            meal_completion = sum(
                1 for count in nutrition_metrics["meal_logs"].values()
                if count > 0
            ) / len(nutrition_metrics["meal_logs"])
            if meal_completion < 0.8:
                insights.append({
                    "type": "nutrition",
                    "category": "tracking",
                    "severity": "medium",
                    "message": "Tracking repas incomplet",
                    "value": meal_completion
                })

            # Insights comportement
            healthy_ratio = (
                behavior_metrics["habits"].get("healthy", 0) /
                max(sum(behavior_metrics["habits"].values()), 1)
            )
            if healthy_ratio < 0.6:
                insights.append({
                    "type": "behavior",
                    "category": "habits",
                    "severity": "medium",
                    "message": "Proportion habitudes saines faible",
                    "value": healthy_ratio
                })

        except Exception as e:
            self.logger.error(f"Erreur détection insights: {str(e)}")

        return insights

    def generate_business_report(self) -> Dict:
        """Génère un rapport métier"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "user_metrics": self.analyze_user_metrics(),
                "nutrition_metrics": self.analyze_nutrition_metrics(),
                "behavior_metrics": self.analyze_behavior_metrics(),
                "insights": self.detect_business_insights(),
                "recommendations": self._generate_business_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return {}

    def _generate_business_recommendations(self) -> List[Dict]:
        """Génère des recommandations métier"""
        recommendations = []
        try:
            # Analyse insights
            insights = self.detect_business_insights()
            
            # Recommandations utilisateur
            user_insights = [
                insight for insight in insights
                if insight["type"] == "user"
            ]
            if user_insights:
                recommendations.append({
                    "type": "user",
                    "priority": "high",
                    "message": "Améliorer engagement utilisateur",
                    "actions": [
                        "Optimiser onboarding",
                        "Améliorer rétention",
                        "Augmenter conversion"
                    ]
                })

            # Recommandations nutrition
            nutrition_insights = [
                insight for insight in insights
                if insight["type"] == "nutrition"
            ]
            if nutrition_insights:
                recommendations.append({
                    "type": "nutrition",
                    "priority": "medium",
                    "message": "Optimiser tracking nutrition",
                    "actions": [
                        "Simplifier saisie repas",
                        "Ajouter rappels",
                        "Améliorer suggestions"
                    ]
                })

            # Recommandations comportement
            behavior_insights = [
                insight for insight in insights
                if insight["type"] == "behavior"
            ]
            if behavior_insights:
                recommendations.append({
                    "type": "behavior",
                    "priority": "medium",
                    "message": "Encourager habitudes saines",
                    "actions": [
                        "Ajouter coaching",
                        "Gamifier objectifs",
                        "Personnaliser conseils"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur génération recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
business_monitor = BusinessMonitor()

# Tracking activité utilisateur
business_monitor.track_user_activity(
    user_type='premium',
    action_type='meal_log'
)

# Tracking nutrition
business_monitor.track_nutrition_metrics(
    meal_type='lunch',
    calories=600,
    goal_type='calories',
    progress=0.8
)

# Tracking comportement
business_monitor.track_behavior_metrics(
    pattern_type='regular',
    habit_type='healthy'
)

# Analyse métriques
user_metrics = business_monitor.analyze_user_metrics()
nutrition_metrics = business_monitor.analyze_nutrition_metrics()
behavior_metrics = business_monitor.analyze_behavior_metrics()

# Détection insights
insights = business_monitor.detect_business_insights()

# Génération rapport
report = business_monitor.generate_business_report()
"""
