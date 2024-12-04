class GoalVisualizer:
    def __init__(self):
        self.progress_data = []
        
    def add_daily_data(self, date, calories_consumed, calories_burned, water_intake):
        daily_data = {
            'date': date,
            'calories_consumed': calories_consumed,
            'calories_burned': calories_burned,
            'water_intake': water_intake,
            'net_calories': calories_consumed - calories_burned
        }
        self.progress_data.append(daily_data)
        
    def get_dashboard_data(self, calorie_goal):
        if not self.progress_data:
            return {
                'current_streak': 0,
                'days_on_target': 0,
                'average_calories': 0,
                'progress_data': []
            }
            
        total_days = len(self.progress_data)
        days_on_target = sum(1 for day in self.progress_data 
                           if abs(day['net_calories'] - calorie_goal) <= 100)
        
        average_calories = sum(day['net_calories'] for day in self.progress_data) / total_days
        
        return {
            'current_streak': self._calculate_streak(),
            'days_on_target': days_on_target,
            'average_calories': round(average_calories),
            'progress_data': self.progress_data[-7:]  # Last 7 days
        }
        
    def _calculate_streak(self):
        streak = 0
        for data in reversed(self.progress_data):
            if data['calories_consumed'] > 0:
                streak += 1
            else:
                break
        return streak
