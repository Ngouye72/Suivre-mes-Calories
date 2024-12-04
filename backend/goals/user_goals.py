from personal_goals import PersonalGoals

# Initialisation du calculateur d'objectifs
goals = PersonalGoals()

# Calcul des objectifs personnalisés
objectifs = goals.calculate_goals(
    age=52,
    sexe='homme',
    poids=80,
    taille=179,
    niveau_activite='très_actif',
    objectif='perte_poids',
    poids_cible=78,
    delai_semaines=6
)

# Sauvegarde des objectifs pour référence
USER_GOALS = objectifs
