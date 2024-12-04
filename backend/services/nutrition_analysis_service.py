from datetime import datetime, timedelta
from models import User, FoodEntry, db
import numpy as np

class NutritionAnalyzer:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)
        self.daily_calories = self.user.target_calories or 2000
        
    def get_detailed_nutrition_analysis(self, date_range=7):
        """Analyse détaillée des habitudes alimentaires"""
        start_date = datetime.now() - timedelta(days=date_range)
        
        # Récupérer toutes les entrées alimentaires pour la période
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= start_date
        ).all()

        # Initialiser l'analyse
        analysis = {
            'calories': {
                'daily_average': 0,
                'trend': [],
                'peak_hours': {},
                'deficit_surplus': 0
            },
            'macronutrients': {
                'proteins': {'total': 0, 'percentage': 0},
                'carbs': {'total': 0, 'percentage': 0},
                'fats': {'total': 0, 'percentage': 0}
            },
            'meal_patterns': {
                'breakfast': {'frequency': 0, 'average_calories': 0},
                'lunch': {'frequency': 0, 'average_calories': 0},
                'dinner': {'frequency': 0, 'average_calories': 0},
                'snacks': {'frequency': 0, 'average_calories': 0}
            },
            'habits': {
                'regular_meals': False,
                'snacking_frequency': 0,
                'late_night_eating': 0,
                'portion_control': 'good'
            },
            'recommendations': []
        }

        if not entries:
            return analysis

        # Analyser les calories
        daily_calories = {}
        meal_times = []
        
        for entry in entries:
            # Analyse quotidienne
            day = entry.date.date()
            daily_calories[day] = daily_calories.get(day, 0) + entry.calories
            
            # Analyse des heures de repas
            hour = entry.date.hour
            meal_times.append(hour)
            
            # Analyse par type de repas
            meal_type = entry.meal_type.lower()
            if meal_type in analysis['meal_patterns']:
                analysis['meal_patterns'][meal_type]['frequency'] += 1
                analysis['meal_patterns'][meal_type]['average_calories'] += entry.calories

            # Analyse des macronutriments
            analysis['macronutrients']['proteins']['total'] += entry.proteins
            analysis['macronutrients']['carbs']['total'] += entry.carbs
            analysis['macronutrients']['fats']['total'] += entry.fats

        # Calculer les moyennes et tendances
        total_days = len(daily_calories)
        analysis['calories']['daily_average'] = sum(daily_calories.values()) / total_days
        analysis['calories']['trend'] = self._calculate_trend(daily_calories)
        analysis['calories']['peak_hours'] = self._analyze_meal_times(meal_times)
        analysis['calories']['deficit_surplus'] = analysis['calories']['daily_average'] - self.daily_calories

        # Calculer les pourcentages de macronutriments
        total_macros = sum(macro['total'] for macro in analysis['macronutrients'].values())
        if total_macros > 0:
            for macro in analysis['macronutrients'].values():
                macro['percentage'] = (macro['total'] / total_macros) * 100

        # Analyser les habitudes
        analysis['habits'] = self._analyze_habits(entries, analysis['meal_patterns'])

        # Générer des recommandations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _calculate_trend(self, daily_calories):
        """Calcule la tendance des calories sur la période"""
        if not daily_calories:
            return []

        dates = sorted(daily_calories.keys())
        calories = [daily_calories[date] for date in dates]
        
        # Calculer la ligne de tendance
        x = np.arange(len(dates))
        z = np.polyfit(x, calories, 1)
        trend = np.poly1d(z)
        
        return {
            'direction': 'increasing' if z[0] > 0 else 'decreasing',
            'slope': abs(z[0]),
            'values': [float(trend(i)) for i in x]
        }

    def _analyze_meal_times(self, meal_times):
        """Analyse les heures de repas les plus fréquentes"""
        if not meal_times:
            return {}

        hour_counts = {}
        for hour in meal_times:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        return {
            'peak_hours': sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'distribution': hour_counts
        }

    def _analyze_habits(self, entries, meal_patterns):
        """Analyse détaillée des habitudes alimentaires"""
        habits = {
            'regular_meals': True,
            'snacking_frequency': 0,
            'late_night_eating': 0,
            'portion_control': 'good',
            'meal_spacing': 'good',
            'hydration': 'unknown',
            'variety': 'good'
        }

        # Analyser la régularité des repas
        for meal_type, stats in meal_patterns.items():
            if stats['frequency'] < len(set(entry.date.date() for entry in entries)) * 0.7:
                habits['regular_meals'] = False

        # Analyser le grignotage
        snack_entries = [e for e in entries if e.meal_type.lower() == 'snacks']
        habits['snacking_frequency'] = len(snack_entries) / len(set(e.date.date() for e in entries))

        # Analyser les repas tardifs
        late_entries = [e for e in entries if e.date.hour >= 22]
        habits['late_night_eating'] = len(late_entries)

        # Analyser le contrôle des portions
        daily_variations = []
        for entry in entries:
            if entry.calories > (self.daily_calories * 0.4):  # Plus de 40% des calories quotidiennes en un repas
                habits['portion_control'] = 'needs_improvement'

        return habits

    def _generate_recommendations(self, analysis):
        """Génère des recommandations personnalisées basées sur l'analyse"""
        recommendations = []

        # Recommandations basées sur les calories
        if abs(analysis['calories']['deficit_surplus']) > 300:
            if analysis['calories']['deficit_surplus'] > 0:
                recommendations.append({
                    'category': 'calories',
                    'title': 'Ajustement des calories',
                    'description': 'Vous consommez en moyenne plus de calories que votre objectif. '
                                 'Essayez de réduire légèrement les portions.',
                    'tips': [
                        'Utilisez des assiettes plus petites',
                        'Mangez lentement et écoutez votre satiété',
                        'Privilégiez les aliments moins caloriques mais rassasiants'
                    ]
                })
            else:
                recommendations.append({
                    'category': 'calories',
                    'title': 'Augmentation des calories',
                    'description': 'Votre apport calorique est inférieur à votre objectif. '
                                 'Assurez-vous de manger suffisamment.',
                    'tips': [
                        'Ajoutez des collations saines',
                        'Enrichissez vos repas avec des aliments nutritifs',
                        'Pensez aux fruits secs et oléagineux'
                    ]
                })

        # Recommandations basées sur les macronutriments
        if analysis['macronutrients']['proteins']['percentage'] < 20:
            recommendations.append({
                'category': 'macronutrients',
                'title': 'Augmentez les protéines',
                'description': 'Votre apport en protéines est un peu faible.',
                'tips': [
                    'Incluez une source de protéines à chaque repas',
                    'Pensez aux légumineuses et aux œufs',
                    'Les produits laitiers sont aussi de bonnes sources de protéines'
                ]
            })

        # Recommandations basées sur les habitudes
        if not analysis['habits']['regular_meals']:
            recommendations.append({
                'category': 'habits',
                'title': 'Régularité des repas',
                'description': 'Essayez de maintenir des horaires de repas plus réguliers.',
                'tips': [
                    'Planifiez vos repas à l\'avance',
                    'Essayez de manger à des heures fixes',
                    'Évitez de sauter des repas'
                ]
            })

        if analysis['habits']['snacking_frequency'] > 2:
            recommendations.append({
                'category': 'habits',
                'title': 'Réduire le grignotage',
                'description': 'Vous avez tendance à grignoter fréquemment.',
                'tips': [
                    'Préparez des collations saines à l\'avance',
                    'Buvez de l\'eau quand vous avez envie de grignoter',
                    'Occupez-vous l\'esprit avec une activité'
                ]
            })

        if analysis['habits']['late_night_eating'] > 2:
            recommendations.append({
                'category': 'habits',
                'title': 'Repas tardifs',
                'description': 'Évitez de manger tard le soir.',
                'tips': [
                    'Essayez de dîner au moins 3h avant le coucher',
                    'Si vous avez faim le soir, optez pour une collation légère',
                    'Buvez une tisane avant de dormir'
                ]
            })

        return recommendations

    def get_meal_suggestions(self, meal_type=None):
        """Génère des suggestions de repas personnalisées"""
        # Calculer les calories cibles par repas
        meal_ratios = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snacks': 0.10
        }

        target_calories = self.daily_calories * meal_ratios.get(meal_type, 0.3)
        
        # Exemple de suggestions (à remplacer par une vraie base de données)
        suggestions = {
            'breakfast': [
                {
                    'name': 'Porridge aux fruits',
                    'calories': 350,
                    'proteins': 12,
                    'carbs': 45,
                    'fats': 8,
                    'ingredients': ['Flocons d\'avoine', 'Lait', 'Banane', 'Fruits rouges'],
                    'preparation_time': 10
                },
                {
                    'name': 'Toast à l\'avocat et œuf',
                    'calories': 400,
                    'proteins': 15,
                    'carbs': 35,
                    'fats': 12,
                    'ingredients': ['Pain complet', 'Avocat', 'Œuf', 'Épices'],
                    'preparation_time': 15
                }
            ],
            'lunch': [
                {
                    'name': 'Bowl de quinoa aux légumes',
                    'calories': 550,
                    'proteins': 20,
                    'carbs': 65,
                    'fats': 15,
                    'ingredients': ['Quinoa', 'Légumes grillés', 'Pois chiches', 'Sauce tahini'],
                    'preparation_time': 25
                }
            ],
            'dinner': [
                {
                    'name': 'Saumon grillé aux légumes',
                    'calories': 450,
                    'proteins': 35,
                    'carbs': 25,
                    'fats': 18,
                    'ingredients': ['Saumon', 'Brocoli', 'Patate douce', 'Huile d\'olive'],
                    'preparation_time': 30
                }
            ],
            'snacks': [
                {
                    'name': 'Yaourt grec aux fruits',
                    'calories': 150,
                    'proteins': 12,
                    'carbs': 15,
                    'fats': 5,
                    'ingredients': ['Yaourt grec', 'Fruits frais', 'Miel'],
                    'preparation_time': 5
                }
            ]
        }

        if meal_type:
            return suggestions.get(meal_type, [])
        return suggestions
