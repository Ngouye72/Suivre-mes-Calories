import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from lifelines import KaplanMeierFitter
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import joblib
import json

class UserAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = {
            'retention_threshold': 30,  # jours
            'engagement_metrics': [
                'login_frequency',
                'meal_logs',
                'weight_logs',
                'feature_usage',
                'session_duration'
            ],
            'clustering_n_segments': 5,
            'churn_prediction_threshold': 0.7,
            'model_path': 'models/user_analytics/'
        }
        
        # Initialisation modèles
        self.models = {
            'user_segmentation': self._init_segmentation_model(),
            'churn_predictor': self._init_churn_predictor(),
            'behavior_analyzer': self._init_behavior_analyzer()
        }

    def _init_segmentation_model(self):
        """Initialise le modèle de segmentation"""
        try:
            return KMeans(
                n_clusters=self.config['clustering_n_segments'],
                random_state=42
            )
        except Exception as e:
            self.logger.error(f"Error initializing segmentation model: {str(e)}")
            return None

    def _init_churn_predictor(self):
        """Initialise le modèle de prédiction du churn"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            return RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
        except Exception as e:
            self.logger.error(f"Error initializing churn predictor: {str(e)}")
            return None

    def _init_behavior_analyzer(self):
        """Initialise l'analyseur de comportement"""
        try:
            from sklearn.decomposition import PCA
            return PCA(n_components=3)
        except Exception as e:
            self.logger.error(f"Error initializing behavior analyzer: {str(e)}")
            return None

    def analyze_user_behavior(self, user_data: List[Dict]) -> Dict:
        """Analyse le comportement des utilisateurs"""
        try:
            df = pd.DataFrame(user_data)
            
            behavior_analysis = {
                'engagement_metrics': self._analyze_engagement(df),
                'usage_patterns': self._analyze_usage_patterns(df),
                'feature_adoption': self._analyze_feature_adoption(df),
                'meal_patterns': self._analyze_meal_patterns(df),
                'goal_progress': self._analyze_goal_progress(df)
            }
            
            return behavior_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing user behavior: {str(e)}")
            return {}

    def _analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """Analyse l'engagement des utilisateurs"""
        try:
            engagement_metrics = {
                'daily_active_users': len(
                    df[df['last_activity'] >= datetime.now() - timedelta(days=1)]
                ),
                'weekly_active_users': len(
                    df[df['last_activity'] >= datetime.now() - timedelta(days=7)]
                ),
                'monthly_active_users': len(
                    df[df['last_activity'] >= datetime.now() - timedelta(days=30)]
                ),
                'average_session_duration': df['session_duration'].mean(),
                'engagement_score': self._calculate_engagement_score(df)
            }
            
            return engagement_metrics

        except Exception as e:
            self.logger.error(f"Error analyzing engagement: {str(e)}")
            return {}

    def _analyze_usage_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns d'utilisation"""
        try:
            usage_patterns = {
                'peak_usage_hours': self._get_peak_hours(df),
                'most_used_features': self._get_popular_features(df),
                'usage_frequency': self._calculate_usage_frequency(df),
                'session_patterns': self._analyze_session_patterns(df)
            }
            
            return usage_patterns

        except Exception as e:
            self.logger.error(f"Error analyzing usage patterns: {str(e)}")
            return {}

    def _analyze_feature_adoption(self, df: pd.DataFrame) -> Dict:
        """Analyse l'adoption des fonctionnalités"""
        try:
            feature_adoption = {
                'feature_usage_rates': self._calculate_feature_usage(df),
                'feature_stickiness': self._calculate_feature_stickiness(df),
                'feature_discovery': self._analyze_feature_discovery(df),
                'popular_combinations': self._find_feature_combinations(df)
            }
            
            return feature_adoption

        except Exception as e:
            self.logger.error(f"Error analyzing feature adoption: {str(e)}")
            return {}

    def _analyze_meal_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns de repas"""
        try:
            meal_patterns = {
                'meal_timing': self._analyze_meal_timing(df),
                'meal_composition': self._analyze_meal_composition(df),
                'calorie_distribution': self._analyze_calorie_distribution(df),
                'dietary_preferences': self._analyze_dietary_preferences(df)
            }
            
            return meal_patterns

        except Exception as e:
            self.logger.error(f"Error analyzing meal patterns: {str(e)}")
            return {}

    def _analyze_goal_progress(self, df: pd.DataFrame) -> Dict:
        """Analyse la progression vers les objectifs"""
        try:
            goal_progress = {
                'goal_achievement_rate': self._calculate_goal_achievement(df),
                'progress_trends': self._analyze_progress_trends(df),
                'goal_adjustments': self._analyze_goal_adjustments(df),
                'success_factors': self._identify_success_factors(df)
            }
            
            return goal_progress

        except Exception as e:
            self.logger.error(f"Error analyzing goal progress: {str(e)}")
            return {}

    def predict_churn(self, user_data: Dict) -> Dict:
        """Prédit le risque de churn pour un utilisateur"""
        try:
            # Préparation features
            features = self._prepare_churn_features(user_data)
            
            # Prédiction
            churn_probability = self.models['churn_predictor'].predict_proba(
                features.reshape(1, -1)
            )[0][1]
            
            # Analyse facteurs de risque
            risk_factors = self._identify_churn_risk_factors(user_data)
            
            return {
                'churn_probability': churn_probability,
                'risk_level': 'high' if churn_probability > 0.7 else 'medium'
                if churn_probability > 0.4 else 'low',
                'risk_factors': risk_factors,
                'recommendations': self._generate_retention_recommendations(
                    churn_probability,
                    risk_factors
                )
            }

        except Exception as e:
            self.logger.error(f"Error predicting churn: {str(e)}")
            return {}

    def segment_users(self, user_data: List[Dict]) -> Dict:
        """Segmente les utilisateurs"""
        try:
            df = pd.DataFrame(user_data)
            
            # Préparation features
            features = self._prepare_segmentation_features(df)
            
            # Segmentation
            segments = self.models['user_segmentation'].fit_predict(features)
            
            # Analyse segments
            segment_analysis = self._analyze_segments(df, segments)
            
            return {
                'segments': segment_analysis,
                'segment_profiles': self._create_segment_profiles(
                    df,
                    segments
                ),
                'recommendations': self._generate_segment_recommendations(
                    segment_analysis
                )
            }

        except Exception as e:
            self.logger.error(f"Error segmenting users: {str(e)}")
            return {}

    def analyze_user_journey(self, user_data: Dict) -> Dict:
        """Analyse le parcours utilisateur"""
        try:
            journey_analysis = {
                'onboarding': self._analyze_onboarding(user_data),
                'key_milestones': self._identify_milestones(user_data),
                'friction_points': self._identify_friction_points(user_data),
                'success_path': self._analyze_success_path(user_data)
            }
            
            return journey_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing user journey: {str(e)}")
            return {}

    def generate_insights(self, user_data: List[Dict]) -> Dict:
        """Génère des insights utilisateur"""
        try:
            insights = {
                'timestamp': datetime.now().isoformat(),
                'behavior_analysis': self.analyze_user_behavior(user_data),
                'user_segments': self.segment_users(user_data),
                'churn_analysis': {
                    user['id']: self.predict_churn(user)
                    for user in user_data
                },
                'recommendations': self._generate_global_recommendations(
                    user_data
                )
            }
            
            return insights

        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {}

    def _calculate_engagement_score(self, df: pd.DataFrame) -> float:
        """Calcule le score d'engagement"""
        try:
            weights = {
                'login_frequency': 0.3,
                'meal_logs': 0.25,
                'weight_logs': 0.15,
                'feature_usage': 0.2,
                'session_duration': 0.1
            }
            
            scores = {}
            for metric in self.config['engagement_metrics']:
                scores[metric] = df[metric].mean() * weights[metric]
            
            return sum(scores.values())

        except Exception as e:
            self.logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0

    def _generate_retention_recommendations(
        self,
        churn_probability: float,
        risk_factors: List[str]
    ) -> List[Dict]:
        """Génère des recommandations de rétention"""
        try:
            recommendations = []
            
            if churn_probability > 0.7:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Intervention immédiate requise',
                    'suggestions': [
                        'Contacter l\'utilisateur',
                        'Offrir un coaching personnalisé',
                        'Proposer des fonctionnalités premium'
                    ]
                })
            
            for factor in risk_factors:
                if factor == 'low_engagement':
                    recommendations.append({
                        'priority': 'medium',
                        'action': 'Augmenter l\'engagement',
                        'suggestions': [
                            'Envoyer des rappels personnalisés',
                            'Proposer des défis quotidiens',
                            'Partager des succès stories'
                        ]
                    })
                elif factor == 'goal_struggles':
                    recommendations.append({
                        'priority': 'high',
                        'action': 'Soutien objectifs',
                        'suggestions': [
                            'Ajuster les objectifs',
                            'Proposer un plan plus adapté',
                            'Fournir des conseils d\'experts'
                        ]
                    })
            
            return recommendations

        except Exception as e:
            self.logger.error(
                f"Error generating retention recommendations: {str(e)}"
            )
            return []

    def _generate_global_recommendations(
        self,
        user_data: List[Dict]
    ) -> List[Dict]:
        """Génère des recommandations globales"""
        try:
            recommendations = []
            
            # Analyse engagement global
            avg_engagement = np.mean([
                user.get('engagement_score', 0) for user in user_data
            ])
            
            if avg_engagement < 0.5:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'high',
                    'action': 'Améliorer engagement global',
                    'suggestions': [
                        'Lancer une campagne de réengagement',
                        'Améliorer l\'onboarding',
                        'Ajouter des fonctionnalités gamifiées'
                    ]
                })
            
            # Analyse rétention
            churn_rate = len([
                user for user in user_data
                if self.predict_churn(user)['churn_probability'] > 0.7
            ]) / len(user_data)
            
            if churn_rate > 0.3:
                recommendations.append({
                    'type': 'retention',
                    'priority': 'critical',
                    'action': 'Réduire le taux de churn',
                    'suggestions': [
                        'Revoir la proposition de valeur',
                        'Améliorer l\'expérience utilisateur',
                        'Mettre en place un programme de fidélité'
                    ]
                })
            
            return recommendations

        except Exception as e:
            self.logger.error(
                f"Error generating global recommendations: {str(e)}"
            )
            return []

# Exemple d'utilisation:
"""
analytics = UserAnalytics()

# Données utilisateur exemple
user_data = [
    {
        'id': 1,
        'login_frequency': 0.8,
        'meal_logs': 45,
        'weight_logs': 30,
        'feature_usage': 0.7,
        'session_duration': 25,
        'last_activity': datetime.now()
    },
    # ... autres utilisateurs
]

# Analyse comportement
behavior = analytics.analyze_user_behavior(user_data)

# Prédiction churn
churn = analytics.predict_churn(user_data[0])

# Segmentation
segments = analytics.segment_users(user_data)

# Génération insights
insights = analytics.generate_insights(user_data)
"""
