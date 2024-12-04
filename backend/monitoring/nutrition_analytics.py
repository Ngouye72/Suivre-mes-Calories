import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging

class NutritionAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

    def analyze_meal_patterns(self, meal_data: Dict) -> Dict:
        """Analyse approfondie des habitudes alimentaires"""
        try:
            df = pd.DataFrame(meal_data)
            
            # Analyse des horaires de repas
            meal_timing = {
                'breakfast': self._analyze_meal_timing(df, 'breakfast'),
                'lunch': self._analyze_meal_timing(df, 'lunch'),
                'dinner': self._analyze_meal_timing(df, 'dinner'),
                'snacks': self._analyze_meal_timing(df, 'snacks')
            }

            # Analyse des portions et calories
            portion_analysis = {
                'average_portions': df.groupby('meal_type')['portion_size'].mean(),
                'calorie_distribution': df.groupby('meal_type')['calories'].describe(),
                'portion_trends': self._analyze_portion_trends(df)
            }

            # Analyse nutritionnelle
            nutrition_analysis = {
                'macro_balance': self._analyze_macro_balance(df),
                'nutrient_adequacy': self._analyze_nutrient_adequacy(df),
                'deficiencies': self._identify_deficiencies(df)
            }

            return {
                'meal_timing': meal_timing,
                'portion_analysis': portion_analysis,
                'nutrition_analysis': nutrition_analysis,
                'insights': self._generate_nutrition_insights(
                    meal_timing,
                    portion_analysis,
                    nutrition_analysis
                )
            }

        except Exception as e:
            self.logger.error(f"Error analyzing meal patterns: {str(e)}")
            return {}

    def predict_weight_trajectory(
        self,
        user_data: Dict,
        target_weight: float,
        timeline_weeks: int = 12
    ) -> Dict:
        """Prédit la trajectoire de poids et l'atteinte des objectifs"""
        try:
            df = pd.DataFrame(user_data)
            
            # Préparation des données
            features = self._prepare_weight_features(df)
            X = self.scaler.fit_transform(features)
            y = df['weight'].values

            # Entraînement du modèle
            self.model.fit(X, y)

            # Génération des prédictions
            future_dates = pd.date_range(
                start=df.index[-1],
                periods=timeline_weeks * 7,
                freq='D'
            )
            future_features = self._generate_future_features(
                features,
                timeline_weeks
            )
            future_X = self.scaler.transform(future_features)
            predictions = self.model.predict(future_X)

            # Analyse de la trajectoire
            trajectory_analysis = self._analyze_weight_trajectory(
                predictions,
                target_weight
            )

            # Recommandations personnalisées
            recommendations = self._generate_weight_recommendations(
                trajectory_analysis,
                target_weight
            )

            return {
                'predictions': list(zip(future_dates, predictions)),
                'trajectory_analysis': trajectory_analysis,
                'target_achievement': self._estimate_target_achievement(
                    predictions,
                    target_weight
                ),
                'recommendations': recommendations
            }

        except Exception as e:
            self.logger.error(f"Error predicting weight trajectory: {str(e)}")
            return {}

    def _analyze_meal_timing(self, df: pd.DataFrame, meal_type: str) -> Dict:
        """Analyse détaillée des horaires de repas"""
        meal_df = df[df['meal_type'] == meal_type]
        
        if meal_df.empty:
            return {}

        times = pd.to_datetime(meal_df['time']).dt.time
        
        return {
            'average_time': times.mode()[0].strftime('%H:%M'),
            'time_variance': times.std().total_seconds() / 3600,  # en heures
            'regularity_score': self._calculate_timing_regularity(times),
            'optimal_window': self._determine_optimal_window(times)
        }

    def _analyze_portion_trends(self, df: pd.DataFrame) -> Dict:
        """Analyse les tendances dans les tailles de portions"""
        trends = {
            'weekly_average': df.resample('W')['portion_size'].mean(),
            'variation': df['portion_size'].std(),
            'trend_direction': 'increasing' if df['portion_size'].is_monotonic_increasing
                             else 'decreasing' if df['portion_size'].is_monotonic_decreasing
                             else 'fluctuating'
        }
        
        return trends

    def _analyze_macro_balance(self, df: pd.DataFrame) -> Dict:
        """Analyse l'équilibre des macronutriments"""
        macros = {
            'proteins': df['proteins'].sum(),
            'carbs': df['carbs'].sum(),
            'fats': df['fats'].sum()
        }
        
        total = sum(macros.values())
        ratios = {k: v/total for k, v in macros.items()}
        
        return {
            'current_ratios': ratios,
            'ideal_ratios': {'proteins': 0.3, 'carbs': 0.4, 'fats': 0.3},
            'balance_score': self._calculate_macro_balance_score(ratios)
        }

    def _analyze_nutrient_adequacy(self, df: pd.DataFrame) -> Dict:
        """Analyse l'adéquation des nutriments"""
        daily_nutrients = df.groupby(df.index.date).sum()
        
        recommended = {
            'fiber': 25,  # g
            'vitamin_c': 90,  # mg
            'calcium': 1000,  # mg
            'iron': 18,  # mg
        }
        
        adequacy = {}
        for nutrient, target in recommended.items():
            if nutrient in daily_nutrients.columns:
                actual = daily_nutrients[nutrient].mean()
                adequacy[nutrient] = {
                    'actual': actual,
                    'target': target,
                    'adequacy_ratio': actual / target
                }
        
        return adequacy

    def _identify_deficiencies(self, df: pd.DataFrame) -> List[Dict]:
        """Identifie les carences potentielles"""
        deficiencies = []
        daily_nutrients = df.groupby(df.index.date).sum()
        
        nutrient_thresholds = {
            'fiber': 20,
            'vitamin_c': 60,
            'calcium': 800,
            'iron': 14,
        }
        
        for nutrient, threshold in nutrient_thresholds.items():
            if nutrient in daily_nutrients.columns:
                avg_intake = daily_nutrients[nutrient].mean()
                if avg_intake < threshold:
                    deficiencies.append({
                        'nutrient': nutrient,
                        'current_intake': avg_intake,
                        'recommended': threshold,
                        'severity': self._calculate_deficiency_severity(
                            avg_intake,
                            threshold
                        )
                    })
        
        return deficiencies

    def _prepare_weight_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les features pour la prédiction de poids"""
        features = pd.DataFrame()
        
        # Tendance de poids
        features['weight_trend'] = df['weight'].rolling(window=7).mean()
        
        # Variation calorique
        features['calorie_deficit'] = df['calories_out'] - df['calories_in']
        
        # Activité physique
        features['activity_level'] = df['activity_minutes']
        
        # Conformité au régime
        features['diet_adherence'] = (
            df['calories_in'] <= df['calorie_target']
        ).astype(int)
        
        return features

    def _analyze_weight_trajectory(
        self,
        predictions: np.ndarray,
        target_weight: float
    ) -> Dict:
        """Analyse la trajectoire de poids prédite"""
        current_weight = predictions[0]
        weight_change = predictions[-1] - current_weight
        
        return {
            'total_change': weight_change,
            'weekly_rate': weight_change / len(predictions) * 7,
            'consistency': self._calculate_trajectory_consistency(predictions),
            'milestone_dates': self._identify_milestone_dates(
                predictions,
                target_weight
            )
        }

    def _generate_weight_recommendations(
        self,
        trajectory: Dict,
        target_weight: float
    ) -> List[Dict]:
        """Génère des recommandations personnalisées"""
        recommendations = []
        
        # Analyse du taux de perte/gain
        weekly_rate = abs(trajectory['weekly_rate'])
        if weekly_rate > 1:
            recommendations.append({
                'type': 'warning',
                'message': 'Le taux de changement de poids est trop rapide',
                'action': 'Ajustez votre déficit/surplus calorique'
            })
        
        # Analyse de la consistance
        if trajectory['consistency'] < 0.7:
            recommendations.append({
                'type': 'consistency',
                'message': 'La progression manque de consistance',
                'action': 'Maintenez des habitudes plus régulières'
            })
        
        return recommendations

    def _calculate_timing_regularity(self, times) -> float:
        """Calcule un score de régularité des horaires"""
        time_diffs = np.diff([t.hour * 60 + t.minute for t in times])
        return 1 - (np.std(time_diffs) / (24 * 60))

    def _determine_optimal_window(self, times) -> Dict:
        """Détermine la fenêtre optimale pour un repas"""
        hours = [t.hour + t.minute/60 for t in times]
        window_start = np.percentile(hours, 25)
        window_end = np.percentile(hours, 75)
        
        return {
            'start': f"{int(window_start):02d}:{int((window_start % 1) * 60):02d}",
            'end': f"{int(window_end):02d}:{int((window_end % 1) * 60):02d}"
        }

    def _calculate_macro_balance_score(self, ratios: Dict) -> float:
        """Calcule un score d'équilibre des macros"""
        ideal = {'proteins': 0.3, 'carbs': 0.4, 'fats': 0.3}
        return 1 - sum(abs(ratios[k] - ideal[k]) for k in ideal) / 2

    def _calculate_deficiency_severity(
        self,
        current: float,
        recommended: float
    ) -> str:
        """Calcule la sévérité d'une carence"""
        ratio = current / recommended
        if ratio < 0.5:
            return 'severe'
        elif ratio < 0.75:
            return 'moderate'
        else:
            return 'mild'

    def _calculate_trajectory_consistency(self, predictions: np.ndarray) -> float:
        """Calcule la consistance de la trajectoire"""
        diffs = np.diff(predictions)
        return np.mean(np.sign(diffs[1:]) == np.sign(diffs[:-1]))

    def _identify_milestone_dates(
        self,
        predictions: np.ndarray,
        target_weight: float
    ) -> List[Dict]:
        """Identifie les dates importantes dans la trajectoire"""
        milestones = []
        start_weight = predictions[0]
        total_change = target_weight - start_weight
        
        for i, weight in enumerate(predictions):
            progress = (weight - start_weight) / total_change
            if progress in [0.25, 0.5, 0.75]:
                milestones.append({
                    'day': i,
                    'weight': weight,
                    'progress': progress
                })
        
        return milestones

    def _estimate_target_achievement(
        self,
        predictions: np.ndarray,
        target_weight: float
    ) -> Dict:
        """Estime l'atteinte de l'objectif"""
        final_weight = predictions[-1]
        progress = (final_weight - predictions[0]) / (target_weight - predictions[0])
        
        return {
            'will_achieve': abs(final_weight - target_weight) < 1,
            'progress_ratio': progress,
            'estimated_completion': len(predictions) if progress >= 1 else None
        }

# Exemple d'utilisation:
"""
analytics = NutritionAnalytics()

# Analyse des repas
meal_data = {
    'meal_type': ['breakfast', 'lunch', 'dinner'],
    'time': ['08:00', '12:30', '19:00'],
    'portion_size': [300, 400, 350],
    'calories': [400, 600, 500],
    'proteins': [20, 30, 25],
    'carbs': [50, 60, 45],
    'fats': [15, 20, 18]
}
meal_analysis = analytics.analyze_meal_patterns(meal_data)

# Prédiction de poids
user_data = {
    'weight': [80, 79.5, 79.2, 78.8],
    'calories_in': [2000, 1800, 1900, 1850],
    'calories_out': [2200, 2100, 2150, 2000],
    'activity_minutes': [30, 45, 40, 35],
    'calorie_target': [1900, 1900, 1900, 1900]
}
weight_prediction = analytics.predict_weight_trajectory(user_data, 75.0)
"""
