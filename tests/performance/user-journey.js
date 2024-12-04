import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Métriques parcours utilisateur
const journeySuccess = new Rate('user_journey_success');
const journeyDuration = new Trend('user_journey_duration');
const onboardingSuccess = new Rate('onboarding_success');
const interactionSuccess = new Rate('user_interaction_success');

export const options = {
    scenarios: {
        user_journey: {
            executor: 'ramping-arrival-rate',
            startRate: 0,
            timeUnit: '1s',
            preAllocatedVUs: 50,
            maxVUs: 100,
            stages: [
                { duration: '2m', target: 10 },   // Démarrage progressif
                { duration: '5m', target: 10 },   // Charge normale
                { duration: '2m', target: 20 },   // Pic d'utilisation
                { duration: '1m', target: 0 }     // Retour au calme
            ]
        }
    },
    thresholds: {
        'user_journey_success': ['rate>0.95'],
        'user_journey_duration': ['p95<10000'],
        'onboarding_success': ['rate>0.98'],
        'user_interaction_success': ['rate>0.95'],
        'http_req_duration': ['p95<3000']
    }
};

// Données de test
const userProfiles = [
    {
        height: 175,
        weight: 70,
        age: 30,
        goal: 'weight_loss',
        activity_level: 'moderate'
    },
    {
        height: 165,
        weight: 60,
        age: 25,
        goal: 'muscle_gain',
        activity_level: 'active'
    }
];

export default function() {
    const journeyStartTime = new Date();
    let journeySuccessful = true;

    group('Onboarding', function() {
        const profile = userProfiles[randomIntBetween(0, userProfiles.length - 1)];
        
        // Étape 1: Création compte
        const registerRes = http.post('http://nutrition-api/auth/register', JSON.stringify({
            email: `test${Date.now()}@example.com`,
            password: 'TestPassword123!'
        }));
        
        if (!check(registerRes, {
            'inscription réussie': (r) => r.status === 201
        })) {
            journeySuccessful = false;
            return;
        }

        const token = registerRes.json('token');
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        // Étape 2: Profil utilisateur
        const profileRes = http.post('http://nutrition-api/profile', JSON.stringify(profile), {
            headers: headers
        });

        if (!check(profileRes, {
            'profil créé': (r) => r.status === 201
        })) {
            journeySuccessful = false;
            return;
        }

        // Étape 3: Objectifs initiaux
        const goalsRes = http.post('http://nutrition-api/goals/initial', JSON.stringify({
            type: profile.goal,
            target_weight: profile.weight - 5,
            timeline_weeks: 12
        }), { headers: headers });

        onboardingSuccess.add(goalsRes.status === 201);
    });

    group('Première utilisation', function() {
        // Recherche d'aliments
        const searchRes = http.get('http://nutrition-api/foods/search?q=poulet', {
            headers: headers
        });

        // Ajout premier repas
        const mealRes = http.post('http://nutrition-api/meals', JSON.stringify({
            name: 'Premier repas',
            foods: searchRes.json('results').slice(0, 3),
            type: 'lunch'
        }), { headers: headers });

        // Vérification dashboard
        const dashboardRes = http.get('http://nutrition-api/dashboard', {
            headers: headers
        });

        interactionSuccess.add(
            searchRes.status === 200 &&
            mealRes.status === 201 &&
            dashboardRes.status === 200
        );
    });

    group('Engagement quotidien', function() {
        // Journal alimentaire
        const logRes = http.get('http://nutrition-api/meals/log', {
            headers: headers
        });

        // Statistiques
        const statsRes = http.get('http://nutrition-api/stats/weekly', {
            headers: headers
        });

        // Recommandations
        const recoRes = http.get('http://nutrition-api/recommendations', {
            headers: headers
        });

        check(logRes, { 'journal accessible': (r) => r.status === 200 });
        check(statsRes, { 'stats accessibles': (r) => r.status === 200 });
        check(recoRes, { 'recommandations reçues': (r) => r.status === 200 });
    });

    journeyDuration.add(new Date() - journeyStartTime);
    journeySuccess.add(journeySuccessful);

    sleep(randomIntBetween(1, 3));
}
