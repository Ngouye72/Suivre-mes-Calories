from datetime import datetime, timedelta
from models import User, db

class ExerciseTracker:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)

    def calculate_calories_burned(self, activity_type, duration_minutes, intensity='moderate'):
        # MET (Metabolic Equivalent of Task) values for different activities
        met_values = {
            'marche': {'light': 2.5, 'moderate': 3.5, 'vigorous': 4.5},
            'course': {'light': 7.0, 'moderate': 8.3, 'vigorous': 9.8},
            'velo': {'light': 4.0, 'moderate': 6.0, 'vigorous': 8.0},
            'natation': {'light': 5.0, 'moderate': 7.0, 'vigorous': 9.0},
            'yoga': {'light': 2.5, 'moderate': 3.0, 'vigorous': 4.0},
            'musculation': {'light': 3.0, 'moderate': 4.0, 'vigorous': 6.0},
            'hiit': {'light': 6.0, 'moderate': 8.0, 'vigorous': 10.0},
            'danse': {'light': 3.5, 'moderate': 4.5, 'vigorous': 6.0}
        }

        if activity_type not in met_values:
            raise ValueError(f"Type d'activité non reconnu: {activity_type}")

        # Obtenir la valeur MET pour l'activité et l'intensité
        met = met_values[activity_type][intensity]
        
        # Formule de calcul des calories brûlées
        # Calories = MET × poids (kg) × durée (heures)
        weight_kg = self.user.weight or 70  # Utiliser 70kg comme poids par défaut
        duration_hours = duration_minutes / 60
        calories_burned = met * weight_kg * duration_hours
        
        return round(calories_burned)

    def suggest_exercises(self, target_calories=None, available_time=None):
        if target_calories is None:
            # Suggérer des exercices pour brûler 10% des calories quotidiennes
            target_calories = (self.user.target_calories or 2000) * 0.1

        suggestions = []
        base_exercises = {
            'marche': {
                'duration': 30,
                'intensity': 'moderate',
                'description': 'Marche rapide en extérieur ou sur tapis',
                'benefits': ['Accessible à tous', 'Faible impact', 'Améliore l\'endurance'],
                'equipment_needed': ['Chaussures de marche confortables']
            },
            'yoga': {
                'duration': 20,
                'intensity': 'light',
                'description': 'Séance de yoga pour débutants',
                'benefits': ['Améliore la flexibilité', 'Réduit le stress', 'Renforce le corps'],
                'equipment_needed': ['Tapis de yoga']
            },
            'hiit': {
                'duration': 15,
                'intensity': 'vigorous',
                'description': 'Entraînement par intervalles de haute intensité',
                'benefits': ['Brûle beaucoup de calories', 'Améliore la condition physique', 'Court mais efficace'],
                'equipment_needed': []
            }
        }

        for activity, details in base_exercises.items():
            calories = self.calculate_calories_burned(
                activity, 
                details['duration'], 
                details['intensity']
            )
            
            suggestion = {
                'activity': activity,
                'duration': details['duration'],
                'intensity': details['intensity'],
                'calories_burned': calories,
                'description': details['description'],
                'benefits': details['benefits'],
                'equipment_needed': details['equipment_needed']
            }

            if available_time is None or details['duration'] <= available_time:
                suggestions.append(suggestion)

        # Trier par calories brûlées si un objectif est spécifié
        if target_calories:
            suggestions.sort(key=lambda x: abs(x['calories_burned'] - target_calories))

        return suggestions

    def get_weekly_plan(self):
        """Génère un plan d'entraînement hebdomadaire équilibré"""
        weekly_plan = []
        
        # Structure de base pour un plan hebdomadaire
        base_plan = [
            {
                'day': 'Lundi',
                'focus': 'cardio',
                'activities': ['marche', 'course'],
                'intensity': 'moderate',
                'duration': 30
            },
            {
                'day': 'Mardi',
                'focus': 'force',
                'activities': ['musculation'],
                'intensity': 'moderate',
                'duration': 45
            },
            {
                'day': 'Mercredi',
                'focus': 'récupération',
                'activities': ['yoga', 'marche'],
                'intensity': 'light',
                'duration': 20
            },
            {
                'day': 'Jeudi',
                'focus': 'cardio_intense',
                'activities': ['hiit'],
                'intensity': 'vigorous',
                'duration': 20
            },
            {
                'day': 'Vendredi',
                'focus': 'force',
                'activities': ['musculation'],
                'intensity': 'moderate',
                'duration': 45
            },
            {
                'day': 'Samedi',
                'focus': 'endurance',
                'activities': ['velo', 'natation'],
                'intensity': 'moderate',
                'duration': 60
            },
            {
                'day': 'Dimanche',
                'focus': 'repos_actif',
                'activities': ['marche', 'yoga'],
                'intensity': 'light',
                'duration': 30
            }
        ]

        for day_plan in base_plan:
            # Calculer les calories pour chaque activité suggérée
            activities_details = []
            for activity in day_plan['activities']:
                calories = self.calculate_calories_burned(
                    activity,
                    day_plan['duration'],
                    day_plan['intensity']
                )
                
                activities_details.append({
                    'name': activity,
                    'duration': day_plan['duration'],
                    'intensity': day_plan['intensity'],
                    'calories_burned': calories
                })

            weekly_plan.append({
                'day': day_plan['day'],
                'focus': day_plan['focus'],
                'activities': activities_details
            })

        return weekly_plan
