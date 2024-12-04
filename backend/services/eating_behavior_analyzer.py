from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from models import User, FoodEntry, db

class EatingBehaviorAnalyzer:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)
        self.daily_calories = self.user.target_calories or 2000

    def analyze_emotional_eating(self, entries, days=30):
        """Analyse du comportement alimentaire émotionnel"""
        emotional_patterns = {
            'stress_eating': self._detect_stress_eating(entries),
            'comfort_foods': self._identify_comfort_foods(entries),
            'mood_related': self._analyze_mood_patterns(entries),
            'binge_episodes': self._detect_binge_episodes(entries),
            'night_eating': self._analyze_night_eating(entries)
        }
        return emotional_patterns

    def analyze_social_eating(self, entries, days=30):
        """Analyse du comportement alimentaire social"""
        social_patterns = {
            'weekend_vs_weekday': self._analyze_weekend_patterns(entries),
            'meal_company': self._analyze_meal_company(entries),
            'special_occasions': self._detect_special_occasions(entries),
            'restaurant_meals': self._analyze_restaurant_meals(entries)
        }
        return social_patterns

    def analyze_mindful_eating(self, entries, days=30):
        """Analyse de la pleine conscience alimentaire"""
        mindful_patterns = {
            'eating_speed': self._analyze_eating_speed(entries),
            'portion_awareness': self._analyze_portion_awareness(entries),
            'distracted_eating': self._detect_distracted_eating(entries),
            'hunger_fullness': self._analyze_hunger_signals(entries)
        }
        return mindful_patterns

    def analyze_environmental_factors(self, entries, days=30):
        """Analyse des facteurs environnementaux influençant l'alimentation"""
        return {
            'location_impact': self._analyze_location_impact(entries),
            'weather_impact': self._analyze_weather_impact(entries),
            'seasonal_patterns': self._analyze_seasonal_patterns(entries),
            'time_constraints': self._analyze_time_constraints(entries)
        }

    def analyze_cultural_influences(self, entries, days=30):
        """Analyse des influences culturelles sur l'alimentation"""
        return {
            'traditional_foods': self._analyze_traditional_foods(entries),
            'celebration_patterns': self._analyze_celebration_patterns(entries),
            'dietary_restrictions': self._analyze_dietary_restrictions(entries),
            'cultural_adaptations': self._analyze_cultural_adaptations(entries)
        }

    def analyze_habit_formation(self, entries, days=30):
        """Analyse de la formation des habitudes alimentaires"""
        return {
            'routine_strength': self._analyze_routine_strength(entries),
            'habit_triggers': self._identify_habit_triggers(entries),
            'habit_consistency': self._analyze_habit_consistency(entries),
            'behavior_chains': self._analyze_behavior_chains(entries)
        }

    def analyze_stress_management(self, entries, days=30):
        """Analyse de la gestion du stress par l'alimentation"""
        return {
            'stress_indicators': self._analyze_stress_indicators(entries),
            'coping_mechanisms': self._identify_coping_mechanisms(entries),
            'recovery_patterns': self._analyze_recovery_patterns(entries),
            'prevention_strategies': self._suggest_prevention_strategies(entries)
        }

    def analyze_weather_correlation(self, entries, weather_data):
        """Analyse détaillée de la corrélation entre météo et alimentation"""
        return {
            'temperature_impact': self._analyze_temperature_impact(entries, weather_data),
            'precipitation_impact': self._analyze_precipitation_impact(entries, weather_data),
            'seasonal_transitions': self._analyze_seasonal_transitions(entries, weather_data),
            'comfort_food_patterns': self._analyze_weather_comfort_foods(entries, weather_data),
            'hydration_patterns': self._analyze_weather_hydration(entries, weather_data),
            'mood_weather_correlation': self._analyze_mood_weather_correlation(entries, weather_data)
        }

    def analyze_circadian_rhythm(self, entries, days=30):
        """Analyse du rythme circadien et son impact sur l'alimentation"""
        return {
            'meal_timing_patterns': self._analyze_meal_timing_patterns(entries),
            'sleep_correlation': self._analyze_sleep_correlation(entries),
            'energy_levels': self._analyze_energy_levels(entries),
            'metabolic_windows': self._identify_metabolic_windows(entries),
            'chronotype_impact': self._analyze_chronotype_impact(entries)
        }

    def analyze_work_impact(self, entries, work_schedule):
        """Analyse de l'impact du travail sur l'alimentation"""
        return {
            'workday_patterns': self._analyze_workday_patterns(entries, work_schedule),
            'stress_correlation': self._analyze_work_stress_correlation(entries, work_schedule),
            'lunch_break_habits': self._analyze_lunch_break_habits(entries, work_schedule),
            'overtime_impact': self._analyze_overtime_impact(entries, work_schedule),
            'workplace_environment': self._analyze_workplace_environment(entries, work_schedule)
        }

    def analyze_physical_activity_correlation(self, entries, activity_data):
        """Analyse de la corrélation entre activité physique et alimentation"""
        return {
            'pre_workout_nutrition': self._analyze_pre_workout_nutrition(entries, activity_data),
            'post_workout_habits': self._analyze_post_workout_habits(entries, activity_data),
            'activity_food_timing': self._analyze_activity_food_timing(entries, activity_data),
            'performance_correlation': self._analyze_performance_correlation(entries, activity_data),
            'recovery_nutrition': self._analyze_recovery_nutrition(entries, activity_data)
        }

    def analyze_budget_impact(self, entries, budget_data):
        """Analyse de l'impact du budget sur les choix alimentaires"""
        return {
            'cost_per_meal': self._analyze_meal_costs(entries, budget_data),
            'budget_constraints': self._analyze_budget_constraints(entries, budget_data),
            'price_quality_ratio': self._analyze_price_quality_ratio(entries, budget_data),
            'seasonal_cost_variations': self._analyze_seasonal_costs(entries, budget_data),
            'cost_optimization_suggestions': self._generate_cost_suggestions(entries, budget_data)
        }

    def analyze_travel_impact(self, entries, location_data):
        """Analyse de l'impact des déplacements sur l'alimentation"""
        return {
            'travel_patterns': self._analyze_travel_eating_patterns(entries, location_data),
            'location_influences': self._analyze_location_influences(entries, location_data),
            'adaptation_strategies': self._analyze_dietary_adaptations(entries, location_data),
            'cultural_influences': self._analyze_cultural_impacts(entries, location_data),
            'travel_recommendations': self._generate_travel_recommendations(entries, location_data)
        }

    def analyze_sustainability_metrics(self, entries):
        """Analyse de l'impact environnemental des choix alimentaires"""
        return {
            'carbon_footprint': self._calculate_carbon_footprint(entries),
            'water_usage': self._calculate_water_usage(entries),
            'packaging_waste': self._analyze_packaging_waste(entries),
            'seasonal_consumption': self._analyze_seasonal_choices(entries),
            'sustainability_score': self._calculate_sustainability_score(entries),
            'improvement_suggestions': self._generate_eco_suggestions(entries)
        }

    def analyze_social_dining(self, entries, social_data):
        """Analyse approfondie des habitudes alimentaires sociales"""
        return {
            'group_dynamics': self._analyze_group_dining_patterns(entries, social_data),
            'social_influence': self._analyze_peer_influence(entries, social_data),
            'restaurant_choices': self._analyze_restaurant_patterns(entries, social_data),
            'portion_variations': self._analyze_social_portions(entries, social_data),
            'social_triggers': self._identify_social_triggers(entries, social_data)
        }

    def analyze_nutrient_optimization(self, entries, nutrient_data):
        """Analyse approfondie de l'optimisation des nutriments"""
        return {
            'nutrient_timing': self._analyze_nutrient_timing(entries, nutrient_data),
            'nutrient_combinations': self._analyze_nutrient_synergies(entries, nutrient_data),
            'absorption_efficiency': self._analyze_absorption_factors(entries, nutrient_data),
            'deficiency_risks': self._identify_deficiency_risks(entries, nutrient_data),
            'bioavailability_score': self._calculate_bioavailability(entries, nutrient_data),
            'optimization_suggestions': self._generate_nutrient_suggestions(entries, nutrient_data)
        }

    def analyze_meal_preparation(self, entries, preparation_data):
        """Analyse des habitudes de préparation des repas"""
        return {
            'prep_time_patterns': self._analyze_prep_time_patterns(entries, preparation_data),
            'cooking_methods': self._analyze_cooking_methods(entries, preparation_data),
            'ingredient_freshness': self._analyze_ingredient_freshness(entries, preparation_data),
            'batch_cooking_patterns': self._analyze_batch_cooking(entries, preparation_data),
            'preparation_efficiency': self._calculate_prep_efficiency(entries, preparation_data),
            'kitchen_organization': self._analyze_kitchen_workflow(entries, preparation_data)
        }

    def analyze_seasonal_adaptations(self, entries, seasonal_data):
        """Analyse des adaptations saisonnières"""
        return {
            'seasonal_preferences': self._analyze_seasonal_preferences(entries, seasonal_data),
            'ingredient_availability': self._analyze_ingredient_availability(entries, seasonal_data),
            'seasonal_transitions': self._analyze_seasonal_transitions(entries, seasonal_data),
            'climate_adaptations': self._analyze_climate_adaptations(entries, seasonal_data),
            'seasonal_nutrition': self._analyze_seasonal_nutrition(entries, seasonal_data),
            'seasonal_recommendations': self._generate_seasonal_recommendations(entries, seasonal_data)
        }

    def analyze_dietary_restrictions(self, entries, restriction_data):
        """Analyse approfondie des restrictions alimentaires"""
        return {
            'restriction_compliance': self._analyze_restriction_compliance(entries, restriction_data),
            'alternative_choices': self._analyze_alternative_choices(entries, restriction_data),
            'nutritional_adequacy': self._analyze_nutritional_adequacy(entries, restriction_data),
            'restriction_challenges': self._identify_restriction_challenges(entries, restriction_data),
            'social_impact': self._analyze_restriction_social_impact(entries, restriction_data),
            'adaptation_strategies': self._generate_restriction_strategies(entries, restriction_data)
        }

    def _detect_stress_eating(self, entries):
        """Détection des épisodes de stress alimentaire"""
        stress_indicators = {
            'rapid_eating': [],
            'large_portions': [],
            'unusual_timing': [],
            'frequent_snacking': []
        }
        
        for entry in entries:
            # Portions importantes
            if entry.calories > (self.daily_calories * 0.4):
                stress_indicators['large_portions'].append(entry)
            
            # Horaires inhabituels
            hour = entry.date.hour
            if hour < 6 or hour > 22:
                stress_indicators['unusual_timing'].append(entry)

        return {
            'episodes_count': len(stress_indicators['large_portions']),
            'risk_level': self._calculate_risk_level(stress_indicators),
            'triggers': self._identify_stress_triggers(stress_indicators)
        }

    def _identify_comfort_foods(self, entries):
        """Identification des aliments de réconfort"""
        comfort_foods = defaultdict(int)
        comfort_patterns = defaultdict(list)

        for entry in entries:
            # Analyse des aliments consommés en soirée ou lors de grands volumes
            if entry.date.hour >= 19 or entry.calories > (self.daily_calories * 0.3):
                comfort_foods[entry.food_name] += 1
                comfort_patterns[entry.food_name].append(entry.date.hour)

        return {
            'most_common': dict(sorted(comfort_foods.items(), key=lambda x: x[1], reverse=True)[:5]),
            'timing_patterns': {food: np.mean(hours) for food, hours in comfort_patterns.items()}
        }

    def _analyze_mood_patterns(self, entries):
        """Analyse des liens entre humeur et alimentation"""
        mood_patterns = {
            'morning': defaultdict(list),
            'afternoon': defaultdict(list),
            'evening': defaultdict(list)
        }

        for entry in entries:
            hour = entry.date.hour
            period = self._get_day_period(hour)
            mood_patterns[period]['calories'].append(entry.calories)
            mood_patterns[period]['foods'].append(entry.food_name)

        return {
            period: {
                'average_calories': np.mean(data['calories']),
                'common_foods': self._get_most_common(data['foods'], 3)
            }
            for period, data in mood_patterns.items()
        }

    def _detect_binge_episodes(self, entries):
        """Détection des épisodes de frénésie alimentaire"""
        binge_indicators = []
        daily_entries = defaultdict(list)

        for entry in entries:
            date = entry.date.date()
            daily_entries[date].append(entry)

        for date, day_entries in daily_entries.items():
            total_calories = sum(e.calories for e in day_entries)
            if total_calories > (self.daily_calories * 1.5):
                binge_indicators.append({
                    'date': date,
                    'total_calories': total_calories,
                    'foods': [e.food_name for e in day_entries],
                    'timing': [e.date.hour for e in day_entries]
                })

        return {
            'episodes_count': len(binge_indicators),
            'average_intensity': np.mean([b['total_calories'] for b in binge_indicators]) if binge_indicators else 0,
            'common_triggers': self._analyze_binge_triggers(binge_indicators)
        }

    def _analyze_night_eating(self, entries):
        """Analyse de l'alimentation nocturne"""
        night_entries = [e for e in entries if e.date.hour >= 22 or e.date.hour < 5]
        
        return {
            'frequency': len(night_entries),
            'average_calories': np.mean([e.calories for e in night_entries]) if night_entries else 0,
            'common_foods': self._get_most_common([e.food_name for e in night_entries], 3),
            'timing_distribution': self._analyze_timing_distribution(night_entries)
        }

    def _analyze_weekend_patterns(self, entries):
        """Analyse des habitudes alimentaires le week-end"""
        weekend_entries = [e for e in entries if e.date.weekday() >= 5]
        weekday_entries = [e for e in entries if e.date.weekday() < 5]

        return {
            'weekend_calories': np.mean([e.calories for e in weekend_entries]) if weekend_entries else 0,
            'weekday_calories': np.mean([e.calories for e in weekday_entries]) if weekday_entries else 0,
            'weekend_foods': self._get_most_common([e.food_name for e in weekend_entries], 5),
            'social_impact': self._analyze_social_impact(weekend_entries)
        }

    def _analyze_meal_company(self, entries):
        """Analyse des repas pris en compagnie"""
        # Cette fonction nécessiterait des données supplémentaires sur le contexte social
        return {
            'solo_meals': 0,
            'social_meals': 0,
            'calories_difference': 0
        }

    def _detect_special_occasions(self, entries):
        """Détection des occasions spéciales"""
        special_days = []
        daily_calories = defaultdict(float)

        for entry in entries:
            date = entry.date.date()
            daily_calories[date] += entry.calories

        mean_calories = np.mean(list(daily_calories.values()))
        std_calories = np.std(list(daily_calories.values()))

        for date, calories in daily_calories.items():
            if calories > (mean_calories + 2 * std_calories):
                special_days.append({
                    'date': date,
                    'calories': calories,
                    'excess': calories - mean_calories
                })

        return {
            'count': len(special_days),
            'average_excess': np.mean([d['excess'] for d in special_days]) if special_days else 0,
            'dates': [d['date'] for d in special_days]
        }

    def _analyze_eating_speed(self, entries):
        """Analyse de la vitesse de consommation"""
        # Cette fonction nécessiterait des données sur la durée des repas
        return {
            'fast_eating_episodes': 0,
            'average_meal_duration': 0,
            'recommendations': []
        }

    def _analyze_portion_awareness(self, entries):
        """Analyse de la conscience des portions"""
        portion_patterns = defaultdict(list)

        for entry in entries:
            meal_type = entry.meal_type.lower()
            portion_patterns[meal_type].append(entry.calories)

        return {
            'consistency': {
                meal: {
                    'average': np.mean(calories),
                    'variation': np.std(calories)
                }
                for meal, calories in portion_patterns.items()
            },
            'large_portions': sum(1 for e in entries if e.calories > (self.daily_calories * 0.4))
        }

    def _detect_distracted_eating(self, entries):
        """Détection des repas distraits"""
        # Cette fonction nécessiterait des données sur le contexte des repas
        return {
            'distracted_episodes': 0,
            'common_distractions': [],
            'impact_on_portions': 0
        }

    def _analyze_hunger_signals(self, entries):
        """Analyse des signaux de faim"""
        # Cette fonction nécessiterait des données sur la sensation de faim
        return {
            'pre_meal_hunger': 0,
            'post_meal_fullness': 0,
            'hunger_patterns': []
        }

    def _get_day_period(self, hour):
        """Détermine la période de la journée"""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'

    def _get_most_common(self, items, n=3):
        """Retourne les n éléments les plus communs"""
        counter = defaultdict(int)
        for item in items:
            counter[item] += 1
        return dict(sorted(counter.items(), key=lambda x: x[1], reverse=True)[:n])

    def _calculate_risk_level(self, indicators):
        """Calcule le niveau de risque de comportement alimentaire problématique"""
        risk_score = 0
        risk_score += len(indicators['large_portions']) * 2
        risk_score += len(indicators['unusual_timing'])
        
        if risk_score > 10:
            return 'high'
        elif risk_score > 5:
            return 'medium'
        return 'low'

    def _identify_stress_triggers(self, indicators):
        """Identifie les déclencheurs potentiels de stress alimentaire"""
        triggers = []
        if len(indicators['unusual_timing']) > 3:
            triggers.append('horaires_irreguliers')
        if len(indicators['large_portions']) > 3:
            triggers.append('portions_importantes')
        return triggers

    def _analyze_timing_distribution(self, entries):
        """Analyse la distribution horaire des repas"""
        hours = [e.date.hour for e in entries]
        return {
            'peak_hours': sorted(self._get_most_common(hours, 3).items()),
            'distribution': {h: hours.count(h) for h in range(24)}
        }

    def _analyze_social_impact(self, entries):
        """Analyse l'impact social sur l'alimentation"""
        return {
            'calories_variation': np.std([e.calories for e in entries]) if entries else 0,
            'meal_size_difference': 0,  # Nécessiterait plus de données
            'food_choices_impact': []   # Nécessiterait plus de données
        }

    def _analyze_location_impact(self, entries):
        """Analyse de l'impact de la localisation sur l'alimentation"""
        location_patterns = defaultdict(list)
        for entry in entries:
            location = getattr(entry, 'location', 'unknown')
            location_patterns[location].append(entry)

        return {
            'home_eating': self._analyze_home_eating(location_patterns.get('home', [])),
            'work_eating': self._analyze_work_eating(location_patterns.get('work', [])),
            'restaurant_eating': self._analyze_restaurant_eating(location_patterns.get('restaurant', [])),
            'location_recommendations': self._generate_location_recommendations(location_patterns)
        }

    def _analyze_weather_impact(self, entries):
        """Analyse de l'impact de la météo sur l'alimentation"""
        weather_patterns = defaultdict(list)
        for entry in entries:
            weather = getattr(entry, 'weather', 'unknown')
            weather_patterns[weather].append(entry)

        return {
            'rainy_day_eating': self._analyze_weather_specific_eating(weather_patterns.get('rain', [])),
            'sunny_day_eating': self._analyze_weather_specific_eating(weather_patterns.get('sun', [])),
            'cold_weather_eating': self._analyze_weather_specific_eating(weather_patterns.get('cold', [])),
            'hot_weather_eating': self._analyze_weather_specific_eating(weather_patterns.get('hot', []))
        }

    def _analyze_seasonal_patterns(self, entries):
        """Analyse des tendances saisonnières"""
        seasonal_data = defaultdict(list)
        for entry in entries:
            month = entry.date.month
            season = (month % 12 + 3) // 3
            seasonal_data[season].append(entry)

        return {
            'winter_patterns': self._analyze_seasonal_eating(seasonal_data.get(4, [])),
            'spring_patterns': self._analyze_seasonal_eating(seasonal_data.get(1, [])),
            'summer_patterns': self._analyze_seasonal_eating(seasonal_data.get(2, [])),
            'fall_patterns': self._analyze_seasonal_eating(seasonal_data.get(3, []))
        }

    def _analyze_time_constraints(self, entries):
        """Analyse de l'impact des contraintes temporelles"""
        time_patterns = defaultdict(list)
        for entry in entries:
            hour = entry.date.hour
            if 7 <= hour <= 9:
                period = 'rush_morning'
            elif 12 <= hour <= 14:
                period = 'lunch_break'
            elif 18 <= hour <= 20:
                period = 'evening_rush'
            else:
                period = 'flexible_time'
            time_patterns[period].append(entry)

        return {
            'rush_hour_impact': self._analyze_rush_hour_eating(time_patterns),
            'time_pressure_effects': self._analyze_time_pressure(time_patterns),
            'meal_planning_effectiveness': self._analyze_meal_planning(entries),
            'time_management_suggestions': self._generate_time_management_tips(time_patterns)
        }

    def _analyze_traditional_foods(self, entries):
        """Analyse des aliments traditionnels consommés"""
        food_categories = defaultdict(list)
        for entry in entries:
            category = self._categorize_food_tradition(entry.food_name)
            food_categories[category].append(entry)

        return {
            'traditional_frequency': {cat: len(entries) for cat, entries in food_categories.items()},
            'cultural_adaptations': self._analyze_cultural_adaptations(food_categories),
            'fusion_patterns': self._analyze_fusion_foods(entries),
            'preservation_score': self._calculate_tradition_preservation(food_categories)
        }

    def _analyze_celebration_patterns(self, entries):
        """Analyse des habitudes alimentaires lors des célébrations"""
        celebration_entries = [e for e in entries if getattr(e, 'is_celebration', False)]
        
        return {
            'celebration_frequency': len(celebration_entries),
            'special_foods': self._identify_celebration_foods(celebration_entries),
            'portion_changes': self._analyze_celebration_portions(celebration_entries),
            'social_impact': self._analyze_celebration_social_impact(celebration_entries)
        }

    def _analyze_routine_strength(self, entries):
        """Analyse de la force des routines alimentaires"""
        daily_patterns = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            day = entry.date.weekday()
            hour = entry.date.hour
            daily_patterns[day][hour].append(entry)

        routine_scores = {}
        for day, hours in daily_patterns.items():
            consistency = self._calculate_routine_consistency(hours)
            timing_regularity = self._calculate_timing_regularity(hours)
            portion_consistency = self._calculate_portion_consistency(hours)
            
            routine_scores[day] = {
                'consistency_score': consistency,
                'timing_score': timing_regularity,
                'portion_score': portion_consistency,
                'overall_score': (consistency + timing_regularity + portion_consistency) / 3
            }

        return routine_scores

    def _identify_habit_triggers(self, entries):
        """Identification des déclencheurs d'habitudes"""
        triggers = defaultdict(lambda: defaultdict(int))
        
        for entry in entries:
            time_trigger = self._identify_time_trigger(entry)
            location_trigger = self._identify_location_trigger(entry)
            emotional_trigger = self._identify_emotional_trigger(entry)
            
            triggers['time'][time_trigger] += 1
            triggers['location'][location_trigger] += 1
            triggers['emotional'][emotional_trigger] += 1

        return {
            'primary_triggers': self._get_primary_triggers(triggers),
            'trigger_patterns': self._analyze_trigger_patterns(triggers),
            'trigger_strength': self._calculate_trigger_strength(triggers)
        }

    def _analyze_stress_indicators(self, entries):
        """Analyse des indicateurs de stress"""
        stress_patterns = {
            'rapid_eating': self._detect_rapid_eating(entries),
            'irregular_timing': self._detect_irregular_timing(entries),
            'comfort_food_seeking': self._detect_comfort_food_seeking(entries),
            'portion_distortion': self._detect_portion_distortion(entries)
        }

        return {
            'stress_level': self._calculate_stress_level(stress_patterns),
            'primary_indicators': self._identify_primary_stress_indicators(stress_patterns),
            'risk_factors': self._identify_stress_risk_factors(stress_patterns),
            'coping_suggestions': self._generate_stress_coping_suggestions(stress_patterns)
        }

    def get_recommendations(self, analysis_results):
        """Génère des recommandations personnalisées basées sur l'analyse"""
        recommendations = []

        # Recommandations pour l'alimentation émotionnelle
        if analysis_results.get('emotional_eating'):
            emotional = analysis_results['emotional_eating']
            if emotional['stress_eating']['risk_level'] == 'high':
                recommendations.append({
                    'type': 'emotional',
                    'title': 'Gestion du stress alimentaire',
                    'description': 'Essayez des techniques de respiration ou de méditation avant les repas',
                    'priority': 'high'
                })

        # Recommandations pour l'alimentation sociale
        if analysis_results.get('social_eating'):
            social = analysis_results['social_eating']
            if social['weekend_vs_weekday']['weekend_calories'] > social['weekend_vs_weekday']['weekday_calories'] * 1.5:
                recommendations.append({
                    'type': 'social',
                    'title': 'Équilibre weekend',
                    'description': 'Planifiez vos repas de weekend à l\'avance pour maintenir l\'équilibre',
                    'priority': 'medium'
                })

        # Recommandations pour l'alimentation en pleine conscience
        if analysis_results.get('mindful_eating'):
            mindful = analysis_results['mindful_eating']
            if mindful['eating_speed'].get('fast_eating_episodes', 0) > 5:
                recommendations.append({
                    'type': 'mindful',
                    'title': 'Ralentir en mangeant',
                    'description': 'Prenez le temps de bien mastiquer et de savourer chaque bouchée',
                    'priority': 'medium'
                })

        return recommendations

    def _analyze_meal_timing_patterns(self, entries):
        """Analyse détaillée des patterns de timing des repas"""
        timing_data = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            hour = entry.date.hour
            day_type = 'weekend' if entry.date.weekday() >= 5 else 'weekday'
            timing_data[day_type][hour].append(entry)

        return {
            'peak_eating_times': self._identify_peak_eating_times(timing_data),
            'fasting_periods': self._analyze_fasting_periods(timing_data),
            'meal_spacing': self._analyze_meal_spacing(timing_data),
            'circadian_alignment': self._assess_circadian_alignment(timing_data),
            'timing_consistency': self._calculate_timing_consistency(timing_data)
        }

    def _analyze_sleep_correlation(self, entries):
        """Analyse de la corrélation entre sommeil et alimentation"""
        sleep_patterns = defaultdict(lambda: {
            'pre_sleep_eating': [],
            'morning_appetite': [],
            'sleep_quality': [],
            'night_eating': []
        })

        for entry in entries:
            date = entry.date.date()
            hour = entry.date.hour
            
            if hour >= 22 or hour < 5:
                sleep_patterns[date]['night_eating'].append(entry)
            elif hour >= 19:
                sleep_patterns[date]['pre_sleep_eating'].append(entry)
            elif 5 <= hour < 10:
                sleep_patterns[date]['morning_appetite'].append(entry)

        return {
            'night_eating_frequency': self._calculate_night_eating_frequency(sleep_patterns),
            'sleep_impact': self._analyze_sleep_impact(sleep_patterns),
            'morning_eating_patterns': self._analyze_morning_patterns(sleep_patterns),
            'sleep_quality_correlation': self._analyze_sleep_quality_correlation(sleep_patterns)
        }

    def _analyze_workday_patterns(self, entries, work_schedule):
        """Analyse des patterns alimentaires pendant les jours de travail"""
        workday_data = defaultdict(lambda: {
            'pre_work': [],
            'during_work': [],
            'post_work': [],
            'breaks': []
        })

        for entry in entries:
            date = entry.date.date()
            if date in work_schedule:
                period = self._categorize_work_period(entry.date, work_schedule[date])
                workday_data[date][period].append(entry)

        return {
            'work_timing_impact': self._analyze_work_timing_impact(workday_data),
            'break_patterns': self._analyze_break_patterns(workday_data),
            'workplace_influence': self._analyze_workplace_influence(workday_data),
            'stress_eating_correlation': self._analyze_work_stress_eating(workday_data)
        }

    def _analyze_physical_activity_correlation(self, entries, activity_data):
        """Analyse de la corrélation entre activité physique et alimentation"""
        activity_patterns = defaultdict(lambda: {
            'pre_activity': [],
            'during_activity': [],
            'post_activity': [],
            'recovery': []
        })

        for entry in entries:
            date = entry.date.date()
            if date in activity_data:
                period = self._categorize_activity_period(entry.date, activity_data[date])
                activity_patterns[date][period].append(entry)

        return {
            'pre_activity_nutrition': self._analyze_pre_activity_nutrition(activity_patterns),
            'post_activity_nutrition': self._analyze_post_activity_nutrition(activity_patterns),
            'performance_impact': self._analyze_nutrition_performance_impact(activity_patterns),
            'recovery_optimization': self._analyze_recovery_optimization(activity_patterns)
        }

    def _identify_peak_eating_times(self, timing_data):
        """Identification des pics de prise alimentaire"""
        peak_times = defaultdict(dict)
        
        for day_type, hours in timing_data.items():
            hourly_counts = {hour: len(entries) for hour, entries in hours.items()}
            peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_times[day_type] = {
                'primary_peaks': peak_hours,
                'consistency': self._calculate_peak_consistency(hours),
                'meal_distribution': self._analyze_meal_distribution(hours)
            }

        return peak_times

    def _analyze_fasting_periods(self, timing_data):
        """Analyse des périodes de jeûne"""
        fasting_periods = defaultdict(list)
        
        for day_type, hours in timing_data.items():
            daily_entries = defaultdict(list)
            for hour, entries in hours.items():
                for entry in entries:
                    date = entry.date.date()
                    daily_entries[date].append(entry.date)
            
            for date, times in daily_entries.items():
                sorted_times = sorted(times)
                if len(sorted_times) >= 2:
                    gaps = [(sorted_times[i+1] - sorted_times[i]).total_seconds() / 3600 
                           for i in range(len(sorted_times)-1)]
                    fasting_periods[day_type].extend(gaps)

        return {
            'average_fasting': {day: np.mean(gaps) for day, gaps in fasting_periods.items()},
            'longest_gaps': {day: max(gaps) for day, gaps in fasting_periods.items()},
            'fasting_consistency': self._calculate_fasting_consistency(fasting_periods)
        }

    def _analyze_temperature_impact(self, entries, weather_data):
        """Analyse de l'impact de la température sur l'alimentation"""
        temp_ranges = {
            'very_cold': (-float('inf'), 5),
            'cold': (5, 15),
            'mild': (15, 25),
            'warm': (25, 30),
            'hot': (30, float('inf'))
        }

        temp_patterns = defaultdict(lambda: {
            'entries': [],
            'calories': [],
            'food_types': defaultdict(int),
            'meal_sizes': [],
            'meal_times': []
        })

        for entry in entries:
            date = entry.date.date()
            if date in weather_data and 'temperature' in weather_data[date]:
                temp = weather_data[date]['temperature']
                temp_range = next(name for name, (min_t, max_t) in temp_ranges.items() 
                                if min_t <= temp < max_t)
                
                temp_patterns[temp_range]['entries'].append(entry)
                temp_patterns[temp_range]['calories'].append(entry.calories)
                temp_patterns[temp_range]['food_types'][self._categorize_food_temperature(entry.food_name)] += 1
                temp_patterns[temp_range]['meal_sizes'].append(entry.calories)
                temp_patterns[temp_range]['meal_times'].append(entry.date.hour)

        return {
            'temperature_correlations': {
                temp_range: {
                    'average_calories': np.mean(data['calories']) if data['calories'] else 0,
                    'preferred_foods': dict(sorted(data['food_types'].items(), 
                                                 key=lambda x: x[1], reverse=True)[:3]),
                    'meal_timing': self._analyze_meal_timing_distribution(data['meal_times']),
                    'meal_size_variation': np.std(data['meal_sizes']) if data['meal_sizes'] else 0
                }
                for temp_range, data in temp_patterns.items()
            },
            'temperature_adaptations': self._analyze_temperature_adaptations(temp_patterns),
            'comfort_zones': self._identify_comfort_temperature_zones(temp_patterns),
            'risk_temperatures': self._identify_risk_temperatures(temp_patterns)
        }

    def _analyze_precipitation_impact(self, entries, weather_data):
        """Analyse de l'impact des précipitations sur l'alimentation"""
        precipitation_patterns = defaultdict(lambda: {
            'entries': [],
            'delivery_orders': [],
            'comfort_foods': defaultdict(int),
            'social_eating': [],
            'meal_preparation': []
        })

        for entry in entries:
            date = entry.date.date()
            if date in weather_data and 'precipitation' in weather_data[date]:
                precip = weather_data[date]['precipitation']
                precip_type = self._categorize_precipitation(precip)
                
                precipitation_patterns[precip_type]['entries'].append(entry)
                precipitation_patterns[precip_type]['delivery_orders'].append(
                    getattr(entry, 'is_delivery', False))
                precipitation_patterns[precip_type]['comfort_foods'][
                    self._categorize_comfort_food(entry.food_name)] += 1
                precipitation_patterns[precip_type]['social_eating'].append(
                    getattr(entry, 'is_social', False))
                precipitation_patterns[precip_type]['meal_preparation'].append(
                    self._categorize_meal_preparation(entry))

        return {
            'precipitation_effects': {
                precip_type: {
                    'delivery_frequency': sum(data['delivery_orders']) / len(data['entries']) 
                                       if data['entries'] else 0,
                    'comfort_food_choices': dict(sorted(data['comfort_foods'].items(), 
                                                      key=lambda x: x[1], reverse=True)[:3]),
                    'social_eating_frequency': sum(data['social_eating']) / len(data['entries']) 
                                             if data['entries'] else 0,
                    'preparation_methods': Counter(data['meal_preparation']).most_common(3)
                }
                for precip_type, data in precipitation_patterns.items()
            },
            'behavioral_changes': self._analyze_precipitation_behavior_changes(precipitation_patterns),
            'adaptation_strategies': self._identify_precipitation_adaptations(precipitation_patterns),
            'risk_patterns': self._identify_precipitation_risks(precipitation_patterns)
        }

    def _analyze_seasonal_transitions(self, entries, weather_data):
        """Analyse des transitions saisonnières dans l'alimentation"""
        transition_periods = self._identify_seasonal_transitions(weather_data)
        transition_patterns = defaultdict(lambda: {
            'before': [],
            'during': [],
            'after': []
        })

        for transition in transition_periods:
            start_date = transition['start_date']
            end_date = transition['end_date']
            transition_type = transition['type']

            for entry in entries:
                date = entry.date.date()
                if date < start_date:
                    transition_patterns[transition_type]['before'].append(entry)
                elif start_date <= date <= end_date:
                    transition_patterns[transition_type]['during'].append(entry)
                elif date > end_date:
                    transition_patterns[transition_type]['after'].append(entry)

        return {
            'transition_adaptations': {
                trans_type: {
                    'dietary_changes': self._analyze_dietary_changes(data),
                    'adaptation_speed': self._calculate_adaptation_speed(data),
                    'preference_shifts': self._analyze_preference_shifts(data)
                }
                for trans_type, data in transition_patterns.items()
            },
            'transition_challenges': self._identify_transition_challenges(transition_patterns),
            'adaptation_strategies': self._suggest_transition_strategies(transition_patterns)
        }

    def _analyze_weather_comfort_foods(self, entries, weather_data):
        """Analyse des aliments de réconfort selon la météo"""
        comfort_patterns = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            date = entry.date.date()
            if date in weather_data:
                weather_condition = self._get_weather_condition(weather_data[date])
                comfort_category = self._categorize_comfort_food(entry.food_name)
                comfort_patterns[weather_condition][comfort_category].append(entry)

        return {
            'weather_preferences': {
                weather: {
                    'preferred_comfort_foods': self._get_preferred_comfort_foods(foods),
                    'comfort_food_frequency': self._calculate_comfort_food_frequency(foods),
                    'emotional_correlation': self._analyze_comfort_emotional_correlation(foods)
                }
                for weather, foods in comfort_patterns.items()
            },
            'comfort_triggers': self._identify_comfort_food_triggers(comfort_patterns),
            'healthy_alternatives': self._suggest_healthy_alternatives(comfort_patterns)
        }

    def _analyze_weather_hydration(self, entries, weather_data):
        """Analyse des patterns d'hydratation selon la météo"""
        hydration_patterns = defaultdict(lambda: {
            'water_intake': [],
            'hydrating_foods': [],
            'dehydrating_factors': []
        })

        for entry in entries:
            date = entry.date.date()
            if date in weather_data:
                weather_condition = self._get_weather_condition(weather_data[date])
                hydration_patterns[weather_condition]['water_intake'].append(
                    getattr(entry, 'water_content', 0))
                hydration_patterns[weather_condition]['hydrating_foods'].append(
                    self._calculate_food_hydration(entry))
                hydration_patterns[weather_condition]['dehydrating_factors'].append(
                    self._identify_dehydrating_factors(entry))

        return {
            'weather_hydration': {
                weather: {
                    'average_water_intake': np.mean(data['water_intake']) if data['water_intake'] else 0,
                    'hydration_adequacy': self._calculate_hydration_adequacy(data),
                    'risk_factors': self._identify_hydration_risks(data)
                }
                for weather, data in hydration_patterns.items()
            },
            'hydration_recommendations': self._generate_hydration_recommendations(hydration_patterns),
            'dehydration_prevention': self._suggest_prevention_strategies(hydration_patterns)
        }

    def _analyze_mood_weather_correlation(self, entries, weather_data):
        """Analyse de la corrélation entre météo, humeur et alimentation"""
        mood_patterns = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            date = entry.date.date()
            if date in weather_data:
                weather_condition = self._get_weather_condition(weather_data[date])
                mood = getattr(entry, 'mood', 'unknown')
                mood_patterns[weather_condition][mood].append(entry)

        return {
            'weather_mood_correlations': {
                weather: {
                    'mood_distribution': self._calculate_mood_distribution(moods),
                    'eating_patterns': self._analyze_mood_eating_patterns(moods),
                    'food_choices': self._analyze_mood_food_choices(moods)
                }
                for weather, moods in mood_patterns.items()
            },
            'mood_management': self._suggest_mood_management_strategies(mood_patterns),
            'weather_adaptations': self._suggest_weather_adaptations(mood_patterns)
        }

    def _analyze_meal_costs(self, entries, budget_data):
        """Analyse détaillée des coûts par repas"""
        meal_costs = defaultdict(list)
        for entry in entries:
            if entry.date.date() in budget_data:
                meal_type = self._categorize_meal_type(entry)
                cost = budget_data[entry.date.date()].get(entry.food_id, 0)
                meal_costs[meal_type].append(cost)

        return {
            'average_cost_by_meal': {meal: np.mean(costs) for meal, costs in meal_costs.items()},
            'cost_trends': self._analyze_cost_trends(meal_costs),
            'budget_efficiency': self._calculate_budget_efficiency(meal_costs),
            'cost_outliers': self._identify_cost_outliers(meal_costs)
        }

    def _analyze_travel_eating_patterns(self, entries, location_data):
        """Analyse des habitudes alimentaires en déplacement"""
        travel_patterns = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            if entry.date.date() in location_data:
                location_type = location_data[entry.date.date()]['type']
                travel_patterns[location_type]['meals'].append(entry)
                travel_patterns[location_type]['times'].append(entry.date.time())

        return {
            'location_preferences': self._analyze_location_preferences(travel_patterns),
            'timing_changes': self._analyze_travel_timing_changes(travel_patterns),
            'adaptation_speed': self._calculate_adaptation_metrics(travel_patterns),
            'dietary_challenges': self._identify_travel_challenges(travel_patterns)
        }

    def _calculate_carbon_footprint(self, entries):
        """Calcul de l'empreinte carbone des choix alimentaires"""
        carbon_data = defaultdict(float)
        
        for entry in entries:
            food_type = self._categorize_food_type(entry)
            quantity = entry.quantity
            carbon_impact = self._get_carbon_impact(food_type)
            carbon_data[entry.date.date()] += carbon_impact * quantity

        return {
            'daily_footprint': dict(carbon_data),
            'average_footprint': np.mean(list(carbon_data.values())),
            'footprint_trends': self._analyze_footprint_trends(carbon_data),
            'high_impact_foods': self._identify_high_impact_foods(entries),
            'reduction_potential': self._calculate_reduction_potential(carbon_data)
        }

    def _analyze_group_dining_patterns(self, entries, social_data):
        """Analyse des patterns de repas en groupe"""
        group_patterns = defaultdict(lambda: {
            'portion_sizes': [],
            'food_choices': [],
            'timing': [],
            'duration': [],
            'location': []
        })

        for entry in entries:
            if entry.date.date() in social_data:
                group_size = social_data[entry.date.date()].get('group_size', 1)
                group_patterns[group_size]['portion_sizes'].append(entry.portion_size)
                group_patterns[group_size]['food_choices'].append(entry.food_id)
                group_patterns[group_size]['timing'].append(entry.date.time())
                group_patterns[group_size]['duration'].append(
                    social_data[entry.date.date()].get('duration', 0))
                group_patterns[group_size]['location'].append(
                    social_data[entry.date.date()].get('location', 'unknown'))

        return {
            'size_impact': self._analyze_group_size_impact(group_patterns),
            'choice_variations': self._analyze_group_choices(group_patterns),
            'timing_patterns': self._analyze_group_timing(group_patterns),
            'duration_analysis': self._analyze_meal_durations(group_patterns),
            'location_preferences': self._analyze_group_locations(group_patterns)
        }

    def _analyze_nutrient_timing(self, entries, nutrient_data):
        """Analyse du timing optimal des nutriments"""
        nutrient_timing = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            if entry.date.date() in nutrient_data:
                hour = entry.date.hour
                nutrients = nutrient_data[entry.date.date()].get(entry.food_id, {})
                for nutrient, amount in nutrients.items():
                    nutrient_timing[nutrient][hour].append(amount)

        return {
            'optimal_timing': self._calculate_optimal_timing(nutrient_timing),
            'absorption_patterns': self._analyze_absorption_patterns(nutrient_timing),
            'timing_effectiveness': self._calculate_timing_effectiveness(nutrient_timing),
            'nutrient_interactions': self._analyze_nutrient_interactions(nutrient_timing)
        }

    def _analyze_prep_time_patterns(self, entries, preparation_data):
        """Analyse des patterns de temps de préparation"""
        prep_patterns = defaultdict(lambda: {
            'duration': [],
            'complexity': [],
            'efficiency': [],
            'satisfaction': []
        })

        for entry in entries:
            if entry.date.date() in preparation_data:
                meal_type = self._categorize_meal_type(entry)
                prep_data = preparation_data[entry.date.date()]
                prep_patterns[meal_type]['duration'].append(prep_data.get('duration', 0))
                prep_patterns[meal_type]['complexity'].append(prep_data.get('complexity', 0))
                prep_patterns[meal_type]['efficiency'].append(prep_data.get('efficiency', 0))
                prep_patterns[meal_type]['satisfaction'].append(prep_data.get('satisfaction', 0))

        return {
            'time_efficiency': self._calculate_time_efficiency(prep_patterns),
            'complexity_impact': self._analyze_complexity_impact(prep_patterns),
            'satisfaction_correlation': self._analyze_satisfaction_correlation(prep_patterns),
            'optimization_opportunities': self._identify_optimization_opportunities(prep_patterns)
        }

    def _analyze_seasonal_preferences(self, entries, seasonal_data):
        """Analyse des préférences alimentaires saisonnières"""
        seasonal_preferences = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            if entry.date.date() in seasonal_data:
                season = seasonal_data[entry.date.date()]['season']
                food_category = self._categorize_food_category(entry)
                seasonal_preferences[season][food_category].append(entry)

        return {
            'seasonal_favorites': self._identify_seasonal_favorites(seasonal_preferences),
            'transition_patterns': self._analyze_season_transitions(seasonal_preferences),
            'seasonal_nutrition': self._analyze_seasonal_nutrition_patterns(seasonal_preferences),
            'adaptation_success': self._calculate_adaptation_success(seasonal_preferences)
        }

    def _analyze_restriction_compliance(self, entries, restriction_data):
        """Analyse de la conformité aux restrictions alimentaires"""
        compliance_data = defaultdict(lambda: {
            'compliant_meals': [],
            'violations': [],
            'alternatives_used': [],
            'challenge_level': []
        })

        for entry in entries:
            if entry.date.date() in restriction_data:
                restrictions = restriction_data[entry.date.date()]['restrictions']
                for restriction in restrictions:
                    is_compliant = self._check_restriction_compliance(entry, restriction)
                    if is_compliant:
                        compliance_data[restriction]['compliant_meals'].append(entry)
                    else:
                        compliance_data[restriction]['violations'].append(entry)
                    
                    alternatives = restriction_data[entry.date.date()].get('alternatives_used', [])
                    compliance_data[restriction]['alternatives_used'].extend(alternatives)
                    
                    challenge = restriction_data[entry.date.date()].get('challenge_level', 0)
                    compliance_data[restriction]['challenge_level'].append(challenge)

        return {
            'compliance_rate': self._calculate_compliance_rate(compliance_data),
            'challenge_patterns': self._analyze_challenge_patterns(compliance_data),
            'alternative_effectiveness': self._analyze_alternative_effectiveness(compliance_data),
            'improvement_areas': self._identify_improvement_areas(compliance_data)
        }
