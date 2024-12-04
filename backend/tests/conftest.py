import pytest
from flask import Flask
from models import db, User, UserProfile, MealEntry, WeatherData, SocialContext
from datetime import datetime, timedelta
import os

@pytest.fixture
def app():
    """Crée une instance de l'application Flask pour les tests"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Client de test pour faire des requêtes"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Crée un utilisateur de test"""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='testuser',
            password='TestPassword123'
        )
        profile = UserProfile(
            height=175,
            weight=70,
            age=30,
            gender='M',
            activity_level='modere'
        )
        user.profile = profile
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(test_user, app):
    """Génère les headers d'authentification"""
    from utils.auth import generate_token
    token = generate_token(test_user.id)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_meals(app, test_user):
    """Crée des repas de test"""
    with app.app_context():
        meals = []
        for i in range(3):
            meal = MealEntry(
                user_id=test_user.id,
                food_name=f'Test Food {i}',
                quantity=100 + i*50,
                calories=200 + i*100,
                date=datetime.utcnow() - timedelta(days=i),
                nutrients={
                    'protein': 10 + i,
                    'carbs': 20 + i,
                    'fat': 5 + i
                }
            )
            meals.append(meal)
            db.session.add(meal)
        db.session.commit()
        return meals

@pytest.fixture
def test_weather(app):
    """Crée des données météo de test"""
    with app.app_context():
        weather_data = []
        for i in range(3):
            weather = WeatherData(
                temperature=20 + i,
                humidity=60 + i,
                conditions='sunny' if i % 2 == 0 else 'cloudy',
                date=datetime.utcnow() - timedelta(days=i)
            )
            weather_data.append(weather)
            db.session.add(weather)
        db.session.commit()
        return weather_data

@pytest.fixture
def test_social_contexts(app, test_user):
    """Crée des contextes sociaux de test"""
    with app.app_context():
        contexts = []
        for i in range(3):
            context = SocialContext(
                user_id=test_user.id,
                context_type=['seul', 'famille', 'amis'][i],
                group_size=1 + i,
                duration=30 + i*15,
                date=datetime.utcnow() - timedelta(days=i)
            )
            contexts.append(context)
            db.session.add(context)
        db.session.commit()
        return contexts
