from datetime import datetime

class DailyTracker:
    def __init__(self):
        self.meals = []
        self.water_intake = 0
        self.exercise = []
        
    def log_meal(self, meal_type, foods, total_calories):
        meal = {
            'timestamp': datetime.now(),
            'type': meal_type,
            'foods': foods,
            'calories': total_calories
        }
        self.meals.append(meal)
        return meal
        
    def log_water(self, amount_ml):
        self.water_intake += amount_ml
        return self.water_intake
        
    def log_exercise(self, activity, duration, calories_burned):
        exercise = {
            'timestamp': datetime.now(),
            'activity': activity,
            'duration': duration,
            'calories_burned': calories_burned
        }
        self.exercise.append(exercise)
        return exercise
        
    def get_daily_summary(self):
        total_calories = sum(meal['calories'] for meal in self.meals)
        total_calories_burned = sum(ex['calories_burned'] for ex in self.exercise)
        
        return {
            'total_calories_consumed': total_calories,
            'total_calories_burned': total_calories_burned,
            'net_calories': total_calories - total_calories_burned,
            'water_intake_ml': self.water_intake,
            'meals': self.meals,
            'exercise': self.exercise
        }
