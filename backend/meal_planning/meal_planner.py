from typing import Dict, List
import random
from datetime import datetime, timedelta

class MealPlanner:
    def __init__(self):
        # Base de données simplifiée des repas
        self.meals = {
            'petit_dejeuner': [
                {
                    'nom': 'Petit-déjeuner protéiné',
                    'calories': 500,
                    'proteines': 30,
                    'glucides': 60,
                    'lipides': 15,
                    'aliments': ['Oeufs', 'Pain complet', 'Fromage blanc', 'Banane']
                }
            ],
            'dejeuner': [
                {
                    'nom': 'Poulet légumes',
                    'calories': 600,
                    'proteines': 40,
                    'glucides': 70,
                    'lipides': 20,
                    'aliments': ['Poulet', 'Riz complet', 'Légumes', 'Huile olive']
                }
            ],
            'collation': [
                {
                    'nom': 'Collation santé',
                    'calories': 200,
                    'proteines': 10,
                    'glucides': 25,
                    'lipides': 8,
                    'aliments': ['Yaourt', 'Fruits', 'Noix']
                }
            ],
            'diner': [
                {
                    'nom': 'Poisson légumes',
                    'calories': 500,
                    'proteines': 35,
                    'glucides': 55,
                    'lipides': 15,
                    'aliments': ['Saumon', 'Quinoa', 'Légumes verts']
                }
            ]
        }
        
    def get_meal(self, meal_type: str) -> Dict:
        """Retourne un repas pour le type donné"""
        if meal_type not in self.meals:
            raise ValueError(f"Type de repas invalide: {meal_type}")
        return random.choice(self.meals[meal_type])

    def generate_daily_plan(self) -> Dict:
        """Génère un plan alimentaire journalier"""
        try:
            plan = {
                'petit_dejeuner': self.get_meal('petit_dejeuner'),
                'dejeuner': self.get_meal('dejeuner'),
                'collation': self.get_meal('collation'),
                'diner': self.get_meal('diner')
            }
            
            # Calcul des totaux
            totals = {
                'calories': sum(meal['calories'] for meal in plan.values()),
                'proteines': sum(meal['proteines'] for meal in plan.values()),
                'glucides': sum(meal['glucides'] for meal in plan.values()),
                'lipides': sum(meal['lipides'] for meal in plan.values())
            }
            
            return {
                'plan': plan,
                'totaux': totals,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Erreur lors de la génération du plan: {str(e)}")
            return {
                'error': str(e)
            }
