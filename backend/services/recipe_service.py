from models import Food, User, db
import random

class RecipeRecommender:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)
        self.daily_calories = self.user.target_calories or 2000

    def get_meal_calories(self, meal_type):
        meal_ratios = {
            'petit-dejeuner': 0.25,
            'dejeuner': 0.35,
            'diner': 0.30,
            'collation': 0.10
        }
        return self.daily_calories * meal_ratios.get(meal_type, 0.3)

    def suggest_recipes(self, meal_type=None, preferences=None):
        recipes = []
        target_calories = self.get_meal_calories(meal_type) if meal_type else self.daily_calories

        # Exemple de recettes (à remplacer par une vraie base de données de recettes)
        sample_recipes = [
            {
                'name': 'Bol de Buddha aux légumes',
                'calories': 450,
                'proteins': 15,
                'carbs': 65,
                'fats': 12,
                'ingredients': [
                    'Quinoa', 'Pois chiches', 'Avocat', 'Légumes rôtis',
                    'Graines de sésame', 'Sauce tahini'
                ],
                'instructions': [
                    'Cuire le quinoa selon les instructions',
                    'Rôtir les légumes au four',
                    'Assembler le bol avec tous les ingrédients',
                    'Garnir de sauce tahini'
                ],
                'preparation_time': 25,
                'difficulty': 'facile',
                'meal_type': ['dejeuner', 'diner']
            },
            {
                'name': 'Smoothie bowl protéiné',
                'calories': 320,
                'proteins': 20,
                'carbs': 45,
                'fats': 8,
                'ingredients': [
                    'Banane', 'Fruits rouges', 'Yaourt grec',
                    'Protéine en poudre', 'Granola', 'Graines de chia'
                ],
                'instructions': [
                    'Mixer les fruits avec le yaourt et la protéine',
                    'Verser dans un bol',
                    'Garnir de granola et de graines'
                ],
                'preparation_time': 10,
                'difficulty': 'facile',
                'meal_type': ['petit-dejeuner', 'collation']
            },
            {
                'name': 'Poulet grillé aux légumes',
                'calories': 550,
                'proteins': 40,
                'carbs': 35,
                'fats': 15,
                'ingredients': [
                    'Blanc de poulet', 'Brocoli', 'Carottes',
                    'Patate douce', 'Huile d\'olive', 'Épices'
                ],
                'instructions': [
                    'Mariner le poulet avec les épices',
                    'Griller le poulet',
                    'Cuire les légumes à la vapeur',
                    'Rôtir la patate douce'
                ],
                'preparation_time': 30,
                'difficulty': 'moyen',
                'meal_type': ['dejeuner', 'diner']
            }
        ]

        # Filtrer les recettes selon le type de repas et les calories cibles
        for recipe in sample_recipes:
            if meal_type and meal_type not in recipe['meal_type']:
                continue
            
            # Vérifier si les calories correspondent approximativement à l'objectif
            calorie_diff = abs(recipe['calories'] - target_calories)
            if calorie_diff <= target_calories * 0.2:  # 20% de marge
                recipes.append(recipe)

        # Ajouter des tags nutritionnels
        for recipe in recipes:
            recipe['tags'] = []
            if recipe['proteins'] >= 20:
                recipe['tags'].append('riche en protéines')
            if recipe['fats'] <= 10:
                recipe['tags'].append('faible en gras')
            if recipe['carbs'] <= 30:
                recipe['tags'].append('faible en glucides')

        return recipes

def get_recipe_suggestions(user_id, meal_type=None):
    recommender = RecipeRecommender(user_id)
    return recommender.suggest_recipes(meal_type)

def get_weekly_meal_plan(user_id):
    recommender = RecipeRecommender(user_id)
    meal_plan = {
        'petit-dejeuner': [],
        'dejeuner': [],
        'diner': [],
        'collation': []
    }

    for meal_type in meal_plan.keys():
        recipes = recommender.suggest_recipes(meal_type)
        # Sélectionner aléatoirement 7 recettes pour chaque type de repas
        meal_plan[meal_type] = random.sample(recipes, min(7, len(recipes)))

    return meal_plan
