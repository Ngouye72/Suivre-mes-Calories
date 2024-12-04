from datetime import datetime, timedelta
from models import User, FoodEntry, db

class SocialFeatures:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)

    def get_achievements(self):
        """Calcule et retourne les succès de l'utilisateur"""
        achievements = []
        
        # Vérifier la régularité d'enregistrement
        streak = self._calculate_streak()
        if streak >= 7:
            achievements.append({
                'type': 'streak',
                'title': 'Régulier comme une horloge !',
                'description': f'Vous avez enregistré vos repas pendant {streak} jours consécutifs !',
                'icon': '🔥',
                'value': streak
            })

        # Vérifier l'atteinte des objectifs caloriques
        goals_met = self._calculate_goals_met()
        if goals_met >= 5:
            achievements.append({
                'type': 'goals',
                'title': 'Objectifs atteints',
                'description': f'Vous avez atteint vos objectifs caloriques {goals_met} fois !',
                'icon': '🎯',
                'value': goals_met
            })

        # Vérifier la variété alimentaire
        variety_score = self._calculate_variety_score()
        if variety_score >= 0.8:
            achievements.append({
                'type': 'variety',
                'title': 'Gourmet équilibré',
                'description': 'Vous avez une excellente variété dans votre alimentation !',
                'icon': '🥗',
                'value': variety_score
            })

        return achievements

    def _calculate_streak(self):
        """Calcule le nombre de jours consécutifs d'enregistrement"""
        streak = 0
        current_date = datetime.now().date()
        
        while True:
            entries = FoodEntry.query.filter(
                FoodEntry.user_id == self.user.id,
                FoodEntry.date == current_date
            ).first()
            
            if not entries:
                break
                
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak

    def _calculate_goals_met(self):
        """Calcule le nombre de fois où les objectifs caloriques ont été atteints"""
        last_week = datetime.now() - timedelta(days=7)
        daily_calories = db.session.query(
            db.func.date(FoodEntry.date),
            db.func.sum(FoodEntry.calories)
        ).filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= last_week
        ).group_by(
            db.func.date(FoodEntry.date)
        ).all()

        goals_met = 0
        target_calories = self.user.target_calories or 2000
        margin = target_calories * 0.1  # 10% de marge

        for _, calories in daily_calories:
            if abs(calories - target_calories) <= margin:
                goals_met += 1

        return goals_met

    def _calculate_variety_score(self):
        """Calcule un score de variété alimentaire"""
        last_week = datetime.now() - timedelta(days=7)
        food_entries = FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= last_week
        ).all()

        unique_foods = set(entry.food_name for entry in food_entries)
        total_entries = len(food_entries)

        if total_entries == 0:
            return 0

        return len(unique_foods) / total_entries

    def get_challenges(self):
        """Retourne les défis disponibles pour l'utilisateur"""
        challenges = [
            {
                'id': 'streak_7',
                'title': 'Semaine parfaite',
                'description': 'Enregistrez vos repas pendant 7 jours consécutifs',
                'reward': 'Badge Régularité',
                'progress': min(self._calculate_streak() / 7, 1),
                'icon': '📅'
            },
            {
                'id': 'variety_10',
                'title': 'Explorateur culinaire',
                'description': 'Essayez 10 nouveaux aliments cette semaine',
                'reward': 'Badge Diversité',
                'progress': min(len(self._get_unique_foods_this_week()) / 10, 1),
                'icon': '🍽️'
            },
            {
                'id': 'goals_5',
                'title': 'Dans le mille',
                'description': 'Atteignez vos objectifs caloriques 5 jours cette semaine',
                'reward': 'Badge Précision',
                'progress': min(self._calculate_goals_met() / 5, 1),
                'icon': '🎯'
            }
        ]
        return challenges

    def _get_unique_foods_this_week(self):
        """Retourne l'ensemble des aliments uniques consommés cette semaine"""
        last_week = datetime.now() - timedelta(days=7)
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= last_week
        ).all()
        return set(entry.food_name for entry in entries)

    def get_leaderboard(self):
        """Génère un classement basé sur différents critères"""
        users = User.query.all()
        leaderboard_entries = []

        for user in users:
            social = SocialFeatures(user.id)
            score = (
                social._calculate_streak() * 10 +  # Points pour la régularité
                social._calculate_goals_met() * 20 +  # Points pour l'atteinte des objectifs
                int(social._calculate_variety_score() * 100)  # Points pour la variété
            )

            leaderboard_entries.append({
                'user_id': user.id,
                'username': user.username,
                'score': score,
                'achievements': len(social.get_achievements()),
                'streak': social._calculate_streak()
            })

        # Trier par score décroissant
        leaderboard_entries.sort(key=lambda x: x['score'], reverse=True)
        
        # Ajouter le rang
        for i, entry in enumerate(leaderboard_entries):
            entry['rank'] = i + 1

        return leaderboard_entries
