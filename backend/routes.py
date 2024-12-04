from flask import jsonify, request
from app import app, db
from models import User, FoodEntry, Activity, Food
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import bcrypt
from services.food_service import search_food_by_barcode, search_food_by_name, add_food_to_database
from services.stats_service import (
    get_daily_stats,
    get_weekly_stats,
    get_monthly_progress,
    get_nutrition_distribution
)
import datetime

# Routes d'authentification
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
        
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur créé avec succès'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token}), 200
    
    return jsonify({'error': 'Identifiants invalides'}), 401

# Routes pour le journal alimentaire
@app.route('/api/food-entries', methods=['POST'])
@jwt_required()
def add_food_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    new_entry = FoodEntry(
        user_id=user_id,
        food_name=data['food_name'],
        calories=data['calories'],
        proteins=data.get('proteins'),
        carbs=data.get('carbs'),
        fats=data.get('fats'),
        meal_type=data['meal_type']
    )
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({'message': 'Entrée ajoutée avec succès'}), 201

@app.route('/api/food-entries', methods=['GET'])
@jwt_required()
def get_food_entries():
    user_id = get_jwt_identity()
    entries = FoodEntry.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': entry.id,
        'food_name': entry.food_name,
        'calories': entry.calories,
        'proteins': entry.proteins,
        'carbs': entry.carbs,
        'fats': entry.fats,
        'date': entry.date.isoformat(),
        'meal_type': entry.meal_type
    } for entry in entries]), 200

# Routes pour les activités physiques
@app.route('/api/activities', methods=['POST'])
@jwt_required()
def add_activity():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    new_activity = Activity(
        user_id=user_id,
        activity_name=data['activity_name'],
        calories_burned=data['calories_burned'],
        duration=data['duration']
    )
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify({'message': 'Activité ajoutée avec succès'}), 201

# Routes pour la recherche d'aliments
@app.route('/api/foods/search', methods=['GET'])
def search_foods():
    query = request.args.get('q', '')
    foods = search_food_by_name(query)
    
    return jsonify([{
        'id': food.id,
        'name': food.name,
        'calories': food.calories,
        'proteins': food.proteins,
        'carbs': food.carbs,
        'fats': food.fats,
        'serving_size': food.serving_size,
        'serving_unit': food.serving_unit
    } for food in foods]), 200

@app.route('/api/foods/barcode/<barcode>', methods=['GET'])
def get_food_by_barcode(barcode):
    food = search_food_by_barcode(barcode)
    
    if food:
        return jsonify({
            'id': food.id,
            'name': food.name,
            'calories': food.calories,
            'proteins': food.proteins,
            'carbs': food.carbs,
            'fats': food.fats,
            'serving_size': food.serving_size,
            'serving_unit': food.serving_unit
        }), 200
    
    return jsonify({'error': 'Produit non trouvé'}), 404

@app.route('/api/foods', methods=['POST'])
@jwt_required()
def add_food():
    data = request.get_json()
    food = add_food_to_database(data)
    
    return jsonify({
        'id': food.id,
        'name': food.name,
        'calories': food.calories,
        'proteins': food.proteins,
        'carbs': food.carbs,
        'fats': food.fats,
        'serving_size': food.serving_size,
        'serving_unit': food.serving_unit
    }), 201

@app.route('/api/foods', methods=['GET'])
def search_foods_old():
    query = request.args.get('q', '')
    foods = Food.query.filter(Food.name.ilike(f'%{query}%')).all()
    
    return jsonify([{
        'id': food.id,
        'name': food.name,
        'calories': food.calories,
        'proteins': food.proteins,
        'carbs': food.carbs,
        'fats': food.fats,
        'serving_size': food.serving_size,
        'serving_unit': food.serving_unit
    } for food in foods]), 200

# Routes pour les statistiques
@app.route('/api/stats/daily', methods=['GET'])
@jwt_required()
def daily_stats():
    user_id = get_jwt_identity()
    date = request.args.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    stats = get_daily_stats(user_id, date)
    return jsonify(stats)

@app.route('/api/stats/weekly', methods=['GET'])
@jwt_required()
def weekly_stats():
    user_id = get_jwt_identity()
    stats = get_weekly_stats(user_id)
    return jsonify(stats)

@app.route('/api/stats/monthly', methods=['GET'])
@jwt_required()
def monthly_progress():
    user_id = get_jwt_identity()
    progress = get_monthly_progress(user_id)
    return jsonify(progress)

@app.route('/api/stats/nutrition-distribution', methods=['GET'])
@jwt_required()
def nutrition_distribution():
    user_id = get_jwt_identity()
    date = request.args.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    distribution = get_nutrition_distribution(user_id, date)
    return jsonify(distribution)
