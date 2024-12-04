from datetime import datetime, timedelta
from sqlalchemy import func
from models import FoodEntry, Activity, User, db

def get_daily_stats(user_id, date=None):
    if date is None:
        date = datetime.now().date()
    
    # Obtenir les entrées alimentaires du jour
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    
    food_entries = FoodEntry.query.filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date.between(start_date, end_date)
    ).all()
    
    # Calculer les totaux
    daily_totals = {
        'calories': sum(entry.calories for entry in food_entries),
        'proteins': sum(entry.proteins for entry in food_entries if entry.proteins),
        'carbs': sum(entry.carbs for entry in food_entries if entry.carbs),
        'fats': sum(entry.fats for entry in food_entries if entry.fats)
    }
    
    # Obtenir les objectifs de l'utilisateur
    user = User.query.get(user_id)
    target_calories = user.target_calories or 2000  # Valeur par défaut
    
    # Calculer les objectifs de macronutriments (distribution standard)
    target_proteins = (target_calories * 0.3) / 4  # 30% des calories, 4 cal/g
    target_carbs = (target_calories * 0.45) / 4    # 45% des calories, 4 cal/g
    target_fats = (target_calories * 0.25) / 9     # 25% des calories, 9 cal/g
    
    return {
        'daily': daily_totals,
        'target': {
            'calories': target_calories,
            'proteins': round(target_proteins),
            'carbs': round(target_carbs),
            'fats': round(target_fats)
        }
    }

def get_weekly_stats(user_id):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Requête pour obtenir les totaux quotidiens
    daily_totals = db.session.query(
        func.date(FoodEntry.date).label('date'),
        func.sum(FoodEntry.calories).label('calories'),
        func.sum(FoodEntry.proteins).label('proteins'),
        func.sum(FoodEntry.carbs).label('carbs'),
        func.sum(FoodEntry.fats).label('fats')
    ).filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date.between(start_date, end_date)
    ).group_by(
        func.date(FoodEntry.date)
    ).all()
    
    # Initialiser les données pour tous les jours
    stats = {}
    for i in range(7):
        date = (end_date - timedelta(days=i)).date()
        stats[date] = {
            'calories': 0,
            'proteins': 0,
            'carbs': 0,
            'fats': 0
        }
    
    # Remplir avec les données réelles
    for total in daily_totals:
        stats[total.date] = {
            'calories': int(total.calories or 0),
            'proteins': float(total.proteins or 0),
            'carbs': float(total.carbs or 0),
            'fats': float(total.fats or 0)
        }
    
    return stats

def get_monthly_progress(user_id):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Obtenir le poids enregistré
    weight_entries = db.session.query(
        User.weight,
        User.updated_at.label('date')
    ).filter(
        User.id == user_id,
        User.updated_at.between(start_date, end_date)
    ).order_by(User.updated_at).all()
    
    # Calculer les moyennes caloriques hebdomadaires
    weekly_calories = db.session.query(
        func.date_trunc('week', FoodEntry.date).label('week'),
        func.avg(FoodEntry.calories).label('avg_calories')
    ).filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date.between(start_date, end_date)
    ).group_by(
        func.date_trunc('week', FoodEntry.date)
    ).all()
    
    return {
        'weight_progress': [{
            'date': entry.date.strftime('%Y-%m-%d'),
            'weight': float(entry.weight)
        } for entry in weight_entries],
        'calorie_trends': [{
            'week': week.week.strftime('%Y-%m-%d'),
            'avg_calories': float(week.avg_calories or 0)
        } for week in weekly_calories]
    }

def get_nutrition_distribution(user_id, date=None):
    if date is None:
        date = datetime.now().date()
    
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    
    # Obtenir la distribution par repas
    meal_distribution = db.session.query(
        FoodEntry.meal_type,
        func.sum(FoodEntry.calories).label('calories'),
        func.sum(FoodEntry.proteins).label('proteins'),
        func.sum(FoodEntry.carbs).label('carbs'),
        func.sum(FoodEntry.fats).label('fats')
    ).filter(
        FoodEntry.user_id == user_id,
        FoodEntry.date.between(start_date, end_date)
    ).group_by(FoodEntry.meal_type).all()
    
    return [{
        'meal_type': meal.meal_type,
        'calories': int(meal.calories or 0),
        'proteins': float(meal.proteins or 0),
        'carbs': float(meal.carbs or 0),
        'fats': float(meal.fats or 0)
    } for meal in meal_distribution]
