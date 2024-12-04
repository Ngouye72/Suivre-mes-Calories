class MealPlanner:
    def __init__(self):
        self.meal_database = {
            'breakfast': [
                {'name': 'Oatmeal with fruits', 'calories': 300, 'protein': 10, 'carbs': 50, 'fat': 6},
                {'name': 'Eggs and toast', 'calories': 400, 'protein': 20, 'carbs': 35, 'fat': 12},
            ],
            'lunch': [
                {'name': 'Chicken salad', 'calories': 450, 'protein': 35, 'carbs': 25, 'fat': 15},
                {'name': 'Tuna sandwich', 'calories': 500, 'protein': 30, 'carbs': 45, 'fat': 18},
            ],
            'dinner': [
                {'name': 'Grilled salmon with vegetables', 'calories': 550, 'protein': 40, 'carbs': 30, 'fat': 20},
                {'name': 'Lean beef stir-fry', 'calories': 600, 'protein': 45, 'carbs': 40, 'fat': 22},
            ],
            'snacks': [
                {'name': 'Greek yogurt with berries', 'calories': 150, 'protein': 12, 'carbs': 15, 'fat': 4},
                {'name': 'Apple with almond butter', 'calories': 200, 'protein': 5, 'carbs': 25, 'fat': 10},
            ]
        }
    
    def generate_daily_plan(self, calorie_goal, protein_goal, carb_goal, fat_goal):
        # Simple meal plan generation based on goals
        daily_plan = {
            'breakfast': self.meal_database['breakfast'][0],
            'lunch': self.meal_database['lunch'][0],
            'dinner': self.meal_database['dinner'][0],
            'snacks': [self.meal_database['snacks'][0]]
        }
        
        total_calories = sum(meal['calories'] for meal in daily_plan.values() if isinstance(meal, dict))
        total_calories += sum(snack['calories'] for snack in daily_plan['snacks'])
        
        return {
            'meals': daily_plan,
            'total_calories': total_calories,
            'target_calories': calorie_goal,
            'calorie_difference': calorie_goal - total_calories
        }
