import pytest
from datetime import datetime, timedelta
from backend.app import create_app
from backend.models import User, MealEntry, UserProfile
import json

@pytest.fixture
def app():
    """Fixture pour créer l'application Flask"""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Fixture pour créer un client de test"""
    return app.test_client()

@pytest.fixture
def auth_headers(client, user):
    """Fixture pour obtenir les en-têtes d'authentification"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

class TestAuthRoutes:
    def test_register(self, client):
        """Test l'enregistrement d'un utilisateur"""
        response = client.post('/api/auth/register', json={
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        assert response.json['message'] == 'User registered successfully'

    def test_login(self, client, user):
        """Test la connexion"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json

    def test_logout(self, client, auth_headers):
        """Test la déconnexion"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'Logged out successfully'

class TestUserRoutes:
    def test_get_profile(self, client, auth_headers, user_profile):
        """Test la récupération du profil"""
        response = client.get('/api/user/profile', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['height'] == 175
        assert response.json['weight'] == 70

    def test_update_profile(self, client, auth_headers):
        """Test la mise à jour du profil"""
        response = client.put('/api/user/profile', 
            headers=auth_headers,
            json={
                'height': 180,
                'weight': 75,
                'age': 31
            }
        )
        
        assert response.status_code == 200
        assert response.json['height'] == 180
        assert response.json['weight'] == 75

class TestMealRoutes:
    def test_add_meal(self, client, auth_headers):
        """Test l'ajout d'un repas"""
        response = client.post('/api/meals', 
            headers=auth_headers,
            json={
                'name': 'Test Meal',
                'calories': 500,
                'protein': 20,
                'carbs': 60,
                'fat': 15,
                'meal_time': datetime.now().isoformat()
            }
        )
        
        assert response.status_code == 201
        assert response.json['name'] == 'Test Meal'
        assert response.json['calories'] == 500

    def test_get_meals(self, client, auth_headers, meal_entry):
        """Test la récupération des repas"""
        response = client.get('/api/meals', headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['calories'] == 500

    def test_get_meal_by_id(self, client, auth_headers, meal_entry):
        """Test la récupération d'un repas par ID"""
        response = client.get(f'/api/meals/{meal_entry.id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['id'] == meal_entry.id
        assert response.json['name'] == 'Test Meal'

class TestAnalysisRoutes:
    def test_nutrient_analysis(self, client, auth_headers, meal_entry):
        """Test l'analyse nutritionnelle"""
        response = client.get('/api/analysis/nutrients', 
            headers=auth_headers,
            query_string={
                'start_date': (datetime.now() - timedelta(days=7)).isoformat(),
                'end_date': datetime.now().isoformat()
            }
        )
        
        assert response.status_code == 200
        assert 'total_calories' in response.json
        assert 'macros' in response.json

    def test_behavior_analysis(self, client, auth_headers, meal_entry):
        """Test l'analyse comportementale"""
        response = client.get('/api/analysis/behavior', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'meal_patterns' in response.json
        assert 'eating_habits' in response.json

class TestNotificationRoutes:
    def test_get_notifications(self, client, auth_headers):
        """Test la récupération des notifications"""
        response = client.get('/api/notifications', headers=auth_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_update_notification_preferences(self, client, auth_headers):
        """Test la mise à jour des préférences de notification"""
        response = client.put('/api/notifications/preferences',
            headers=auth_headers,
            json={
                'email_enabled': True,
                'push_enabled': False,
                'quiet_hours_start': 22,
                'quiet_hours_end': 7
            }
        )
        
        assert response.status_code == 200
        assert response.json['email_enabled'] is True
        assert response.json['push_enabled'] is False

class TestSyncRoutes:
    def test_sync_data(self, client, auth_headers):
        """Test la synchronisation des données"""
        response = client.post('/api/sync',
            headers=auth_headers,
            json={
                'last_sync': datetime.now().isoformat(),
                'changes': []
            }
        )
        
        assert response.status_code == 200
        assert 'sync_token' in response.json

    def test_sync_status(self, client, auth_headers):
        """Test le statut de synchronisation"""
        response = client.get('/api/sync/status', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'last_sync' in response.json
        assert 'status' in response.json
