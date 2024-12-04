import pytest
from flask import json
from datetime import datetime, timedelta
from models import MealEntry, WeatherData, SocialContext

def test_nutrient_analysis(client, test_user, test_meals, auth_headers):
    """Test l'analyse nutritionnelle"""
    params = {
        'start_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end_date': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    response = client.get('/analysis/nutrient-analysis',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'nutrients' in response.json
    assert 'recommendations' in response.json

def test_behavior_analysis(client, test_user, test_meals, auth_headers):
    """Test l'analyse comportementale"""
    params = {
        'start_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end_date': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    response = client.get('/analysis/behavior-analysis',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'patterns' in response.json
    assert 'recommendations' in response.json

def test_weather_impact(client, test_user, test_meals, test_weather, auth_headers):
    """Test l'analyse de l'impact météorologique"""
    params = {
        'start_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end_date': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    response = client.get('/analysis/weather-impact',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'correlations' in response.json
    assert 'impact_factors' in response.json

def test_circadian_analysis(client, test_user, test_meals, auth_headers):
    """Test l'analyse du rythme circadien"""
    params = {
        'days': 30
    }
    
    response = client.get('/analysis/circadian-analysis',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'meal_timing' in response.json
    assert 'patterns' in response.json
    assert 'recommendations' in response.json

def test_seasonal_trends(client, test_user, test_meals, auth_headers):
    """Test l'analyse des tendances saisonnières"""
    params = {
        'year': datetime.utcnow().year
    }
    
    response = client.get('/analysis/seasonal-trends',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'seasonal_patterns' in response.json
    assert 'recommendations' in response.json

def test_social_dining_analysis(client, test_user, test_meals, test_social_contexts, auth_headers):
    """Test l'analyse des repas sociaux"""
    params = {
        'start_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end_date': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    response = client.get('/analysis/social-dining',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'social_patterns' in response.json
    assert 'group_impacts' in response.json
    assert 'recommendations' in response.json

def test_invalid_date_range(client, auth_headers):
    """Test l'analyse avec une plage de dates invalide"""
    params = {
        'start_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'end_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
    }
    
    response = client.get('/analysis/nutrient-analysis',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_missing_data(client, test_user, auth_headers):
    """Test l'analyse sans données"""
    params = {
        'start_date': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end_date': datetime.utcnow().strftime('%Y-%m-%d')
    }
    
    # Suppression de toutes les données existantes
    MealEntry.query.filter_by(user_id=test_user.id).delete()
    
    response = client.get('/analysis/nutrient-analysis',
                         headers=auth_headers,
                         query_string=params)
    
    assert response.status_code == 200
    assert 'message' in response.json
    assert 'Pas assez de données' in response.json['message']

def test_analysis_without_authentication(client):
    """Test l'analyse sans authentification"""
    response = client.get('/analysis/nutrient-analysis')
    
    assert response.status_code == 401
    assert 'error' in response.json
