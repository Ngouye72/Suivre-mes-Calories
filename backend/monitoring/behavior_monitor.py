from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class BehaviorMonitor:
    def __init__(self):
        # Métriques des repas
        self.meal_timing = Histogram(
            'nutrition_meal_timing',
            'Distribution horaire des repas',
            ['meal_type']
        )
        
        self.portion_size = Histogram(
            'nutrition_portion_size',
            'Taille des portions',
            ['meal_type', 'food_category']
        )
        
        # Métriques des habitudes
        self.eating_speed = Gauge(
            'nutrition_eating_speed',
            'Vitesse de consommation des repas',
            ['user_id', 'meal_type']
        )
        
        self.meal_regularity = Gauge(
            'nutrition_meal_regularity',
            'Régularité des repas',
            ['user_id']
        )
        
        # Métriques des choix alimentaires
        self.food_choices = Counter(
            'nutrition_food_choices_total',
            'Choix alimentaires',
            ['food_category', 'meal_type']
        )
        
        self.nutrient_balance = Gauge(
            'nutrition_nutrient_balance',
            'Équilibre nutritionnel',
            ['user_id', 'nutrient_type']
        )
        
        # Métriques comportementales
        self.emotional_eating = Counter(
            'nutrition_emotional_eating_total',
            'Épisodes de consommation émotionnelle',
            ['emotion_type']
        )
        
        self.snacking_frequency = Counter(
            'nutrition_snacking_frequency_total',
            'Fréquence des collations',
            ['time_of_day']
        )

        self.logger = logging.getLogger(__name__)

    def track_meal_timing(
        self,
        user_id: str,
        meal_type: str,
        timestamp: datetime
    ):
        """Suit les horaires des repas"""
        try:
            hour = timestamp.hour + timestamp.minute / 60.0
            self.meal_timing.labels(meal_type=meal_type).observe(hour)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi des horaires: {str(e)}")

    def track_portion(
        self,
        meal_type: str,
        food_category: str,
        portion_size: float
    ):
        """Suit les tailles de portion"""
        try:
            self.portion_size.labels(
                meal_type=meal_type,
                food_category=food_category
            ).observe(portion_size)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi des portions: {str(e)}")

    def track_eating_speed(
        self,
        user_id: str,
        meal_type: str,
        duration_minutes: float
    ):
        """Suit la vitesse de consommation"""
        try:
            speed_score = 100 * (1 - min(duration_minutes / 30.0, 1))
            self.eating_speed.labels(
                user_id=user_id,
                meal_type=meal_type
            ).set(speed_score)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de la vitesse: {str(e)}")

    def track_meal_regularity(
        self,
        user_id: str,
        meal_times: List[datetime],
        expected_times: List[datetime]
    ):
        """Suit la régularité des repas"""
        try:
            deviations = []
            for actual, expected in zip(meal_times, expected_times):
                deviation = abs((actual - expected).total_seconds() / 3600)
                deviations.append(deviation)
            
            regularity_score = 100 * (1 - min(np.mean(deviations) / 2.0, 1))
            self.meal_regularity.labels(user_id=user_id).set(regularity_score)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi de la régularité: {str(e)}")

    def track_food_choice(
        self,
        food_category: str,
        meal_type: str
    ):
        """Suit les choix alimentaires"""
        try:
            self.food_choices.labels(
                food_category=food_category,
                meal_type=meal_type
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi des choix: {str(e)}")

    def track_nutrient_balance(
        self,
        user_id: str,
        nutrients: Dict[str, float]
    ):
        """Suit l'équilibre nutritionnel"""
        try:
            for nutrient, value in nutrients.items():
                self.nutrient_balance.labels(
                    user_id=user_id,
                    nutrient_type=nutrient
                ).set(value)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi nutritionnel: {str(e)}")

    def track_emotional_eating(
        self,
        emotion_type: str
    ):
        """Suit la consommation émotionnelle"""
        try:
            self.emotional_eating.labels(
                emotion_type=emotion_type
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi émotionnel: {str(e)}")

    def track_snacking(
        self,
        time_of_day: str
    ):
        """Suit les collations"""
        try:
            self.snacking_frequency.labels(
                time_of_day=time_of_day
            ).inc()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du suivi des collations: {str(e)}")

    def analyze_meal_patterns(
        self,
        user_id: str,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse les patterns de repas"""
        try:
            return {
                "timing": {
                    meal_type: {
                        "mean": self.meal_timing.labels(
                            meal_type=meal_type
                        )._sum.get() / max(
                            self.meal_timing.labels(
                                meal_type=meal_type
                            )._count.get(), 1
                        )
                    }
                    for meal_type in ["breakfast", "lunch", "dinner"]
                },
                "regularity": self.meal_regularity.labels(
                    user_id=user_id
                )._value.get(),
                "eating_speed": {
                    meal_type: self.eating_speed.labels(
                        user_id=user_id,
                        meal_type=meal_type
                    )._value.get()
                    for meal_type in ["breakfast", "lunch", "dinner"]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des patterns: {str(e)}")
            return {}

    def analyze_food_choices(
        self,
        timeframe_days: int = 30
    ) -> Dict:
        """Analyse les choix alimentaires"""
        try:
            return {
                "category_distribution": {
                    category: self.food_choices.labels(
                        food_category=category,
                        meal_type="all"
                    )._value.get()
                    for category in [
                        "vegetables",
                        "proteins",
                        "carbs",
                        "dairy",
                        "snacks"
                    ]
                },
                "meal_type_distribution": {
                    meal_type: self.food_choices.labels(
                        food_category="all",
                        meal_type=meal_type
                    )._value.get()
                    for meal_type in ["breakfast", "lunch", "dinner", "snack"]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des choix: {str(e)}")
            return {}

    def analyze_emotional_patterns(self) -> Dict:
        """Analyse les patterns émotionnels"""
        try:
            return {
                "emotional_triggers": {
                    emotion: self.emotional_eating.labels(
                        emotion_type=emotion
                    )._value.get()
                    for emotion in ["stress", "happiness", "boredom", "anxiety"]
                },
                "snacking_patterns": {
                    time: self.snacking_frequency.labels(
                        time_of_day=time
                    )._value.get()
                    for time in ["morning", "afternoon", "evening", "night"]
                }
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse émotionnelle: {str(e)}")
            return {}

    def generate_behavior_insights(
        self,
        user_id: str
    ) -> List[Dict]:
        """Génère des insights comportementaux"""
        insights = []
        try:
            # Analyse des horaires
            meal_patterns = self.analyze_meal_patterns(user_id)
            if meal_patterns["regularity"] < 70:
                insights.append({
                    "type": "meal_timing",
                    "message": "Irrégularité des repas détectée",
                    "suggestion": "Essayer de maintenir des horaires plus réguliers"
                })

            # Analyse de la vitesse
            if any(speed > 80 for speed in meal_patterns["eating_speed"].values()):
                insights.append({
                    "type": "eating_speed",
                    "message": "Consommation rapide détectée",
                    "suggestion": "Prendre plus de temps pour manger"
                })

            # Analyse émotionnelle
            emotional_patterns = self.analyze_emotional_patterns()
            if sum(emotional_patterns["emotional_triggers"].values()) > 10:
                insights.append({
                    "type": "emotional_eating",
                    "message": "Tendance à la consommation émotionnelle",
                    "suggestion": "Explorer des alternatives à la nourriture"
                })

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération d'insights: {str(e)}")

        return insights

    def generate_behavior_report(
        self,
        user_id: str
    ) -> Dict:
        """Génère un rapport comportemental complet"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "meal_patterns": self.analyze_meal_patterns(user_id),
                "food_choices": self.analyze_food_choices(),
                "emotional_patterns": self.analyze_emotional_patterns(),
                "insights": self.generate_behavior_insights(user_id),
                "recommendations": self._generate_behavior_recommendations(user_id)
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return {}

    def _generate_behavior_recommendations(
        self,
        user_id: str
    ) -> List[Dict]:
        """Génère des recommandations comportementales"""
        recommendations = []
        try:
            # Analyse des patterns
            meal_patterns = self.analyze_meal_patterns(user_id)
            emotional_patterns = self.analyze_emotional_patterns()
            food_choices = self.analyze_food_choices()

            # Recommandations horaires
            if meal_patterns["regularity"] < 70:
                recommendations.append({
                    "type": "timing",
                    "priority": "high",
                    "message": "Établir des horaires de repas réguliers",
                    "actions": [
                        "Définir des heures fixes pour chaque repas",
                        "Utiliser des rappels",
                        "Planifier les repas à l'avance"
                    ]
                })

            # Recommandations émotionnelles
            if sum(emotional_patterns["emotional_triggers"].values()) > 10:
                recommendations.append({
                    "type": "emotional",
                    "priority": "medium",
                    "message": "Gérer la consommation émotionnelle",
                    "actions": [
                        "Tenir un journal alimentaire émotionnel",
                        "Pratiquer la pleine conscience",
                        "Trouver des alternatives à la nourriture"
                    ]
                })

            # Recommandations alimentaires
            if food_choices["category_distribution"].get("vegetables", 0) < 5:
                recommendations.append({
                    "type": "nutrition",
                    "priority": "high",
                    "message": "Augmenter la consommation de légumes",
                    "actions": [
                        "Ajouter des légumes à chaque repas",
                        "Varier les types de légumes",
                        "Préparer des collations à base de légumes"
                    ]
                })

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la génération des recommandations: {str(e)}"
            )

        return recommendations

# Exemple d'utilisation:
"""
behavior_monitor = BehaviorMonitor()

# Suivi des horaires
behavior_monitor.track_meal_timing(
    user_id="123",
    meal_type="breakfast",
    timestamp=datetime.now()
)

# Suivi des portions
behavior_monitor.track_portion(
    meal_type="lunch",
    food_category="proteins",
    portion_size=200
)

# Suivi de la vitesse
behavior_monitor.track_eating_speed(
    user_id="123",
    meal_type="dinner",
    duration_minutes=15
)

# Suivi de la régularité
behavior_monitor.track_meal_regularity(
    user_id="123",
    meal_times=[datetime.now()],
    expected_times=[datetime.now()]
)

# Suivi des choix
behavior_monitor.track_food_choice(
    food_category="vegetables",
    meal_type="lunch"
)

# Suivi nutritionnel
behavior_monitor.track_nutrient_balance(
    user_id="123",
    nutrients={
        "protein": 0.8,
        "carbs": 0.6,
        "fat": 0.7
    }
)

# Analyse des patterns
patterns = behavior_monitor.analyze_meal_patterns(user_id="123")

# Génération d'insights
insights = behavior_monitor.generate_behavior_insights(user_id="123")

# Génération rapport
report = behavior_monitor.generate_behavior_report(user_id="123")
"""
