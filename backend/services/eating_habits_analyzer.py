from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from models import User, FoodEntry, db

class EatingHabitsAnalyzer:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)
        self.daily_calories = self.user.target_calories or 2000

    def get_detailed_habits_analysis(self, date_range=30):
        """Analyse détaillée des habitudes alimentaires"""
        start_date = datetime.now() - timedelta(days=date_range)
        entries = FoodEntry.query.filter(
            FoodEntry.user_id == self.user.id,
            FoodEntry.date >= start_date
        ).all()

        analysis = {
            'meal_timing': self._analyze_meal_timing(entries),
            'portion_control': self._analyze_portion_control(entries),
            'eating_patterns': self._analyze_eating_patterns(entries),
            'food_variety': self._analyze_food_variety(entries),
            'emotional_eating': self._analyze_emotional_eating(entries),
            'social_eating': self._analyze_social_eating(entries),
            'nutrient_balance': self._analyze_nutrient_balance(entries),
            'hydration': self._analyze_hydration(entries),
            'weekly_patterns': self._analyze_weekly_patterns(entries),
            'improvement_areas': []
        }

        # Identifier les domaines d'amélioration
        analysis['improvement_areas'] = self._identify_improvement_areas(analysis)

        return analysis

    def _analyze_meal_timing(self, entries):
        """Analyse détaillée des horaires de repas"""
        meal_times = defaultdict(list)
        time_gaps = []
        last_meal_time = None

        for entry in sorted(entries, key=lambda x: x.date):
            hour = entry.date.hour
            meal_type = entry.meal_type.lower()
            meal_times[meal_type].append(hour)

            if last_meal_time:
                gap = (entry.date - last_meal_time).total_seconds() / 3600
                if gap < 24:  # Ignorer les gaps entre les jours
                    time_gaps.append(gap)
            last_meal_time = entry.date

        return {
            'meal_time_distribution': {
                meal: {
                    'average_time': np.mean(times) if times else 0,
                    'consistency': np.std(times) if times else 0,
                    'most_common_hour': max(set(times), key=times.count) if times else 0
                }
                for meal, times in meal_times.items()
            },
            'average_time_between_meals': np.mean(time_gaps) if time_gaps else 0,
            'meal_timing_consistency': np.std(time_gaps) if time_gaps else 0,
            'late_night_eating': sum(1 for t in meal_times.get('dinner', []) if t >= 21),
            'early_breakfast': sum(1 for t in meal_times.get('breakfast', []) if 6 <= t <= 9)
        }

    def _analyze_portion_control(self, entries):
        """Analyse du contrôle des portions"""
        daily_calories = defaultdict(list)
        meal_sizes = defaultdict(list)

        for entry in entries:
            date = entry.date.date()
            meal_type = entry.meal_type.lower()
            daily_calories[date].append(entry.calories)
            meal_sizes[meal_type].append(entry.calories)

        return {
            'meal_size_consistency': {
                meal: {
                    'average_size': np.mean(sizes),
                    'variation': np.std(sizes),
                    'largest_meal': max(sizes),
                    'smallest_meal': min(sizes)
                }
                for meal, sizes in meal_sizes.items()
            },
            'daily_calorie_consistency': {
                'average_daily_calories': np.mean([sum(cals) for cals in daily_calories.values()]),
                'daily_variation': np.std([sum(cals) for cals in daily_calories.values()]),
                'days_over_target': sum(1 for cals in daily_calories.values() if sum(cals) > self.daily_calories),
                'days_under_target': sum(1 for cals in daily_calories.values() if sum(cals) < self.daily_calories * 0.8)
            }
        }

    def _analyze_eating_patterns(self, entries):
        """Analyse des schémas alimentaires"""
        days_with_entries = defaultdict(lambda: defaultdict(int))
        meal_combinations = defaultdict(int)
        snacking_patterns = defaultdict(int)

        for entry in entries:
            date = entry.date.date()
            meal_type = entry.meal_type.lower()
            hour = entry.date.hour
            days_with_entries[date][meal_type] += 1

            # Analyser les combinaisons de repas
            daily_meals = tuple(sorted(days_with_entries[date].keys()))
            meal_combinations[daily_meals] += 1

            # Analyser le grignotage
            if meal_type == 'snack':
                period = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 18 else 'evening'
                snacking_patterns[period] += 1

        return {
            'meal_frequency': {
                meal: sum(1 for day in days_with_entries.values() if meal in day)
                for meal in ['breakfast', 'lunch', 'dinner', 'snack']
            },
            'common_meal_combinations': {
                ' + '.join(combo): count
                for combo, count in sorted(meal_combinations.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            'snacking_patterns': dict(snacking_patterns),
            'regular_meal_schedule': sum(1 for day in days_with_entries.values() 
                                      if len(day) >= 3 and 'breakfast' in day and 'lunch' in day and 'dinner' in day),
            'skipped_meals': {
                meal: sum(1 for day in days_with_entries.values() if meal not in day)
                for meal in ['breakfast', 'lunch', 'dinner']
            }
        }

    def _analyze_food_variety(self, entries):
        """Analyse de la variété alimentaire"""
        foods_by_meal = defaultdict(set)
        foods_by_day = defaultdict(set)
        repeated_foods = defaultdict(int)

        for entry in entries:
            date = entry.date.date()
            meal_type = entry.meal_type.lower()
            foods_by_meal[meal_type].add(entry.food_name)
            foods_by_day[date].add(entry.food_name)
            repeated_foods[entry.food_name] += 1

        return {
            'variety_score': {
                meal: len(foods) for meal, foods in foods_by_meal.items()
            },
            'daily_variety': {
                'average_unique_foods': np.mean([len(foods) for foods in foods_by_day.values()]),
                'max_unique_foods': max(len(foods) for foods in foods_by_day.values()),
                'min_unique_foods': min(len(foods) for foods in foods_by_day.values())
            },
            'most_repeated_foods': {
                food: count for food, count in sorted(repeated_foods.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            'food_categories': self._categorize_foods(entries)
        }

    def _analyze_emotional_eating(self, entries):
        """Analyse des comportements alimentaires émotionnels"""
        late_night_snacks = []
        large_portions = []
        irregular_patterns = defaultdict(list)

        for entry in entries:
            hour = entry.date.hour
            
            # Repas tardifs
            if hour >= 22:
                late_night_snacks.append(entry)

            # Portions importantes
            if entry.calories > (self.daily_calories * 0.4):
                large_portions.append(entry)

            # Schémas irréguliers
            date = entry.date.date()
            irregular_patterns[date].append(entry)

        return {
            'late_night_eating': {
                'frequency': len(late_night_snacks),
                'average_calories': np.mean([entry.calories for entry in late_night_snacks]) if late_night_snacks else 0
            },
            'stress_eating_indicators': {
                'large_portions': len(large_portions),
                'irregular_meals': sum(1 for entries in irregular_patterns.values() if len(entries) > 5)
            }
        }

    def _analyze_social_eating(self, entries):
        """Analyse des habitudes alimentaires sociales"""
        weekend_patterns = defaultdict(list)
        weekday_patterns = defaultdict(list)

        for entry in entries:
            if entry.date.weekday() >= 5:  # Weekend
                weekend_patterns[entry.date.date()].append(entry)
            else:
                weekday_patterns[entry.date.date()].append(entry)

        return {
            'weekend_vs_weekday': {
                'weekend_average_calories': np.mean([sum(e.calories for e in entries) 
                                                   for entries in weekend_patterns.values()]) if weekend_patterns else 0,
                'weekday_average_calories': np.mean([sum(e.calories for e in entries) 
                                                   for entries in weekday_patterns.values()]) if weekday_patterns else 0,
                'weekend_meal_frequency': np.mean([len(entries) for entries in weekend_patterns.values()]) if weekend_patterns else 0,
                'weekday_meal_frequency': np.mean([len(entries) for entries in weekday_patterns.values()]) if weekday_patterns else 0
            }
        }

    def _analyze_nutrient_balance(self, entries):
        """Analyse de l'équilibre nutritionnel"""
        daily_nutrients = defaultdict(lambda: {'proteins': 0, 'carbs': 0, 'fats': 0})

        for entry in entries:
            date = entry.date.date()
            daily_nutrients[date]['proteins'] += entry.proteins
            daily_nutrients[date]['carbs'] += entry.carbs
            daily_nutrients[date]['fats'] += entry.fats

        nutrient_ratios = []
        for nutrients in daily_nutrients.values():
            total = sum(nutrients.values())
            if total > 0:
                ratios = {
                    nutrient: (value / total) * 100
                    for nutrient, value in nutrients.items()
                }
                nutrient_ratios.append(ratios)

        return {
            'average_ratios': {
                nutrient: np.mean([ratio[nutrient] for ratio in nutrient_ratios]) if nutrient_ratios else 0
                for nutrient in ['proteins', 'carbs', 'fats']
            },
            'ratio_consistency': {
                nutrient: np.std([ratio[nutrient] for ratio in nutrient_ratios]) if nutrient_ratios else 0
                for nutrient in ['proteins', 'carbs', 'fats']
            },
            'days_with_balanced_nutrients': sum(
                1 for ratios in nutrient_ratios
                if 10 <= ratios['proteins'] <= 35 and
                   45 <= ratios['carbs'] <= 65 and
                   20 <= ratios['fats'] <= 35
            )
        }

    def _analyze_hydration(self, entries):
        """Analyse des habitudes d'hydratation"""
        # Simuler des données d'hydratation (à remplacer par de vraies données)
        daily_water = defaultdict(float)
        hydration_times = defaultdict(list)

        return {
            'average_daily_water': np.mean(list(daily_water.values())) if daily_water else 0,
            'hydration_consistency': np.std(list(daily_water.values())) if daily_water else 0,
            'hydration_timing': {
                period: len(times)
                for period, times in hydration_times.items()
            }
        }

    def _analyze_weekly_patterns(self, entries):
        """Analyse des tendances hebdomadaires"""
        weekly_calories = defaultdict(list)
        weekly_meals = defaultdict(lambda: defaultdict(int))

        for entry in entries:
            day_of_week = entry.date.strftime('%A')
            weekly_calories[day_of_week].append(entry.calories)
            weekly_meals[day_of_week][entry.meal_type.lower()] += 1

        return {
            'calories_by_day': {
                day: np.mean(calories) if calories else 0
                for day, calories in weekly_calories.items()
            },
            'meal_frequency_by_day': {
                day: dict(meals)
                for day, meals in weekly_meals.items()
            }
        }

    def _categorize_foods(self, entries):
        """Catégorisation des aliments consommés"""
        categories = defaultdict(int)
        for entry in entries:
            # Logique simplifiée de catégorisation (à améliorer avec une vraie base de données d'aliments)
            if 'fruit' in entry.food_name.lower():
                categories['fruits'] += 1
            elif 'légume' in entry.food_name.lower():
                categories['légumes'] += 1
            elif 'viande' in entry.food_name.lower():
                categories['protéines'] += 1
            elif 'pain' in entry.food_name.lower() or 'pâtes' in entry.food_name.lower():
                categories['glucides'] += 1
            else:
                categories['autres'] += 1

        return dict(categories)

    def _identify_improvement_areas(self, analysis):
        """Identifie les domaines nécessitant une amélioration"""
        improvements = []

        # Analyse des horaires de repas
        meal_timing = analysis['meal_timing']
        if meal_timing['late_night_eating'] > 2:
            improvements.append({
                'area': 'meal_timing',
                'issue': 'repas_tardifs',
                'description': 'Vous mangez souvent tard le soir',
                'recommendation': 'Essayez de dîner au moins 3 heures avant le coucher'
            })

        # Analyse du contrôle des portions
        portion_control = analysis['portion_control']
        if portion_control['daily_calorie_consistency']['days_over_target'] > 5:
            improvements.append({
                'area': 'portion_control',
                'issue': 'calories_excessives',
                'description': 'Dépassement fréquent des objectifs caloriques',
                'recommendation': 'Utilisez des assiettes plus petites et mangez plus lentement'
            })

        # Analyse des schémas alimentaires
        patterns = analysis['eating_patterns']
        if patterns['skipped_meals']['breakfast'] > 5:
            improvements.append({
                'area': 'meal_frequency',
                'issue': 'petit_dejeuner_manque',
                'description': 'Vous sautez souvent le petit-déjeuner',
                'recommendation': 'Le petit-déjeuner est important pour démarrer la journée'
            })

        return improvements
