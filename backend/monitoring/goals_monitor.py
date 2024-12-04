from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

class GoalsMonitor:
    def __init__(self):
        # Métriques de prédiction
        self.prediction_accuracy = Gauge(
            'nutrition_prediction_accuracy',
            'Précision des prédictions nutritionnelles',
            ['prediction_type']
        )
        
        self.prediction_error = Histogram(
            'nutrition_prediction_error',
            'Erreur des prédictions',
            ['prediction_type']
        )
        
        # Métriques d'objectifs
        self.goal_completion = Counter(
            'nutrition_goal_completion_total',
            'Complétion des objectifs',
            ['goal_type', 'difficulty']
        )
        
        self.goal_adherence = Gauge(
            'nutrition_goal_adherence',
            'Adhérence aux objectifs',
            ['user_id', 'goal_type']
        )
        
        # Métriques de progression
        self.weight_progress = Gauge(
            'nutrition_weight_progress',
            'Progression du poids',
            ['user_id']
        )
        
        self.calorie_target = Gauge(
            'nutrition_calorie_target',
            'Objectif calorique',
            ['user_id']
        )

        # Métriques de recommandations
        self.recommendation_relevance = Gauge(
            'nutrition_recommendation_relevance',
            'Pertinence des recommandations',
            ['recommendation_type']
        )
        
        self.recommendation_adoption = Counter(
            'nutrition_recommendation_adoption_total',
            'Adoption des recommandations',
            ['recommendation_type']
        )

        self.logger = logging.getLogger(__name__)

    def track_prediction(
        self,
        prediction_type: str,
        predicted: float,
        actual: float
    ):
        """Suit la précision des prédictions"""
        try:
            error = abs(predicted - actual)
            self.prediction_error.labels(
                prediction_type=prediction_type
            ).observe(error)
            
            accuracy = max(0, 1 - error/actual)
            self.prediction_accuracy.labels(
                prediction_type=prediction_type
            ).set(accuracy)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de prédiction: {str(e)}")

    def track_goal_progress(
        self,
        user_id: str,
        goal_type: str,
        difficulty: str,
        progress: float,
        completed: bool = False
    ):
        """Suit la progression vers les objectifs"""
        try:
            if completed:
                self.goal_completion.labels(
                    goal_type=goal_type,
                    difficulty=difficulty
                ).inc()
            
            self.goal_adherence.labels(
                user_id=user_id,
                goal_type=goal_type
            ).set(progress)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi d'objectif: {str(e)}")

    def track_weight_progress(
        self,
        user_id: str,
        current_weight: float,
        target_weight: float
    ):
        """Suit la progression du poids"""
        try:
            progress = (target_weight - current_weight) / target_weight
            self.weight_progress.labels(user_id=user_id).set(progress)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi du poids: {str(e)}")

    def track_calorie_target(
        self,
        user_id: str,
        target: float,
        actual: float
    ):
        """Suit l'adhérence aux objectifs caloriques"""
        try:
            adherence = actual / target
            self.calorie_target.labels(user_id=user_id).set(adherence)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi calorique: {str(e)}")

    def track_recommendation(
        self,
        recommendation_type: str,
        relevance_score: float,
        adopted: bool = False
    ):
        """Suit l'efficacité des recommandations"""
        try:
            self.recommendation_relevance.labels(
                recommendation_type=recommendation_type
            ).set(relevance_score)
            
            if adopted:
                self.recommendation_adoption.labels(
                    recommendation_type=recommendation_type
                ).inc()
                
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de recommandation: {str(e)}")

    def analyze_predictions(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse la qualité des prédictions"""
        try:
            analysis = {
                "accuracy": {
                    pred_type: self.prediction_accuracy.labels(
                        prediction_type=pred_type
                    )._value.get()
                    for pred_type in ["weight", "calories", "nutrients"]
                },
                "error_distribution": {
                    "mean": self.prediction_error._sum.get() / 
                           max(self.prediction_error._count.get(), 1),
                    "count": self.prediction_error._count.get()
                }
            }
            return analysis
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des prédictions: {str(e)}")
            return {}

    def analyze_goal_achievement(
        self,
        user_id: str,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse la réalisation des objectifs"""
        try:
            return {
                "completion_rate": {
                    goal_type: self.goal_completion.labels(
                        goal_type=goal_type,
                        difficulty="medium"
                    )._value.get()
                    for goal_type in ["weight", "calories", "activity"]
                },
                "adherence": self.goal_adherence.labels(
                    user_id=user_id,
                    goal_type="overall"
                )._value.get(),
                "weight_progress": self.weight_progress.labels(
                    user_id=user_id
                )._value.get()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des objectifs: {str(e)}")
            return {}

    def analyze_recommendations(self) -> Dict:
        """Analyse l'efficacité des recommandations"""
        try:
            return {
                "relevance": {
                    rec_type: self.recommendation_relevance.labels(
                        recommendation_type=rec_type
                    )._value.get()
                    for rec_type in ["diet", "activity", "habits"]
                },
                "adoption_rate": {
                    rec_type: self.recommendation_adoption.labels(
                        recommendation_type=rec_type
                    )._value.get()
                    for rec_type in ["diet", "activity", "habits"]
                }
            }
        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'analyse des recommandations: {str(e)}"
            )
            return {}

    def generate_personalized_insights(
        self,
        user_id: str,
        user_data: Dict
    ) -> List[Dict]:
        """Génère des insights personnalisés"""
        insights = []
        try:
            # Analyse des objectifs
            goal_analysis = self.analyze_goal_achievement(user_id)
            if goal_analysis["adherence"] < 0.7:
                insights.append({
                    "type": "goal_adjustment",
                    "message": "Objectifs potentiellement trop ambitieux",
                    "suggestion": "Considérer des objectifs intermédiaires"
                })

            # Analyse du poids
            weight_progress = self.weight_progress.labels(
                user_id=user_id
            )._value.get()
            if abs(weight_progress) < 0.1:
                insights.append({
                    "type": "weight_plateau",
                    "message": "Plateau de poids détecté",
                    "suggestion": "Ajuster l'apport calorique ou l'activité"
                })

            # Analyse calorique
            calorie_adherence = self.calorie_target.labels(
                user_id=user_id
            )._value.get()
            if calorie_adherence > 1.1:
                insights.append({
                    "type": "calorie_excess",
                    "message": "Dépassement régulier des calories",
                    "suggestion": "Revoir les portions et les choix alimentaires"
                })

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération d'insights: {str(e)}")

        return insights

    def generate_prediction_report(self) -> Dict:
        """Génère un rapport sur la qualité des prédictions"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "prediction_metrics": {
                    "accuracy": {
                        pred_type: self.prediction_accuracy.labels(
                            prediction_type=pred_type
                        )._value.get()
                        for pred_type in ["weight", "calories", "nutrients"]
                    },
                    "error_stats": {
                        "mean": self.prediction_error._sum.get() / 
                               max(self.prediction_error._count.get(), 1),
                        "count": self.prediction_error._count.get()
                    }
                },
                "recommendation_metrics": self.analyze_recommendations(),
                "model_health": self._assess_model_health(),
                "recommendations": self._generate_model_recommendations()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _assess_model_health(self) -> Dict:
        """Évalue la santé globale des modèles"""
        try:
            return {
                "prediction_quality": "good" if self.prediction_accuracy._value.get() > 0.8 else "needs_improvement",
                "recommendation_quality": "good" if self.recommendation_relevance._value.get() > 0.7 else "needs_improvement",
                "data_quality": "good"  # À implémenter avec des métriques de qualité des données
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'évaluation des modèles: {str(e)}")
            return {}

    def _generate_model_recommendations(self) -> List[str]:
        """Génère des recommandations pour l'amélioration des modèles"""
        recommendations = []
        try:
            # Analyse de la précision
            avg_accuracy = np.mean([
                self.prediction_accuracy.labels(
                    prediction_type=pt
                )._value.get()
                for pt in ["weight", "calories", "nutrients"]
            ])
            if avg_accuracy < 0.8:
                recommendations.append(
                    "Envisager un retraining des modèles de prédiction"
                )

            # Analyse des recommandations
            avg_relevance = np.mean([
                self.recommendation_relevance.labels(
                    recommendation_type=rt
                )._value.get()
                for rt in ["diet", "activity", "habits"]
            ])
            if avg_relevance < 0.7:
                recommendations.append(
                    "Améliorer la pertinence des recommandations"
                )

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la génération des recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
goals_monitor = GoalsMonitor()

# Suivi d'une prédiction
goals_monitor.track_prediction(
    prediction_type="weight",
    predicted=75.0,
    actual=74.5
)

# Suivi d'un objectif
goals_monitor.track_goal_progress(
    user_id="123",
    goal_type="weight_loss",
    difficulty="medium",
    progress=0.7,
    completed=False
)

# Suivi du poids
goals_monitor.track_weight_progress(
    user_id="123",
    current_weight=75,
    target_weight=70
)

# Suivi des calories
goals_monitor.track_calorie_target(
    user_id="123",
    target=2000,
    actual=1900
)

# Analyse des prédictions
prediction_analysis = goals_monitor.analyze_predictions()

# Analyse des objectifs
goal_analysis = goals_monitor.analyze_goal_achievement(user_id="123")

# Génération d'insights
insights = goals_monitor.generate_personalized_insights(
    user_id="123",
    user_data={}
)

# Génération rapport
report = goals_monitor.generate_prediction_report()
"""
