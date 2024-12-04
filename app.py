from flask import Flask, render_template, jsonify, request
from backend.goals.personal_goals import PersonalGoals
from backend.tracking.daily_tracker import DailyTracker
from backend.meal_planning.meal_planner import MealPlanner
from backend.visualization.goal_visualizer import GoalVisualizer
from backend.coaching.nutrition_coach import NutritionCoach
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback

# Configuration du logging
if not os.path.exists('logs'):
    os.makedirs('logs')

app = Flask(__name__)

# Configuration du logger
handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=1)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application démarrée')

# Initialisation des composants en mode local
try:
    goals = PersonalGoals()
    tracker = DailyTracker()
    planner = MealPlanner()
    visualizer = GoalVisualizer()
    coach = NutritionCoach()
    app.logger.info('Composants initialisés avec succès')
except Exception as e:
    app.logger.error(f'Erreur lors de l\'initialisation des composants: {str(e)}')
    traceback.print_exc()

@app.route('/')
def home():
    """Page d'accueil"""
    try:
        app.logger.info('Accès à la page d\'accueil')
        return render_template('index.html')  # Changé pour index.html
    except Exception as e:
        app.logger.error(f'Erreur page d\'accueil: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/goals', methods=['POST'])
def calculate_goals():
    """Calcule les objectifs personnalisés"""
    try:
        data = request.json
        app.logger.info(f'Calcul des objectifs pour: {data}')
        goals_data = goals.calculate_goals(
            age=data.get('age', 52),
            sexe=data.get('sexe', 'M'),
            poids=data.get('poids', 80),
            taille=data.get('taille', 179),
            niveau_activite=data.get('niveau_activite', 'actif'),
            objectif=data.get('objectif', 'perte'),
            poids_cible=data.get('poids_cible', 78),
            delai_semaines=data.get('delai_semaines', 6)
        )
        return jsonify(goals_data)
    except Exception as e:
        app.logger.error(f'Erreur calcul objectifs: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/meals/daily', methods=['GET'])
def get_daily_plan():
    """Génère un plan de repas journalier"""
    try:
        app.logger.info('Génération du plan journalier')
        daily_plan = planner.generate_daily_plan()
        return jsonify(daily_plan)
    except Exception as e:
        app.logger.error(f'Erreur génération plan repas: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/tracking/log-meal', methods=['POST'])
def log_meal():
    """Enregistre un repas"""
    try:
        data = request.json
        app.logger.info(f'Enregistrement du repas: {data}')
        progress = tracker.log_meal(
            meal_type=data.get('meal_type', 'dejeuner'),
            calories=data.get('calories', 0),
            proteines=data.get('proteines', 0),
            glucides=data.get('glucides', 0),
            lipides=data.get('lipides', 0),
            aliments=data.get('aliments', [])
        )
        return jsonify(progress)
    except Exception as e:
        app.logger.error(f'Erreur enregistrement repas: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/tracking/log-water', methods=['POST'])
def log_water():
    """Enregistre la consommation d'eau"""
    try:
        data = request.json
        app.logger.info(f'Enregistrement eau: {data}')
        progress = tracker.log_water(quantity_ml=data.get('quantity_ml', 0))
        return jsonify(progress)
    except Exception as e:
        app.logger.error(f'Erreur enregistrement eau: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/tracking/log-exercise', methods=['POST'])
def log_exercise():
    """Enregistre une activité physique"""
    try:
        data = request.json
        app.logger.info(f'Enregistrement exercice: {data}')
        progress = tracker.log_exercise(
            activity=data.get('activity', ''),
            duration=data.get('duration', 0),
            intensity=data.get('intensity', 'modérée'),
            calories_burned=data.get('calories_burned', 0)
        )
        return jsonify(progress)
    except Exception as e:
        app.logger.error(f'Erreur enregistrement exercice: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/tracking/daily-summary', methods=['GET'])
def get_daily_summary():
    """Obtient le résumé journalier"""
    try:
        app.logger.info('Récupération du résumé journalier')
        summary = tracker.get_daily_summary()
        return jsonify(summary)
    except Exception as e:
        app.logger.error(f'Erreur génération résumé: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/visualization/dashboard', methods=['GET'])
def get_dashboard():
    """Génère le tableau de bord"""
    try:
        app.logger.info('Génération du tableau de bord')
        dashboard = visualizer.create_dashboard(
            poids_initial=80,
            poids_cible=78,
            delai_semaines=6,
            calories=2650,
            proteines=230,
            glucides=265,
            lipides=75,
            hydratation=3600
        )
        return jsonify(dashboard)
    except Exception as e:
        app.logger.error(f'Erreur génération dashboard: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/api/coach/guidance', methods=['GET'])
def get_guidance():
    """Obtient les conseils du coach"""
    try:
        app.logger.info('Récupération des conseils')
        user_data = {
            'calories': 2000,
            'proteins': 150,
            'carbs': 200,
            'fats': 60,
            'water': 2500
        }
        guidance = coach.get_daily_guidance(user_data)
        return jsonify(guidance)
    except Exception as e:
        app.logger.error(f'Erreur génération conseils: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page non trouvée: {request.url}')
    return jsonify({'error': 'Page non trouvée'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Erreur serveur: {error}')
    return jsonify({'error': 'Erreur serveur interne'}), 500

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
