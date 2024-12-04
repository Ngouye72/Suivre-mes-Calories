import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Métriques personnalisées
const mealCreationRate = new Rate('meal_creation_success');
const weightLogRate = new Rate('weight_log_success');
const nutritionCalcTrend = new Trend('nutrition_calculation_duration');

// Configuration des scénarios
export const options = {
  scenarios: {
    // Scénario de charge normale
    normal_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 50 },  // Montée progressive
        { duration: '10m', target: 50 }, // Maintien
        { duration: '5m', target: 0 }    // Descente
      ],
      gracefulRampDown: '2m',
    },
    // Scénario de pic d'utilisation
    peak_hours: {
      executor: 'ramping-vus',
      startTime: '30m',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },  // Montée rapide
        { duration: '5m', target: 100 },  // Maintien du pic
        { duration: '2m', target: 0 }     // Descente rapide
      ],
    },
    // Scénario de stress test
    stress_test: {
      executor: 'ramping-vus',
      startTime: '45m',
      startVUs: 0,
      stages: [
        { duration: '10m', target: 200 }, // Montée intensive
        { duration: '5m', target: 200 },  // Maintien
        { duration: '5m', target: 0 }     // Descente
      ],
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% des requêtes sous 500ms
    http_req_failed: ['rate<0.01'],   // Moins de 1% d'erreurs
    'meal_creation_success': ['rate>0.95'], // 95% de succès création repas
    'weight_log_success': ['rate>0.95'],    // 95% de succès log poids
  }
};

// Données de test
const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];
const foodItems = [
  { name: 'Banana', calories: 105 },
  { name: 'Chicken Breast', calories: 165 },
  { name: 'Rice', calories: 130 },
  { name: 'Salad', calories: 20 },
  { name: 'Yogurt', calories: 150 }
];

// Fonction principale de test
export default function() {
  const baseUrl = 'https://nutrition-app.com/api';
  
  // Authentification
  const loginRes = http.post(`${baseUrl}/auth/login`, {
    username: `user_${__VU}@example.com`,
    password: 'testPassword123'
  });
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });
  
  const token = loginRes.json('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  // Simulation du comportement utilisateur
  group('User Journey', () => {
    // 1. Consultation du tableau de bord
    const dashboardRes = http.get(`${baseUrl}/dashboard`, { headers });
    check(dashboardRes, {
      'dashboard loaded': (r) => r.status === 200,
    });
    
    sleep(randomIntBetween(1, 3));
    
    // 2. Création d'un repas
    const meal = {
      type: mealTypes[randomIntBetween(0, mealTypes.length - 1)],
      items: Array(randomIntBetween(1, 3)).fill().map(() => 
        foodItems[randomIntBetween(0, foodItems.length - 1)]
      ),
      timestamp: new Date().toISOString()
    };
    
    const startTime = new Date();
    const mealRes = http.post(`${baseUrl}/meals`, JSON.stringify(meal), { headers });
    const duration = new Date() - startTime;
    
    nutritionCalcTrend.add(duration);
    mealCreationRate.add(mealRes.status === 201);
    
    check(mealRes, {
      'meal created': (r) => r.status === 201,
    });
    
    sleep(randomIntBetween(2, 5));
    
    // 3. Enregistrement du poids
    const weight = {
      value: randomIntBetween(50, 100),
      unit: 'kg',
      timestamp: new Date().toISOString()
    };
    
    const weightRes = http.post(`${baseUrl}/weight-logs`, JSON.stringify(weight), { headers });
    weightLogRate.add(weightRes.status === 201);
    
    check(weightRes, {
      'weight logged': (r) => r.status === 201,
    });
    
    sleep(randomIntBetween(1, 3));
    
    // 4. Consultation des statistiques
    const statsRes = http.get(`${baseUrl}/stats/nutrition`, { headers });
    check(statsRes, {
      'stats loaded': (r) => r.status === 200,
    });
  });
  
  sleep(randomIntBetween(5, 10));
}

// Fonctions utilitaires pour la génération de données
function generateMealData() {
  return {
    type: mealTypes[randomIntBetween(0, mealTypes.length - 1)],
    items: Array(randomIntBetween(1, 5)).fill().map(generateFoodItem),
    notes: `Test meal ${Date.now()}`
  };
}

function generateFoodItem() {
  const item = foodItems[randomIntBetween(0, foodItems.length - 1)];
  return {
    ...item,
    quantity: randomIntBetween(1, 3),
    unit: 'portion'
  };
}

// Configuration des hooks
export function setup() {
  // Création des utilisateurs de test si nécessaire
  const setupRes = http.post('https://nutrition-app.com/api/test/setup', {
    users: 200 // Nombre d'utilisateurs de test
  });
  
  check(setupRes, {
    'test setup completed': (r) => r.status === 200,
  });
  
  return { setupCompleted: true };
}

export function teardown(data) {
  // Nettoyage des données de test
  if (data.setupCompleted) {
    const cleanupRes = http.post('https://nutrition-app.com/api/test/cleanup');
    check(cleanupRes, {
      'test cleanup completed': (r) => r.status === 200,
    });
  }
}
