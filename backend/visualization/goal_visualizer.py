import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json

class GoalVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#2E86C1',
            'secondary': '#28B463',
            'accent': '#E74C3C',
            'light': '#85C1E9',
            'background': '#F8F9F9'
        }

    def _convert_to_serializable(self, fig_dict: Dict) -> Dict:
        """Convertit les données numpy en types Python standards"""
        return json.loads(json.dumps(fig_dict, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else str(x) if isinstance(x, (np.int64, np.float64)) else x))

    def create_weight_trajectory_chart(
        self,
        poids_initial: float = 80,
        poids_cible: float = 78,
        delai_semaines: int = 6
    ) -> Dict:
        """Crée un graphique de trajectoire de poids"""
        
        # Génération des dates
        dates = pd.date_range(
            start=datetime.now(),
            periods=delai_semaines * 7 + 1,
            freq='D'
        )

        # Calcul de la trajectoire idéale
        perte_totale = poids_initial - poids_cible
        perte_journaliere = perte_totale / (delai_semaines * 7)
        trajectoire_ideale = [
            poids_initial - (perte_journaliere * i)
            for i in range(len(dates))
        ]

        # Création du graphique
        fig = go.Figure()

        # Trajectoire idéale
        fig.add_trace(go.Scatter(
            x=dates,
            y=trajectoire_ideale,
            name='Trajectoire idéale',
            line=dict(color=self.colors['primary'], width=2),
            mode='lines'
        ))

        # Zone de confiance (±0.5kg)
        fig.add_trace(go.Scatter(
            x=dates,
            y=[y + 0.5 for y in trajectoire_ideale],
            fill=None,
            mode='lines',
            line=dict(color=self.colors['light'], width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=[y - 0.5 for y in trajectoire_ideale],
            fill='tonexty',
            mode='lines',
            line=dict(color=self.colors['light'], width=0),
            name='Zone optimale'
        ))

        # Points clés
        fig.add_trace(go.Scatter(
            x=[dates[0], dates[-1]],
            y=[poids_initial, poids_cible],
            mode='markers+text',
            marker=dict(size=10, color=self.colors['accent']),
            text=['Début', 'Objectif'],
            textposition='top center',
            name='Points clés'
        ))

        # Mise en forme
        fig.update_layout(
            title='Trajectoire de Poids Prévue',
            xaxis_title='Date',
            yaxis_title='Poids (kg)',
            template='plotly_white',
            height=500,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return self._convert_to_serializable(fig.to_dict())

    def create_macro_distribution_chart(
        self,
        calories: float = 2650,
        proteines: float = 230,
        glucides: float = 265,
        lipides: float = 75
    ) -> Dict:
        """Crée un graphique de distribution des macronutriments"""
        
        # Création du subplot
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'bar'}]],
            subplot_titles=(
                'Répartition des Calories',
                'Objectifs Macronutriments (g)'
            )
        )

        # Camembert des calories
        calories_proteines = proteines * 4
        calories_glucides = glucides * 4
        calories_lipides = lipides * 9

        fig.add_trace(
            go.Pie(
                labels=['Protéines', 'Glucides', 'Lipides'],
                values=[
                    calories_proteines,
                    calories_glucides,
                    calories_lipides
                ],
                marker=dict(
                    colors=[
                        self.colors['primary'],
                        self.colors['secondary'],
                        self.colors['accent']
                    ]
                ),
                textinfo='percent+label',
                hole=.4,
                showlegend=False
            ),
            row=1, col=1
        )

        # Barres des macronutriments
        fig.add_trace(
            go.Bar(
                x=['Protéines', 'Glucides', 'Lipides'],
                y=[proteines, glucides, lipides],
                marker_color=[
                    self.colors['primary'],
                    self.colors['secondary'],
                    self.colors['accent']
                ],
                text=[f"{v}g" for v in [proteines, glucides, lipides]],
                textposition='auto',
            ),
            row=1, col=2
        )

        # Mise en forme
        fig.update_layout(
            title='Distribution des Macronutriments',
            height=500,
            showlegend=False
        )

        return self._convert_to_serializable(fig.to_dict())

    def create_daily_targets_chart(
        self,
        calories: float = 2650,
        hydratation: float = 3600
    ) -> Dict:
        """Crée un graphique des objectifs journaliers"""
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=(
                'Objectif Calorique',
                'Objectif Hydratation'
            )
        )

        # Jauge calories
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=0,  # Valeur initiale
                delta={'reference': calories},
                gauge={
                    'axis': {'range': [None, calories * 1.2]},
                    'bar': {'color': self.colors['primary']},
                    'steps': [
                        {'range': [0, calories * 0.8], 'color': self.colors['light']},
                        {'range': [calories * 0.8, calories * 1.1], 'color': self.colors['background']}
                    ],
                    'threshold': {
                        'line': {'color': self.colors['accent'], 'width': 4},
                        'thickness': 0.75,
                        'value': calories
                    }
                },
                title={'text': "Calories"}
            ),
            row=1, col=1
        )

        # Jauge hydratation
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=0,  # Valeur initiale
                delta={'reference': hydratation},
                gauge={
                    'axis': {'range': [None, hydratation * 1.2]},
                    'bar': {'color': self.colors['secondary']},
                    'steps': [
                        {'range': [0, hydratation * 0.8], 'color': self.colors['light']},
                        {'range': [hydratation * 0.8, hydratation * 1.1], 'color': self.colors['background']}
                    ],
                    'threshold': {
                        'line': {'color': self.colors['accent'], 'width': 4},
                        'thickness': 0.75,
                        'value': hydratation
                    }
                },
                title={'text': "Hydratation (ml)"}
            ),
            row=1, col=2
        )

        # Mise en forme
        fig.update_layout(
            title='Objectifs Journaliers',
            height=400,
            showlegend=False
        )

        return self._convert_to_serializable(fig.to_dict())

    def create_weekly_goals_chart(
        self,
        poids_initial: float = 80,
        poids_cible: float = 78,
        delai_semaines: int = 6
    ) -> Dict:
        """Crée un graphique des objectifs hebdomadaires"""
        
        # Calcul des objectifs hebdomadaires
        perte_hebdo = (poids_initial - poids_cible) / delai_semaines
        objectifs = [
            poids_initial - (perte_hebdo * i)
            for i in range(delai_semaines + 1)
        ]
        semaines = [f"Semaine {i}" for i in range(delai_semaines + 1)]

        # Création du graphique
        fig = go.Figure()

        # Ligne d'objectif
        fig.add_trace(go.Scatter(
            x=semaines,
            y=objectifs,
            mode='lines+markers+text',
            name='Objectif',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=10),
            text=[f"{y:.1f} kg" for y in objectifs],
            textposition='top center'
        ))

        # Mise en forme
        fig.update_layout(
            title='Objectifs Hebdomadaires',
            xaxis_title='Période',
            yaxis_title='Poids (kg)',
            template='plotly_white',
            height=400,
            showlegend=False
        )

        return self._convert_to_serializable(fig.to_dict())

    def create_dashboard(
        self,
        poids_initial: float = 80,
        poids_cible: float = 78,
        delai_semaines: int = 6,
        calories: float = 2650,
        proteines: float = 230,
        glucides: float = 265,
        lipides: float = 75,
        hydratation: float = 3600
    ) -> Dict:
        """Crée un dashboard complet des objectifs"""
        
        # Création des graphiques individuels
        weight_chart = self.create_weight_trajectory_chart(
            poids_initial, poids_cible, delai_semaines
        )
        macro_chart = self.create_macro_distribution_chart(
            calories, proteines, glucides, lipides
        )
        daily_chart = self.create_daily_targets_chart(
            calories, hydratation
        )
        weekly_chart = self.create_weekly_goals_chart(
            poids_initial, poids_cible, delai_semaines
        )

        return {
            'weight_trajectory': weight_chart,
            'macro_distribution': macro_chart,
            'daily_targets': daily_chart,
            'weekly_goals': weekly_chart
        }

# Exemple d'utilisation
"""
visualizer = GoalVisualizer()

# Création du dashboard
dashboard = visualizer.create_dashboard(
    poids_initial=80,
    poids_cible=78,
    delai_semaines=6,
    calories=2650,
    proteines=230,
    glucides=265,
    lipides=75,
    hydratation=3600
)
"""
