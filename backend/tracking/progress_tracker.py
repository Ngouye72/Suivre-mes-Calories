import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional
import logging

class ProgressTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = [
            'poids', 'calories', 'protéines', 'glucides', 'lipides', 'eau'
        ]

    def create_progress_dashboard(self, user_data: Dict) -> Dict:
        """Crée un dashboard interactif de progression"""
        try:
            df = pd.DataFrame(user_data)
            
            dashboard = {
                'weight_progress': self._create_weight_chart(df),
                'nutrition_progress': self._create_nutrition_chart(df),
                'weekly_summary': self._create_weekly_summary(df),
                'achievements': self._track_achievements(df),
                'predictions': self._generate_predictions(df)
            }

            return dashboard

        except Exception as e:
            self.logger.error(f"Erreur création dashboard: {str(e)}")
            return {}

    def _create_weight_chart(self, df: pd.DataFrame) -> Dict:
        """Crée un graphique de progression du poids"""
        fig = go.Figure()

        # Courbe de poids réelle
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['poids'],
            name='Poids actuel',
            line=dict(color='blue', width=2),
            mode='lines+markers'
        ))

        # Objectif de poids
        if 'objectif_poids' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['objectif_poids'],
                name='Objectif',
                line=dict(color='green', dash='dash')
            ))

        # Mise en forme
        fig.update_layout(
            title='Progression du Poids',
            xaxis_title='Date',
            yaxis_title='Poids (kg)',
            template='plotly_white',
            height=400
        )

        return fig.to_dict()

    def _create_nutrition_chart(self, df: pd.DataFrame) -> Dict:
        """Crée un graphique des apports nutritionnels"""
        # Création du subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Calories', 'Macronutriments',
                'Hydratation', 'Balance Énergétique'
            )
        )

        # Calories
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['calories'],
                name='Calories',
                fill='tozeroy'
            ),
            row=1, col=1
        )

        # Macronutriments
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['protéines'],
                name='Protéines',
                marker_color='rgb(55, 83, 109)'
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['glucides'],
                name='Glucides',
                marker_color='rgb(26, 118, 255)'
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['lipides'],
                name='Lipides',
                marker_color='rgb(158, 202, 225)'
            ),
            row=1, col=2
        )

        # Hydratation
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['eau'],
                name='Eau (ml)',
                line=dict(color='lightblue', width=2)
            ),
            row=2, col=1
        )

        # Balance énergétique
        if 'calories_out' in df.columns:
            balance = df['calories_out'] - df['calories']
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=balance,
                    name='Balance',
                    marker_color=np.where(balance >= 0, 'green', 'red')
                ),
                row=2, col=2
            )

        # Mise en forme
        fig.update_layout(
            height=800,
            showlegend=True,
            template='plotly_white'
        )

        return fig.to_dict()

    def _create_weekly_summary(self, df: pd.DataFrame) -> Dict:
        """Crée un résumé hebdomadaire"""
        weekly = df.resample('W').mean()
        
        summary = {
            'moyennes': {
                metric: weekly[metric].mean()
                for metric in self.metrics
                if metric in weekly.columns
            },
            'tendances': {
                metric: self._calculate_trend(weekly[metric])
                for metric in self.metrics
                if metric in weekly.columns
            },
            'objectifs_atteints': self._calculate_goals_achieved(df)
        }

        return summary

    def _track_achievements(self, df: pd.DataFrame) -> List[Dict]:
        """Suit les réalisations et objectifs atteints"""
        achievements = []

        # Perte de poids
        if 'poids' in df.columns:
            total_loss = df['poids'].iloc[0] - df['poids'].iloc[-1]
            if total_loss > 0:
                achievements.append({
                    'type': 'perte_poids',
                    'valeur': total_loss,
                    'message': f"Perte de {total_loss:.1f}kg"
                })

        # Maintien calories
        if 'calories' in df.columns and 'objectif_calories' in df.columns:
            days_on_target = sum(
                abs(df['calories'] - df['objectif_calories']) <= 100
            )
            if days_on_target >= 5:
                achievements.append({
                    'type': 'calories',
                    'valeur': days_on_target,
                    'message': f"{days_on_target} jours dans l'objectif calorique"
                })

        # Hydratation
        if 'eau' in df.columns:
            days_hydrated = sum(df['eau'] >= 2000)
            if days_hydrated >= 5:
                achievements.append({
                    'type': 'hydratation',
                    'valeur': days_hydrated,
                    'message': f"{days_hydrated} jours bien hydraté"
                })

        return achievements

    def _generate_predictions(self, df: pd.DataFrame) -> Dict:
        """Génère des prédictions de progression"""
        predictions = {}

        if 'poids' in df.columns:
            # Calcul tendance
            weights = df['poids'].values
            days = np.arange(len(weights))
            z = np.polyfit(days, weights, 1)
            p = np.poly1d(z)

            # Prédiction 4 semaines
            future_days = np.arange(len(weights), len(weights) + 28)
            predicted_weights = p(future_days)

            predictions['poids'] = {
                'dates': [
                    (df.index[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d')
                    for i in range(28)
                ],
                'valeurs': predicted_weights.tolist(),
                'tendance': 'baisse' if z[0] < 0 else 'hausse'
            }

        return predictions

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calcule la tendance d'une série"""
        if len(series) < 2:
            return 'stable'
            
        change = series.iloc[-1] - series.iloc[0]
        if abs(change) < 0.01:
            return 'stable'
        return 'hausse' if change > 0 else 'baisse'

    def _calculate_goals_achieved(self, df: pd.DataFrame) -> Dict:
        """Calcule le taux d'atteinte des objectifs"""
        goals_achieved = {}

        for metric in self.metrics:
            goal_col = f'objectif_{metric}'
            if metric in df.columns and goal_col in df.columns:
                total_days = len(df)
                days_achieved = sum(
                    abs(df[metric] - df[goal_col]) <= 0.05 * df[goal_col]
                )
                goals_achieved[metric] = days_achieved / total_days * 100

        return goals_achieved

    def generate_progress_report(self, user_data: Dict) -> str:
        """Génère un rapport de progression détaillé"""
        try:
            df = pd.DataFrame(user_data)
            
            # Création du rapport HTML
            template = """
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .container { max-width: 800px; margin: auto; }
                    .metric { margin: 20px 0; }
                    .trend-up { color: green; }
                    .trend-down { color: red; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Rapport de Progression</h1>
                    
                    <div class="metric">
                        <h2>Poids</h2>
                        <p>Initial: {initial_weight:.1f}kg</p>
                        <p>Actuel: {current_weight:.1f}kg</p>
                        <p>Variation: <span class="{weight_trend_class}">{weight_change:+.1f}kg</span></p>
                    </div>

                    <div class="metric">
                        <h2>Nutrition</h2>
                        <p>Moyenne calories: {avg_calories:.0f}</p>
                        <p>Respect objectif: {calories_adherence:.1f}%</p>
                    </div>

                    <div class="metric">
                        <h2>Réalisations</h2>
                        {achievements}
                    </div>

                    <div class="metric">
                        <h2>Prédictions</h2>
                        {predictions}
                    </div>
                </div>
            </body>
            </html>
            """

            # Calcul des métriques
            weight_change = df['poids'].iloc[-1] - df['poids'].iloc[0]
            weight_trend_class = 'trend-down' if weight_change < 0 else 'trend-up'

            # Formatage des réalisations
            achievements_html = "<ul>"
            for achievement in self._track_achievements(df):
                achievements_html += f"<li>{achievement['message']}</li>"
            achievements_html += "</ul>"

            # Formatage des prédictions
            predictions = self._generate_predictions(df)
            predictions_html = "<ul>"
            if 'poids' in predictions:
                final_weight = predictions['poids']['valeurs'][-1]
                predictions_html += f"<li>Poids prévu dans 4 semaines: {final_weight:.1f}kg</li>"
            predictions_html += "</ul>"

            # Génération du rapport
            report = template.format(
                initial_weight=df['poids'].iloc[0],
                current_weight=df['poids'].iloc[-1],
                weight_change=weight_change,
                weight_trend_class=weight_trend_class,
                avg_calories=df['calories'].mean(),
                calories_adherence=self._calculate_goals_achieved(df).get('calories', 0),
                achievements=achievements_html,
                predictions=predictions_html
            )

            return report

        except Exception as e:
            self.logger.error(f"Erreur génération rapport: {str(e)}")
            return ""

# Exemple d'utilisation:
"""
tracker = ProgressTracker()

# Données exemple
user_data = {
    'date': pd.date_range(start='2024-01-01', periods=30),
    'poids': np.linspace(80, 78, 30),
    'calories': np.random.normal(2000, 200, 30),
    'protéines': np.random.normal(80, 10, 30),
    'glucides': np.random.normal(250, 25, 30),
    'lipides': np.random.normal(65, 8, 30),
    'eau': np.random.normal(2000, 300, 30),
    'objectif_poids': [75] * 30,
    'objectif_calories': [2000] * 30
}

# Création dashboard
dashboard = tracker.create_progress_dashboard(user_data)

# Génération rapport
report = tracker.generate_progress_report(user_data)
"""
