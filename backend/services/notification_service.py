from datetime import datetime, timedelta
from models import User, FoodEntry, db

class NotificationManager:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)

    def get_meal_reminders(self):
        """Génère des rappels de repas personnalisés"""
        now = datetime.now()
        current_time = now.time()
        
        # Heures habituelles des repas
        meal_times = {
            'petit-dejeuner': {'start': '07:00', 'end': '09:00'},
            'dejeuner': {'start': '12:00', 'end': '14:00'},
            'diner': {'start': '19:00', 'end': '21:00'}
        }

        reminders = []
        
        # Vérifier les entrées du jour
        today_entries = FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= now.date()
        ).all()

        recorded_meals = set(entry.meal_type for entry in today_entries)

        for meal, times in meal_times.items():
            start_time = datetime.strptime(times['start'], '%H:%M').time()
            end_time = datetime.strptime(times['end'], '%H:%M').time()

            # Si le repas n'a pas été enregistré et nous sommes dans la plage horaire
            if (meal not in recorded_meals and 
                start_time <= current_time <= end_time):
                reminders.append({
                    'type': 'meal_reminder',
                    'message': f"N'oubliez pas d'enregistrer votre {meal} !",
                    'priority': 'high'
                })

        return reminders

    def get_goal_updates(self):
        """Génère des mises à jour sur les objectifs"""
        updates = []
        
        # Vérifier la progression vers l'objectif de calories
        today_calories = sum(entry.calories for entry in FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= datetime.now().date()
        ).all())

        target_calories = self.user.target_calories or 2000
        
        if today_calories > target_calories:
            updates.append({
                'type': 'goal_alert',
                'message': f"Vous avez dépassé votre objectif calorique de {today_calories - target_calories} calories",
                'priority': 'medium'
            })
        elif today_calories < target_calories * 0.5 and datetime.now().hour >= 18:
            updates.append({
                'type': 'goal_alert',
                'message': "Vous êtes bien en dessous de votre objectif calorique aujourd'hui",
                'priority': 'medium'
            })

        return updates

    def get_achievements(self):
        """Génère des notifications d'accomplissement"""
        achievements = []
        
        # Vérifier la régularité d'enregistrement
        last_week = datetime.now() - timedelta(days=7)
        daily_entries = db.session.query(
            db.func.date(FoodEntry.date),
            db.func.count(FoodEntry.id)
        ).filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= last_week
        ).group_by(
            db.func.date(FoodEntry.date)
        ).all()

        if len(daily_entries) >= 7:
            achievements.append({
                'type': 'achievement',
                'message': "Bravo ! Vous avez enregistré vos repas pendant 7 jours consécutifs !",
                'priority': 'low'
            })

        return achievements

def get_user_notifications(user_id):
    manager = NotificationManager(user_id)
    
    notifications = []
    notifications.extend(manager.get_meal_reminders())
    notifications.extend(manager.get_goal_updates())
    notifications.extend(manager.get_achievements())
    
    # Trier par priorité
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    notifications.sort(key=lambda x: priority_order[x['priority']])
    
    return notifications
