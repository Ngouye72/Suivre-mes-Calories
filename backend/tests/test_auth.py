import pytest
from flask import json
from models import User, UserProfile

def test_register_success(client):
    """Test l'inscription réussie d'un utilisateur"""
    data = {
        'email': 'new@example.com',
        'password': 'NewPassword123',
        'username': 'newuser',
        'height': 180,
        'weight': 75,
        'age': 25,
        'gender': 'M',
        'activity_level': 'modere'
    }
    
    response = client.post('/auth/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    assert 'token' in response.json
    assert 'user' in response.json
    
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'
    assert user.profile.height == 180

def test_register_duplicate_email(client, test_user):
    """Test l'inscription avec un email déjà utilisé"""
    data = {
        'email': 'test@example.com',
        'password': 'Password123',
        'username': 'anotheruser'
    }
    
    response = client.post('/auth/register',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Email déjà utilisé' in response.json['error']

def test_login_success(client, test_user):
    """Test la connexion réussie"""
    data = {
        'email': 'test@example.com',
        'password': 'TestPassword123'
    }
    
    response = client.post('/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    assert 'token' in response.json
    assert 'user' in response.json

def test_login_invalid_credentials(client):
    """Test la connexion avec des identifiants invalides"""
    data = {
        'email': 'wrong@example.com',
        'password': 'WrongPassword'
    }
    
    response = client.post('/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 401
    assert 'error' in response.json

def test_get_profile(client, test_user, auth_headers):
    """Test la récupération du profil utilisateur"""
    response = client.get('/auth/profile',
                         headers=auth_headers)
    
    assert response.status_code == 200
    assert 'user' in response.json
    assert 'profile' in response.json
    assert response.json['user']['email'] == test_user.email

def test_update_profile(client, test_user, auth_headers):
    """Test la mise à jour du profil utilisateur"""
    data = {
        'height': 185,
        'weight': 80,
        'activity_level': 'actif'
    }
    
    response = client.put('/auth/profile',
                         headers=auth_headers,
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 200
    assert 'profile' in response.json
    assert response.json['profile']['height'] == 185
    assert response.json['profile']['weight'] == 80
    assert response.json['profile']['activity_level'] == 'actif'

def test_update_profile_invalid_data(client, auth_headers):
    """Test la mise à jour du profil avec des données invalides"""
    data = {
        'height': -50,  # Hauteur invalide
        'weight': 1000  # Poids invalide
    }
    
    response = client.put('/auth/profile',
                         headers=auth_headers,
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_password_reset_request(client, test_user):
    """Test la demande de réinitialisation du mot de passe"""
    data = {
        'email': test_user.email
    }
    
    response = client.post('/auth/password/reset-request',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    assert 'message' in response.json

def test_unauthorized_access(client):
    """Test l'accès non autorisé aux routes protégées"""
    response = client.get('/auth/profile')
    assert response.status_code == 401
    assert 'error' in response.json

def test_invalid_token(client):
    """Test l'accès avec un token invalide"""
    headers = {'Authorization': 'Bearer invalid-token'}
    response = client.get('/auth/profile', headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
