class NutritionCoach:
    def __init__(self):
        self.tips_database = {
            'over_calories': [
                "Essayez de manger plus lentement pour mieux ressentir la satiété",
                "Buvez un grand verre d'eau avant chaque repas",
                "Augmentez votre consommation de légumes pour vous sentir rassasié avec moins de calories"
            ],
            'under_calories': [
                "Ajoutez des collations saines entre les repas",
                "Incorporez des aliments plus denses en calories comme les noix ou l'avocat",
                "Augmentez légèrement les portions à chaque repas"
            ],
            'low_protein': [
                "Incluez une source de protéines à chaque repas",
                "Pensez aux œufs, poulet, poisson ou légumineuses",
                "Un smoothie protéiné peut être une bonne option"
            ],
            'hydration': [
                "Gardez une bouteille d'eau à portée de main",
                "Définissez des rappels pour boire régulièrement",
                "Commencez chaque repas par un verre d'eau"
            ]
        }
    
    def get_guidance(self, daily_summary, goals):
        advice = []
        
        # Analyse des calories
        net_calories = daily_summary['total_calories_consumed'] - daily_summary['total_calories_burned']
        if net_calories > goals['calorie_goal'] * 1.1:  # Plus de 10% au-dessus
            advice.extend(self.tips_database['over_calories'])
        elif net_calories < goals['calorie_goal'] * 0.9:  # Plus de 10% en-dessous
            advice.extend(self.tips_database['under_calories'])
            
        # Analyse de l'hydratation
        if daily_summary['water_intake_ml'] < 2000:  # Moins de 2L par jour
            advice.extend(self.tips_database['hydration'])
            
        return {
            'daily_analysis': {
                'calorie_status': 'high' if net_calories > goals['calorie_goal'] else 'low',
                'hydration_status': 'low' if daily_summary['water_intake_ml'] < 2000 else 'good'
            },
            'recommendations': advice
        }
