from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserProfile
from utils.validators import validate_registration, validate_profile_update
from utils.auth import generate_token, require_auth, AuthError
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données
        validate_registration(data)
        
        # Vérification si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400

        # Création de l'utilisateur
        new_user = User(
            email=data['email'],
            password=generate_password_hash(data['password'], method='pbkdf2:sha256'),
            username=data.get('username', data['email'].split('@')[0]),
            created_at=datetime.utcnow()
        )
        
        # Création du profil utilisateur
        profile = UserProfile(
            height=data.get('height'),
            weight=data.get('weight'),
            age=data.get('age'),
            gender=data.get('gender'),
            activity_level=data.get('activity_level', 'moderate'),
            dietary_restrictions=data.get('dietary_restrictions', []),
            health_conditions=data.get('health_conditions', []),
            goals=data.get('goals', [])
        )
        
        new_user.profile = profile
        
        # Sauvegarde en base de données
        db.session.add(new_user)
        db.session.commit()
        
        # Génération du token
        token = generate_token(new_user.id)
        
        return jsonify({
            'message': 'Inscription réussie',
            'token': token,
            'user': new_user.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Recherche de l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Génération du token
        token = generate_token(user.id)
        
        # Mise à jour de la dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Récupération du profil utilisateur"""
    try:
        return jsonify({
            'user': request.user.to_dict(),
            'profile': request.user.profile.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Mise à jour du profil utilisateur"""
    try:
        data = request.get_json()
        validate_profile_update(data)
        
        user = request.user
        profile = user.profile

        # Mise à jour des champs du profil
        for field in ['height', 'weight', 'age', 'gender', 'activity_level',
                     'dietary_restrictions', 'health_conditions', 'goals']:
            if field in data:
                setattr(profile, field, data[field])
        
        # Mise à jour des champs utilisateur
        if 'username' in data:
            user.username = data['username']
        
        # Mise à jour du mot de passe si fourni
        if 'password' in data:
            user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': user.to_dict(),
            'profile': profile.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/password/reset-request', methods=['POST'])
def request_password_reset():
    """Demande de réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requis'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé'}), 200
        
        # Génération du token de réinitialisation
        reset_token = generate_token(user.id)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # TODO: Envoyer l'email de réinitialisation
        # send_reset_email(user.email, reset_token)
        
        return jsonify({
            'message': 'Si un compte existe avec cet email, un lien de réinitialisation sera envoyé'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """Réinitialisation du mot de passe"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token et nouveau mot de passe requis'}), 400
        
        # Vérification du token
        try:
            payload = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
                algorithms=['HS256']
            )
            user_id = payload['user_id']
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
        
        user = User.query.get(user_id)
        if not user or user.reset_token != token or \
           user.reset_token_expires < datetime.utcnow():
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        
        # Mise à jour du mot de passe
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur serveur'}), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Déconnexion de l'utilisateur"""
    try:
        # Mise à jour de la dernière déconnexion
        request.user.last_logout = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Déconnexion réussie'}), 200

    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500
