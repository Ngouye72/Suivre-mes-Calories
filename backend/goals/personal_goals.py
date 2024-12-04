class PersonalGoals:
    def __init__(self):
        self.weight_goal = None
        self.calorie_goal = None
        self.protein_goal = None
        self.carb_goal = None
        self.fat_goal = None
        
    def calculate_goals(self, weight, height, age, gender, activity_level, goal_type):
        # Calcul du BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
        # Ajustement selon le niveau d'activité
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level.lower(), 1.2)
        
        # Ajustement selon l'objectif
        goal_adjustments = {
            'lose': -500,    # Déficit calorique pour perdre du poids
            'maintain': 0,   # Maintien du poids
            'gain': 300      # Surplus calorique pour gagner du poids
        }
        
        self.calorie_goal = tdee + goal_adjustments.get(goal_type.lower(), 0)
        
        # Calcul des macronutriments
        self.protein_goal = weight * 2.2  # 2.2g par kg de poids corporel
        self.fat_goal = (self.calorie_goal * 0.25) / 9  # 25% des calories totales
        # Le reste en glucides
        self.carb_goal = (self.calorie_goal - (self.protein_goal * 4 + self.fat_goal * 9)) / 4
        
        return {
            'calorie_goal': round(self.calorie_goal),
            'protein_goal': round(self.protein_goal),
            'carb_goal': round(self.carb_goal),
            'fat_goal': round(self.fat_goal)
        }
