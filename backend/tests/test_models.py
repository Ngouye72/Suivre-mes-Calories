import pytest
from datetime import datetime, timedelta
from backend.models import (
    User, UserProfile, MealEntry, WeatherData,
    SocialContext, Notification, NotificationPreference
)
from backend.database import db

@pytest.fixture
def user(db_session):
    """Fixture pour créer un utilisateur de test"""
    user = User(
        email='test@example.com',
        username='testuser',
        password='password123'
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def user_profile(db_session, user):
    """Fixture pour créer un profil utilisateur"""
    profile = UserProfile(
        user_id=user.id,
        height=175,
        weight=70,
        age=30,
        gender='M',
        activity_level='moderate'
    )
    db_session.add(profile)
    db_session.commit()
    return profile

@pytest.fixture
def meal_entry(db_session, user):
    """Fixture pour créer une entrée de repas"""
    meal = MealEntry(
        user_id=user.id,
        name='Test Meal',
        calories=500,
        protein=20,
        carbs=60,
        fat=15,
        meal_time=datetime.now()
    )
    db_session.add(meal)
    db_session.commit()
    return meal

class TestUser:
    def test_create_user(self, db_session):
        """Test la création d'un utilisateur"""
        user = User(
            email='new@example.com',
            username='newuser',
            password='password123'
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == 'new@example.com'
        assert user.verify_password('password123')

    def test_user_profile_relationship(self, user, user_profile):
        """Test la relation entre User et UserProfile"""
        assert user.profile is not None
        assert user.profile.height == 175
        assert user.profile.weight == 70

    def test_user_meals_relationship(self, user, meal_entry):
        """Test la relation entre User et MealEntry"""
        assert len(user.meals) == 1
        assert user.meals[0].calories == 500

    def test_password_hashing(self, user):
        """Test le hachage du mot de passe"""
        assert user.password != 'password123'
        assert user.verify_password('password123')
        assert not user.verify_password('wrongpassword')

class TestUserProfile:
    def test_create_profile(self, db_session, user):
        """Test la création d'un profil"""
        profile = UserProfile(
            user_id=user.id,
            height=180,
            weight=75,
            age=25,
            gender='F',
            activity_level='high'
        )
        db_session.add(profile)
        db_session.commit()

        assert profile.id is not None
        assert profile.height == 180
        assert profile.user_id == user.id

    def test_calculate_bmi(self, user_profile):
        """Test le calcul du BMI"""
        bmi = user_profile.calculate_bmi()
        expected_bmi = 70 / ((175/100) ** 2)
        assert abs(bmi - expected_bmi) < 0.1

    def test_calculate_daily_calories(self, user_profile):
        """Test le calcul des calories journalières"""
        calories = user_profile.calculate_daily_calories()
        assert calories > 0

class TestMealEntry:
    def test_create_meal(self, db_session, user):
        """Test la création d'un repas"""
        meal = MealEntry(
            user_id=user.id,
            name='Breakfast',
            calories=300,
            protein=15,
            carbs=40,
            fat=10,
            meal_time=datetime.now()
        )
        db_session.add(meal)
        db_session.commit()

        assert meal.id is not None
        assert meal.calories == 300
        assert meal.name == 'Breakfast'

    def test_meal_macros(self, meal_entry):
        """Test les macronutriments du repas"""
        assert meal_entry.protein == 20
        assert meal_entry.carbs == 60
        assert meal_entry.fat == 15

    def test_meal_time_range(self, user, db_session):
        """Test la plage horaire des repas"""
        now = datetime.now()
        
        # Création de repas sur différentes heures
        meals = [
            MealEntry(
                user_id=user.id,
                name=f'Meal {i}',
                calories=300,
                meal_time=now + timedelta(hours=i)
            )
            for i in range(3)
        ]
        
        db_session.add_all(meals)
        db_session.commit()

        # Vérification de la récupération par plage horaire
        start_time = now
        end_time = now + timedelta(hours=2)
        
        found_meals = MealEntry.query.filter(
            MealEntry.user_id == user.id,
            MealEntry.meal_time.between(start_time, end_time)
        ).all()
        
        assert len(found_meals) == 2

class TestWeatherData:
    def test_create_weather_data(self, db_session):
        """Test la création de données météo"""
        weather = WeatherData(
            temperature=25.5,
            humidity=65,
            pressure=1013,
            description='Sunny',
            timestamp=datetime.now()
        )
        db_session.add(weather)
        db_session.commit()

        assert weather.id is not None
        assert weather.temperature == 25.5
        assert weather.description == 'Sunny'

class TestSocialContext:
    def test_create_social_context(self, db_session, meal_entry):
        """Test la création d'un contexte social"""
        context = SocialContext(
            meal_id=meal_entry.id,
            location='Restaurant',
            companions=2,
            mood='Happy',
            occasion='Birthday'
        )
        db_session.add(context)
        db_session.commit()

        assert context.id is not None
        assert context.location == 'Restaurant'
        assert context.meal_id == meal_entry.id

class TestNotification:
    def test_create_notification(self, db_session, user):
        """Test la création d'une notification"""
        notif = Notification(
            user_id=user.id,
            title='Test Notification',
            message='This is a test',
            type='reminder',
            priority='high'
        )
        db_session.add(notif)
        db_session.commit()

        assert notif.id is not None
        assert notif.title == 'Test Notification'
        assert notif.user_id == user.id

    def test_notification_preference(self, db_session, user):
        """Test les préférences de notification"""
        pref = NotificationPreference(
            user_id=user.id,
            type='reminder',
            email_enabled=True,
            push_enabled=False,
            quiet_hours_start=20,
            quiet_hours_end=8
        )
        db_session.add(pref)
        db_session.commit()

        assert pref.id is not None
        assert pref.email_enabled
        assert not pref.push_enabled
