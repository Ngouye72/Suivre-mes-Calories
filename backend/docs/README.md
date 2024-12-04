# Documentation API Nutrition Tracking

## Vue d'ensemble

Cette API permet de gérer le suivi nutritionnel et l'analyse comportementale des utilisateurs. Elle fournit des endpoints pour :

- Gestion des utilisateurs et authentification
- Suivi des repas et de l'alimentation
- Analyses nutritionnelles et comportementales
- Gestion des notifications
- Synchronisation des données

## Accès à la Documentation

La documentation interactive de l'API est disponible via Swagger UI à l'adresse :

- Production : https://api.calories.example.com/api/docs
- Staging : https://staging-api.calories.example.com/api/docs
- Local : http://localhost:5000/api/docs

## Authentification

L'API utilise l'authentification JWT (JSON Web Token). Pour accéder aux endpoints protégés :

1. Obtenez un token via `/auth/login`
2. Incluez le token dans le header Authorization : `Bearer <token>`

## Endpoints Principaux

### Authentification

- `POST /auth/register` : Inscription d'un nouvel utilisateur
- `POST /auth/login` : Connexion utilisateur
- `POST /auth/logout` : Déconnexion

### Repas

- `GET /meals` : Liste des repas
- `POST /meals` : Ajouter un repas
- `GET /meals/{id}` : Détails d'un repas
- `PUT /meals/{id}` : Modifier un repas
- `DELETE /meals/{id}` : Supprimer un repas

### Analyses

- `GET /analysis/nutrients` : Analyse nutritionnelle
- `GET /analysis/behavior` : Analyse comportementale
- `GET /analysis/weather` : Impact météo
- `GET /analysis/circadian` : Rythme circadien
- `GET /analysis/social` : Contexte social

## Modèles de Données

### User
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user123",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Meal
```json
{
  "id": 1,
  "name": "Déjeuner",
  "calories": 500,
  "protein": 20,
  "carbs": 60,
  "fat": 15,
  "meal_time": "2024-01-01T12:30:00Z"
}
```

### NutrientAnalysis
```json
{
  "total_calories": 2000,
  "average_daily_calories": 1800,
  "macros": {
    "protein": 80,
    "carbs": 250,
    "fat": 65
  }
}
```

## Gestion des Erreurs

L'API utilise les codes HTTP standards :

- 200 : Succès
- 201 : Création réussie
- 400 : Requête invalide
- 401 : Non autorisé
- 404 : Non trouvé
- 500 : Erreur serveur

Les réponses d'erreur suivent ce format :
```json
{
  "error": "Description de l'erreur",
  "details": {
    "field": "Message d'erreur spécifique"
  }
}
```

## Limites et Quotas

- Rate limiting : 100 requêtes par minute par IP
- Taille maximale des requêtes : 10MB
- Limite de pagination : 100 items par page

## Versions

- v1 : Version actuelle (stable)
- v2 : En développement (beta)

## Support

Pour toute question ou problème :

- Email : support@calories.example.com
- Documentation : https://docs.calories.example.com
- Status API : https://status.calories.example.com
