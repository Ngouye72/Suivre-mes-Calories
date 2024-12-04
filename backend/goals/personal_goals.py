import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

class PersonalGoals:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.activity_levels = {
            'sédentaire': 1.2,
            'légèrement_actif': 1.375,
            'modérément_actif': 1.55,
            'très_actif': 1.725,
            'extrêmement_actif': 1.9
        }

    def calculate_goals(
        self,
        age: int,
        sexe: str,
        poids: float,
        taille: float,
        niveau_activite: str,
        objectif: str,
        poids_cible: Optional[float] = None,
        delai_semaines: Optional[int] = 12
    ) -> Dict:
        """Calcule les objectifs personnalisés"""
        try:
            # Calcul du métabolisme de base (formule de Mifflin-St Jeor)
            if sexe.lower() == 'homme':
                bmr = 10 * poids + 6.25 * taille - 5 * age + 5
            else:
                bmr = 10 * poids + 6.25 * taille - 5 * age - 161

            # Ajustement selon niveau d'activité
            tdee = bmr * self.activity_levels.get(niveau_activite, 1.2)

            # Ajustement selon l'objectif
            calories_objectif = self._adjust_calories(
                tdee, objectif, poids, poids_cible, delai_semaines
            )

            # Calcul des macronutriments
            macros = self._calculate_macros(
                calories_objectif, poids, objectif
            )

            # Calcul de l'hydratation
            hydratation = self._calculate_hydration(poids, niveau_activite)

            # Création des objectifs hebdomadaires
            weekly_goals = self._create_weekly_goals(
                poids, poids_cible, delai_semaines
            )

            return {
                'calories': {
                    'total': round(calories_objectif),
                    'min': round(calories_objectif * 0.95),
                    'max': round(calories_objectif * 1.05),
                    'repartition': self._calculate_meal_distribution(calories_objectif)
                },
                'macronutriments': macros,
                'hydratation': hydratation,
                'objectifs_hebdomadaires': weekly_goals,
                'recommandations': self._generate_recommendations(
                    objectif, niveau_activite
                )
            }

        except Exception as e:
            self.logger.error(f"Erreur calcul objectifs: {str(e)}")
            return {}

    def _adjust_calories(
        self,
        tdee: float,
        objectif: str,
        poids: float,
        poids_cible: Optional[float],
        delai_semaines: Optional[int]
    ) -> float:
        """Ajuste les calories selon l'objectif"""
        if objectif == 'perte_poids' and poids_cible and delai_semaines:
            # Calcul du déficit nécessaire
            poids_a_perdre = poids - poids_cible
            calories_deficit = (poids_a_perdre * 7700) / (delai_semaines * 7)
            # Maximum 20% de déficit
            max_deficit = tdee * 0.2
            return tdee - min(calories_deficit, max_deficit)
        
        elif objectif == 'prise_poids' and poids_cible and delai_semaines:
            # Calcul du surplus nécessaire
            poids_a_prendre = poids_cible - poids
            calories_surplus = (poids_a_prendre * 7700) / (delai_semaines * 7)
            # Maximum 15% de surplus
            max_surplus = tdee * 0.15
            return tdee + min(calories_surplus, max_surplus)
        
        else:  # maintien
            return tdee

    def _calculate_macros(
        self,
        calories: float,
        poids: float,
        objectif: str
    ) -> Dict:
        """Calcule la répartition des macronutriments"""
        if objectif == 'perte_poids':
            proteine_ratio = 0.35  # Plus de protéines pour préserver la masse
            lipide_ratio = 0.25
            glucide_ratio = 0.40
        elif objectif == 'prise_poids':
            proteine_ratio = 0.25
            lipide_ratio = 0.25
            glucide_ratio = 0.50  # Plus de glucides pour le surplus
        else:  # maintien
            proteine_ratio = 0.30
            lipide_ratio = 0.25
            glucide_ratio = 0.45

        return {
            'proteines': {
                'grammes': round(calories * proteine_ratio / 4),
                'ratio': proteine_ratio,
                'min_par_repas': round(0.3 * poids)  # Minimum 0.3g/kg par repas
            },
            'glucides': {
                'grammes': round(calories * glucide_ratio / 4),
                'ratio': glucide_ratio,
                'min_par_repas': 30  # Minimum 30g par repas
            },
            'lipides': {
                'grammes': round(calories * lipide_ratio / 9),
                'ratio': lipide_ratio,
                'min_par_repas': 10  # Minimum 10g par repas
            }
        }

    def _calculate_hydration(
        self,
        poids: float,
        niveau_activite: str
    ) -> Dict:
        """Calcule les besoins en hydratation"""
        # Base: 35ml/kg
        base_hydration = poids * 35

        # Ajustement selon niveau d'activité
        activity_multipliers = {
            'sédentaire': 1.0,
            'légèrement_actif': 1.1,
            'modérément_actif': 1.2,
            'très_actif': 1.3,
            'extrêmement_actif': 1.4
        }

        total_hydration = base_hydration * activity_multipliers.get(
            niveau_activite, 1.0
        )

        return {
            'total_ml': round(total_hydration),
            'repartition': {
                'matin': round(total_hydration * 0.3),
                'midi': round(total_hydration * 0.3),
                'apres_midi': round(total_hydration * 0.2),
                'soir': round(total_hydration * 0.2)
            },
            'recommandations': [
                "Boire un verre d'eau au réveil",
                "Boire avant, pendant et après l'exercice",
                "Avoir une bouteille d'eau à portée de main"
            ]
        }

    def _create_weekly_goals(
        self,
        poids_initial: float,
        poids_cible: Optional[float],
        delai_semaines: Optional[int]
    ) -> List[Dict]:
        """Crée des objectifs hebdomadaires"""
        if not (poids_cible and delai_semaines):
            return []

        poids_total = poids_initial - poids_cible
        poids_hebdo = poids_total / delai_semaines

        return [{
            'semaine': i + 1,
            'poids_cible': round(poids_initial - poids_hebdo * (i + 1), 1),
            'objectifs': self._generate_weekly_objectives(i + 1)
        } for i in range(delai_semaines)]

    def _calculate_meal_distribution(self, calories: float) -> Dict:
        """Calcule la répartition des calories par repas"""
        return {
            'petit_dejeuner': round(calories * 0.25),
            'dejeuner': round(calories * 0.35),
            'collation': round(calories * 0.10),
            'diner': round(calories * 0.30)
        }

    def _generate_weekly_objectives(self, week: int) -> List[str]:
        """Génère des objectifs hebdomadaires spécifiques"""
        base_objectives = [
            "Respecter les apports caloriques quotidiens",
            "Atteindre l'objectif d'hydratation",
            "Maintenir l'équilibre des macronutriments"
        ]

        progressive_objectives = [
            "Introduire un nouveau légume",
            "Ajouter une séance d'activité physique",
            "Préparer un repas équilibré",
            "Tenir un journal alimentaire complet"
        ]

        # Ajoute progressivement des objectifs
        num_objectives = min(3 + week // 2, len(progressive_objectives))
        return base_objectives + progressive_objectives[:num_objectives]

    def _generate_recommendations(
        self,
        objectif: str,
        niveau_activite: str
    ) -> List[str]:
        """Génère des recommandations personnalisées"""
        recommendations = [
            "Prenez vos repas à heures régulières",
            "Mastiquez lentement et prenez le temps de manger",
            "Buvez régulièrement de l'eau tout au long de la journée"
        ]

        if objectif == 'perte_poids':
            recommendations.extend([
                "Privilégiez les aliments riches en protéines",
                "Augmentez la consommation de légumes",
                "Évitez les calories liquides (sodas, jus)"
            ])
        elif objectif == 'prise_poids':
            recommendations.extend([
                "Ajoutez des collations nutritives",
                "Augmentez progressivement les portions",
                "Privilégiez les aliments caloriquement denses"
            ])

        if niveau_activite in ['modérément_actif', 'très_actif', 'extrêmement_actif']:
            recommendations.extend([
                "Adaptez vos apports selon l'intensité de l'exercice",
                "Prévoyez une collation post-entraînement",
                "Surveillez votre hydratation pendant l'effort"
            ])

        return recommendations

# Exemple d'utilisation:
"""
goals = PersonalGoals()

# Calcul des objectifs
objectifs = goals.calculate_goals(
    age=30,
    sexe='homme',
    poids=80,
    taille=175,
    niveau_activite='modérément_actif',
    objectif='perte_poids',
    poids_cible=70,
    delai_semaines=12
)

# Affichage des objectifs
print("Objectifs caloriques:", objectifs['calories'])
print("\nMacronutriments:", objectifs['macronutriments'])
print("\nHydratation:", objectifs['hydratation'])
print("\nRecommandations:", objectifs['recommandations'])
"""
