from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Informations personnelles
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    activity_level = db.Column(db.String(20))
    goal = db.Column(db.String(20))  # perte, maintien, prise de poids
    target_calories = db.Column(db.Integer)

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    proteins = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    meal_type = db.Column(db.String(20))  # petit-déjeuner, déjeuner, dîner, collation

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_name = db.Column(db.String(100), nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)  # en minutes
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    calories = db.Column(db.Integer, nullable=False)
    proteins = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    serving_size = db.Column(db.Float)
    serving_unit = db.Column(db.String(20))
