import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import logging

class NutritionCoach:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_goals = {
            'calories': None,
            'proteins': None,
            'carbs': None,
            'fats': None,
            'water': None
        }

    def set_daily_goals(self, goals: Dict[str, float]):
        """Définit les objectifs quotidiens"""
        self.daily_goals.update(goals)

    def get_daily_guidance(self, user_data: Dict) -> Dict:
        """Fournit des conseils quotidiens personnalisés"""
        try:
            # Analyse des données utilisateur
            progress = self._analyze_daily_progress(user_data)
            
            # Génération des conseils
            guidance = {
                'summary': self._generate_daily_summary(progress),
                'recommendations': self._get_recommendations(progress),
                'next_steps': self._suggest_next_steps(progress),
                'motivation': self._generate_motivation_message(progress)
            }

            return guidance

        except Exception as e:
            self.logger.error(f"Error generating daily guidance: {str(e)}")
            return {}

    def _analyze_daily_progress(self, user_data: Dict) -> Dict:
        """Analyse la progression quotidienne"""
        progress = {}
        
        for metric, goal in self.daily_goals.items():
            if goal and metric in user_data:
                current = user_data[metric]
                progress[metric] = {
                    'current': current,
                    'goal': goal,
                    'progress': (current / goal) * 100,
                    'remaining': max(0, goal - current)
                }

        return progress

    def _generate_daily_summary(self, progress: Dict) -> str:
        """Génère un résumé quotidien"""
        summary_parts = []
        
        for metric, data in progress.items():
            if data['progress'] < 100:
                remaining = data['remaining']
                summary_parts.append(
                    f"Il vous reste {remaining:.1f} {metric} à consommer"
                )
            else:
                summary_parts.append(
                    f"Objectif {metric} atteint !"
                )

        return " | ".join(summary_parts)

    def _get_recommendations(self, progress: Dict) -> List[Dict]:
        """Fournit des recommandations personnalisées"""
        recommendations = []
        
        # Recommandations caloriques
        if 'calories' in progress:
            cal_progress = progress['calories']
            if cal_progress['progress'] < 50:
                recommendations.append({
                    'type': 'meal',
                    'priority': 'high',
                    'message': "Pensez à prendre un repas équilibré bientôt"
                })

        # Recommandations protéines
        if 'proteins' in progress:
            prot_progress = progress['proteins']
            if prot_progress['progress'] < 60:
                recommendations.append({
                    'type': 'protein',
                    'priority': 'medium',
                    'message': "Privilégiez les aliments riches en protéines"
                })

        # Recommandations hydratation
        if 'water' in progress:
            water_progress = progress['water']
            if water_progress['progress'] < 70:
                recommendations.append({
                    'type': 'hydration',
                    'priority': 'high',
                    'message': "N'oubliez pas de boire régulièrement"
                })

        return recommendations

    def _suggest_next_steps(self, progress: Dict) -> List[str]:
        """Suggère les prochaines actions"""
        next_steps = []
        
        # Priorité aux objectifs les moins atteints
        sorted_progress = sorted(
            progress.items(),
            key=lambda x: x[1]['progress']
        )
        
        for metric, data in sorted_progress[:3]:
            if data['progress'] < 100:
                next_steps.append(
                    f"Atteindre {data['remaining']:.1f} {metric}"
                )

        return next_steps

    def _generate_motivation_message(self, progress: Dict) -> str:
        """Génère un message motivant"""
        avg_progress = sum(
            d['progress'] for d in progress.values()
        ) / len(progress)
        
        if avg_progress >= 90:
            return "Excellent ! Vous êtes sur la bonne voie !"
        elif avg_progress >= 70:
            return "Continuez comme ça, vous y êtes presque !"
        elif avg_progress >= 50:
            return "Vous avez bien commencé, gardez le rythme !"
        else:
            return "Chaque petit pas compte, continuez vos efforts !"

    def get_weekly_review(self, week_data: List[Dict]) -> Dict:
        """Génère une revue hebdomadaire"""
        try:
            df = pd.DataFrame(week_data)
            
            review = {
                'achievements': self._analyze_achievements(df),
                'trends': self._analyze_weekly_trends(df),
                'suggestions': self._generate_weekly_suggestions(df),
                'next_week_goals': self._set_next_week_goals(df)
            }

            return review

        except Exception as e:
            self.logger.error(f"Error generating weekly review: {str(e)}")
            return {}

    def _analyze_achievements(self, df: pd.DataFrame) -> List[Dict]:
        """Analyse les réussites de la semaine"""
        achievements = []
        
        # Objectifs atteints
        for metric, goal in self.daily_goals.items():
            if goal and metric in df.columns:
                days_achieved = sum(df[metric] >= goal)
                if days_achieved > 0:
                    achievements.append({
                        'metric': metric,
                        'days_achieved': days_achieved,
                        'best_day': df[metric].max()
                    })

        return achievements

    def _analyze_weekly_trends(self, df: pd.DataFrame) -> Dict:
        """Analyse les tendances hebdomadaires"""
        trends = {}
        
        for metric in self.daily_goals.keys():
            if metric in df.columns:
                trend = df[metric].diff().mean()
                trends[metric] = {
                    'direction': 'up' if trend > 0 else 'down',
                    'strength': abs(trend),
                    'consistency': df[metric].std() / df[metric].mean()
                }

        return trends

    def _generate_weekly_suggestions(self, df: pd.DataFrame) -> List[str]:
        """Génère des suggestions pour la semaine suivante"""
        suggestions = []
        
        # Analyse des points faibles
        for metric, goal in self.daily_goals.items():
            if goal and metric in df.columns:
                avg = df[metric].mean()
                if avg < goal:
                    deficit = goal - avg
                    suggestions.append(
                        f"Augmenter {metric} de {deficit:.1f} par jour"
                    )

        return suggestions

    def _set_next_week_goals(self, df: pd.DataFrame) -> Dict:
        """Définit les objectifs pour la semaine suivante"""
        next_goals = {}
        
        for metric, goal in self.daily_goals.items():
            if goal and metric in df.columns:
                current_avg = df[metric].mean()
                if current_avg < goal:
                    # Augmentation progressive
                    next_goals[metric] = min(
                        goal,
                        current_avg * 1.1  # +10% max
                    )
                else:
                    next_goals[metric] = goal

        return next_goals

# Exemple d'utilisation:
"""
coach = NutritionCoach()

# Définir les objectifs
coach.set_daily_goals({
    'calories': 2000,
    'proteins': 80,
    'carbs': 250,
    'fats': 65,
    'water': 2000
})

# Données utilisateur
user_data = {
    'calories': 1500,
    'proteins': 60,
    'carbs': 180,
    'fats': 50,
    'water': 1500
}

# Obtenir des conseils
guidance = coach.get_daily_guidance(user_data)

# Afficher les conseils
print("Résumé:", guidance['summary'])
print("\nRecommandations:")
for rec in guidance['recommendations']:
    print(f"- {rec['message']}")
print("\nProchaines étapes:")
for step in guidance['next_steps']:
    print(f"- {step}")
print("\nMotivation:", guidance['motivation'])
"""
