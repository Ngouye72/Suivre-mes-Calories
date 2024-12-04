import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Métriques personnalisées
const mealCreationSuccess = new Rate('meal_creation_success');
const mealCreationDuration = new Trend('meal_creation_duration');
const goalUpdateSuccess = new Rate('goal_update_success');
const searchLatency = new Trend('food_search_latency');
const mlPredictionLatency = new Trend('ml_prediction_latency');

// Configuration des seuils
export const options = {
    scenarios: {
        nutrition_load: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 100 },  // Montée progressive
                { duration: '5m', target: 100 },  // Charge soutenue
                { duration: '2m', target: 200 },  // Pic de charge
                { duration: '1m', target: 0 }     // Retour au calme
            ]
        }
    },
    thresholds: {
        'meal_creation_success': ['rate>0.95'],
        'meal_creation_duration': ['p95<2000'],
        'goal_update_success': ['rate>0.98'],
        'food_search_latency': ['p95<1000'],
        'ml_prediction_latency': ['p95<500'],
        'http_req_duration': ['p95<2000'],
        'http_req_failed': ['rate<0.01']
    }
};

// Données de test
const meals = [
    { name: 'Petit-déjeuner équilibré', calories: 500, protein: 20, carbs: 60, fat: 15 },
    { name: 'Déjeuner protéiné', calories: 700, protein: 40, carbs: 50, fat: 20 },
    { name: 'Dîner léger', calories: 400, protein: 25, carbs: 40, fat: 10 }
];

const searchTerms = ['poulet', 'salade', 'riz', 'poisson', 'légumes'];

export function setup() {
    // Authentification
    const loginRes = http.post('http://nutrition-api/auth/login', {
        username: 'testuser',
        password: 'testpass'
    });
    
    return { token: loginRes.json('token') };
}

export default function(data) {
    const headers = {
        'Authorization': `Bearer ${data.token}`,
        'Content-Type': 'application/json'
    };

    group('Création de repas', function() {
        const meal = meals[randomIntBetween(0, meals.length - 1)];
        const startTime = new Date();
        
        const mealRes = http.post('http://nutrition-api/meals', JSON.stringify(meal), {
            headers: headers
        });
        
        mealCreationDuration.add(new Date() - startTime);
        mealCreationSuccess.add(mealRes.status === 201);
        
        check(mealRes, {
            'création repas réussie': (r) => r.status === 201,
            'ID repas reçu': (r) => r.json('id') !== undefined
        });
    });

    group('Recherche aliments', function() {
        const term = searchTerms[randomIntBetween(0, searchTerms.length - 1)];
        const startTime = new Date();
        
        const searchRes = http.get(`http://nutrition-api/foods/search?q=${term}`, {
            headers: headers
        });
        
        searchLatency.add(new Date() - startTime);
        
        check(searchRes, {
            'recherche réussie': (r) => r.status === 200,
            'résultats reçus': (r) => r.json('results').length > 0
        });
    });

    group('Mise à jour objectifs', function() {
        const goalUpdate = {
            type: 'weight',
            target: randomIntBetween(60, 80),
            deadline: '2024-12-31'
        };
        
        const goalRes = http.put('http://nutrition-api/goals', JSON.stringify(goalUpdate), {
            headers: headers
        });
        
        goalUpdateSuccess.add(goalRes.status === 200);
        
        check(goalRes, {
            'mise à jour objectif réussie': (r) => r.status === 200
        });
    });

    group('Prédictions ML', function() {
        const predictionData = {
            user_id: 'test-user',
            meal_history: meals,
            current_weight: 70,
            target_weight: 65
        };
        
        const startTime = new Date();
        const predictionRes = http.post('http://nutrition-api/ml/predict', JSON.stringify(predictionData), {
            headers: headers
        });
        
        mlPredictionLatency.add(new Date() - startTime);
        
        check(predictionRes, {
            'prédiction réussie': (r) => r.status === 200,
            'recommandations reçues': (r) => r.json('recommendations').length > 0
        });
    });

    sleep(randomIntBetween(1, 5));
}
