from datetime import datetime, timedelta
import json
import pandas as pd
from typing import Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DailyTracker:
    def __init__(self):
        self.daily_logs = []
        self.water_logs = []
        self.exercise_logs = []

    def log_meal(
        self,
        meal_type: str,
        calories: float,
        proteines: float,
        glucides: float,
        lipides: float,
        aliments: List[str]
    ) -> Dict:
        """Enregistre un repas"""
        log = {
            'timestamp': datetime.now().isoformat(),
            'meal_type': meal_type,
            'calories': calories,
            'proteines': proteines,
            'glucides': glucides,
            'lipides': lipides,
            'aliments': aliments
        }
        self.daily_logs.append(log)
        return self._calculate_daily_progress()

    def log_water(self, quantity_ml: float) -> Dict:
        """Enregistre la consommation d'eau"""
        log = {
            'timestamp': datetime.now().isoformat(),
            'quantity_ml': quantity_ml
        }
        self.water_logs.append(log)
        return self._calculate_hydration_progress()

    def log_exercise(
        self,
        activity: str,
        duration: int,
        intensity: str,
        calories_burned: float
    ) -> Dict:
        """Enregistre une activité physique"""
        log = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'duration': duration,
            'intensity': intensity,
            'calories_burned': calories_burned
        }
        self.exercise_logs.append(log)
        return self._calculate_exercise_progress()

    def get_daily_summary(self) -> Dict:
        """Génère un résumé journalier"""
        nutrition = self._calculate_daily_progress()
        hydration = self._calculate_hydration_progress()
        exercise = self._calculate_exercise_progress()
        
        return {
            'nutrition': nutrition,
            'hydration': hydration,
            'exercise': exercise,
            'recommendations': self._generate_recommendations(
                nutrition,
                hydration,
                exercise
            )
        }

    def generate_daily_report(self) -> str:
        """Génère un rapport journalier détaillé"""
        summary = self.get_daily_summary()
        
        report = "=== RAPPORT JOURNALIER ===\n\n"
        
        # Nutrition
        report += "NUTRITION\n"
        report += f"Calories : {summary['nutrition']['calories']} / {summary['nutrition']['calories_goal']} kcal\n"
        report += f"Protéines : {summary['nutrition']['proteines']} / {summary['nutrition']['proteines_goal']}g\n"
        report += f"Glucides : {summary['nutrition']['glucides']} / {summary['nutrition']['glucides_goal']}g\n"
        report += f"Lipides : {summary['nutrition']['lipides']} / {summary['nutrition']['lipides_goal']}g\n\n"
        
        # Hydratation
        report += "HYDRATATION\n"
        report += f"Eau : {summary['hydration']['total_ml']} / {summary['hydration']['goal_ml']} ml\n\n"
        
        # Exercice
        report += "ACTIVITÉ PHYSIQUE\n"
        report += f"Durée totale : {summary['exercise']['total_duration']} minutes\n"
        report += f"Calories brûlées : {summary['exercise']['calories_burned']} kcal\n\n"
        
        # Recommandations
        report += "RECOMMANDATIONS\n"
        for rec in summary['recommendations']:
            report += f"- {rec}\n"
            
        return report

    def create_progress_visualizations(self) -> Dict:
        """Crée des visualisations de la progression"""
        # Création du subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Calories', 'Macronutriments',
                'Hydratation', 'Activité Physique'
            )
        )

        # Données journalières
        summary = self.get_daily_summary()
        
        # Graphique calories
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=summary['nutrition']['calories'],
                title={'text': "Calories"},
                gauge={'axis': {'range': [None, summary['nutrition']['calories_goal']]},
                       'bar': {'color': "darkblue"}},
                domain={'row': 0, 'column': 0}
            ),
            row=1, col=1
        )

        # Graphique macronutriments
        macros = ['proteines', 'glucides', 'lipides']
        values = [summary['nutrition'][m] for m in macros]
        goals = [summary['nutrition'][f'{m}_goal'] for m in macros]
        
        fig.add_trace(
            go.Bar(
                name='Actuel',
                x=macros,
                y=values,
                marker_color='blue'
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(
                name='Objectif',
                x=macros,
                y=goals,
                marker_color='green'
            ),
            row=1, col=2
        )

        # Graphique hydratation
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=summary['hydration']['total_ml'],
                title={'text': "Hydratation (ml)"},
                gauge={'axis': {'range': [None, summary['hydration']['goal_ml']]},
                       'bar': {'color': "lightblue"}},
                domain={'row': 1, 'column': 0}
            ),
            row=2, col=1
        )

        # Graphique activité physique
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=summary['exercise']['calories_burned'],
                title={'text': "Calories brûlées"},
                domain={'row': 1, 'column': 1}
            ),
            row=2, col=2
        )

        fig.update_layout(height=800, showlegend=True)
        
        return fig.to_dict()

    def _calculate_daily_progress(self) -> Dict:
        """Calcule la progression nutritionnelle journalière"""
        today_logs = [
            log for log in self.daily_logs
            if datetime.fromisoformat(log['timestamp']).date() == datetime.now().date()
        ]
        
        totals = {
            'calories': sum(log['calories'] for log in today_logs),
            'proteines': sum(log['proteines'] for log in today_logs),
            'glucides': sum(log['glucides'] for log in today_logs),
            'lipides': sum(log['lipides'] for log in today_logs)
        }
        
        # Objectifs journaliers (à adapter selon les besoins)
        goals = {
            'calories': 2650,
            'proteines': 230,
            'glucides': 265,
            'lipides': 75
        }
        
        return {**totals, **{f"{k}_goal": v for k, v in goals.items()}}

    def _calculate_hydration_progress(self) -> Dict:
        """Calcule la progression d'hydratation"""
        today_logs = [
            log for log in self.water_logs
            if datetime.fromisoformat(log['timestamp']).date() == datetime.now().date()
        ]
        
        total_ml = sum(log['quantity_ml'] for log in today_logs)
        goal_ml = 3600  # Objectif journalier
        
        return {
            'total_ml': total_ml,
            'goal_ml': goal_ml,
            'progress': (total_ml / goal_ml) * 100 if goal_ml > 0 else 0
        }

    def _calculate_exercise_progress(self) -> Dict:
        """Calcule la progression d'exercice"""
        today_logs = [
            log for log in self.exercise_logs
            if datetime.fromisoformat(log['timestamp']).date() == datetime.now().date()
        ]
        
        return {
            'total_duration': sum(log['duration'] for log in today_logs),
            'calories_burned': sum(log['calories_burned'] for log in today_logs),
            'activities': [log['activity'] for log in today_logs]
        }

    def _generate_recommendations(
        self,
        nutrition: Dict,
        hydration: Dict,
        exercise: Dict
    ) -> List[str]:
        """Génère des recommandations basées sur la progression"""
        recommendations = []
        
        # Recommandations nutrition
        if nutrition['calories'] < nutrition['calories_goal'] * 0.8:
            recommendations.append(
                "Augmentez vos apports caloriques pour atteindre vos objectifs"
            )
        elif nutrition['calories'] > nutrition['calories_goal'] * 1.1:
            recommendations.append(
                "Réduisez légèrement vos apports caloriques"
            )
            
        # Recommandations protéines
        if nutrition['proteines'] < nutrition['proteines_goal'] * 0.8:
            recommendations.append(
                "Privilégiez les sources de protéines dans vos prochains repas"
            )
            
        # Recommandations hydratation
        if hydration['progress'] < 70:
            recommendations.append(
                "Pensez à boire plus régulièrement"
            )
            
        return recommendations

# Exemple d'utilisation
"""
tracker = DailyTracker()

# Enregistrer un repas
tracker.log_meal(
    meal_type="dejeuner",
    calories=800,
    proteines=40,
    glucides=90,
    lipides=20,
    aliments=["Poulet", "Riz", "Légumes"]
)

# Enregistrer consommation d'eau
tracker.log_water(500)

# Enregistrer exercice
tracker.log_exercise(
    activity="Course",
    duration=30,
    intensity="modérée",
    calories_burned=300
)

# Obtenir le résumé
print(tracker.generate_daily_report())
"""
