import pytest
from flask import json
from datetime import datetime, timedelta
from models import MealEntry, SocialContext, SyncLog
from services.sync_service import SyncService

def test_sync_changes(client, test_user, test_meals, auth_headers):
    """Test la synchronisation des changements"""
    # Préparation des changements client
    client_changes = {
        'meals': [{
            'food_name': 'New Food',
            'quantity': 150,
            'calories': 300,
            'date': datetime.utcnow().isoformat(),
            'nutrients': {
                'protein': 15,
                'carbs': 25,
                'fat': 10
            }
        }],
        'deleted': []
    }
    
    data = {
        'last_sync': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'changes': client_changes
    }
    
    response = client.post('/sync/sync',
                          headers=auth_headers,
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    assert 'success' in response.json
    assert 'server_changes' in response.json
    assert 'sync_timestamp' in response.json

def test_sync_conflict_resolution(client, test_user, test_meals, auth_headers):
    """Test la résolution des conflits de synchronisation"""
    sync_service = SyncService()
    
    # Modification du même repas côté serveur et client
    meal = test_meals[0]
    server_data = {meal.id: {
        'quantity': 200,
        'updated_at': datetime.utcnow()
    }}
    
    client_data = {meal.id: {
        'quantity': 250,
        'updated_at': datetime.utcnow() - timedelta(minutes=5)
    }}
    
    resolved = sync_service.handle_conflicts(server_data, client_data)
    assert resolved[meal.id]['quantity'] == 200  # La version serveur doit gagner

def test_sync_status(client, test_user, auth_headers):
    """Test la vérification du statut de synchronisation"""
    response = client.get('/sync/status',
                         headers=auth_headers)
    
    assert response.status_code == 200
    assert 'last_sync' in response.json
    assert 'integrity_issues' in response.json
    assert 'status' in response.json

def test_data_integrity(client, test_user, test_meals, auth_headers):
    """Test la vérification de l'intégrité des données"""
    sync_service = SyncService()
    
    # Modification manuelle d'un hash pour simuler un problème d'intégrité
    meal = test_meals[0]
    meal.hash = 'invalid_hash'
    
    issues = sync_service.verify_data_integrity(test_user.id)
    assert len(issues) > 0
    assert issues[0]['type'] == 'meal'
    assert issues[0]['id'] == meal.id

def test_repair_data(client, test_user, test_meals, auth_headers):
    """Test la réparation des données"""
    # Création d'un problème d'intégrité
    meal = test_meals[0]
    meal.hash = 'invalid_hash'
    
    response = client.post('/sync/repair',
                          headers=auth_headers)
    
    assert response.status_code == 200
    assert 'message' in response.json
    assert 'repaired_items' in response.json
    
    # Vérification que le problème est résolu
    sync_service = SyncService()
    issues = sync_service.verify_data_integrity(test_user.id)
    assert len(issues) == 0

def test_cleanup_sync_logs(client, test_user, auth_headers):
    """Test le nettoyage des logs de synchronisation"""
    # Création de vieux logs
    old_log = SyncLog(
        user_id=test_user.id,
        action='sync',
        timestamp=datetime.utcnow() - timedelta(days=40)
    )
    
    response = client.post('/sync/cleanup',
                          headers=auth_headers,
                          query_string={'days': 30})
    
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Vérification que les vieux logs sont supprimés
    old_logs = SyncLog.query.filter(
        SyncLog.timestamp < datetime.utcnow() - timedelta(days=30)
    ).all()
    assert len(old_logs) == 0

def test_sync_with_invalid_data(client, auth_headers):
    """Test la synchronisation avec des données invalides"""
    data = {
        'last_sync': 'invalid_date',
        'changes': {}
    }
    
    response = client.post('/sync/sync',
                          headers=auth_headers,
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_sync_without_authentication(client):
    """Test la synchronisation sans authentification"""
    response = client.post('/sync/sync',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 401
    assert 'error' in response.json
