from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from services.eating_behavior_analyzer import EatingBehaviorAnalyzer
from models import db, User, MealEntry, WeatherData, SocialContext
from utils.auth import require_auth
from utils.validators import validate_date_range

analysis_bp = Blueprint('analysis', __name__)
analyzer = EatingBehaviorAnalyzer()

@analysis_bp.route('/nutrient-analysis', methods=['GET'])
@require_auth
def get_nutrient_analysis():
    """Récupère l'analyse nutritionnelle pour une période donnée"""
    try:
        start_date, end_date = validate_date_range(request.args)
        user_id = request.user.id

        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            MealEntry.date.between(start_date, end_date)
        ).all()

        nutrient_data = {
            entry.date.date(): {
                'nutrients': entry.nutrients,
                'quantity': entry.quantity
            } for entry in entries
        }

        analysis = analyzer.analyze_nutrient_optimization(entries, nutrient_data)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@analysis_bp.route('/behavior-analysis', methods=['GET'])
@require_auth
def get_behavior_analysis():
    """Récupère l'analyse comportementale"""
    try:
        start_date, end_date = validate_date_range(request.args)
        user_id = request.user.id

        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            MealEntry.date.between(start_date, end_date)
        ).all()

        analysis = analyzer.analyze_eating_behavior(entries)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@analysis_bp.route('/weather-impact', methods=['GET'])
@require_auth
def get_weather_impact():
    """Analyse l'impact de la météo sur l'alimentation"""
    try:
        start_date, end_date = validate_date_range(request.args)
        user_id = request.user.id

        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            MealEntry.date.between(start_date, end_date)
        ).all()

        weather_data = WeatherData.query.filter(
            WeatherData.date.between(start_date, end_date)
        ).all()

        weather_dict = {
            data.date.date(): {
                'temperature': data.temperature,
                'humidity': data.humidity,
                'conditions': data.conditions
            } for data in weather_data
        }

        analysis = analyzer.analyze_weather_impact(entries, weather_dict)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@analysis_bp.route('/circadian-analysis', methods=['GET'])
@require_auth
def get_circadian_analysis():
    """Analyse du rythme circadien"""
    try:
        user_id = request.user.id
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            MealEntry.date.between(start_date, end_date)
        ).all()

        analysis = analyzer.analyze_circadian_rhythm(entries, days)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@analysis_bp.route('/seasonal-trends', methods=['GET'])
@require_auth
def get_seasonal_trends():
    """Analyse des tendances saisonnières"""
    try:
        user_id = request.user.id
        year = int(request.args.get('year', datetime.now().year))
        
        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            db.extract('year', MealEntry.date) == year
        ).all()

        seasonal_data = {
            entry.date.date(): {
                'season': get_season(entry.date),
                'temperature': entry.weather_data.temperature if entry.weather_data else None
            } for entry in entries
        }

        analysis = analyzer.analyze_seasonal_adaptations(entries, seasonal_data)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@analysis_bp.route('/social-dining', methods=['GET'])
@require_auth
def get_social_dining_analysis():
    """Analyse des repas sociaux"""
    try:
        start_date, end_date = validate_date_range(request.args)
        user_id = request.user.id

        entries = MealEntry.query.filter(
            MealEntry.user_id == user_id,
            MealEntry.date.between(start_date, end_date)
        ).all()

        social_contexts = SocialContext.query.filter(
            SocialContext.user_id == user_id,
            SocialContext.date.between(start_date, end_date)
        ).all()

        social_data = {
            context.date.date(): {
                'context_type': context.context_type,
                'group_size': context.group_size,
                'duration': context.duration,
                'location': context.location
            } for context in social_contexts
        }

        analysis = analyzer.analyze_social_dining(entries, social_data)
        return jsonify(analysis), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

def get_season(date):
    """Détermine la saison pour une date donnée"""
    month = date.month
    if month in (12, 1, 2):
        return 'hiver'
    elif month in (3, 4, 5):
        return 'printemps'
    elif month in (6, 7, 8):
        return 'été'
    else:
        return 'automne'
