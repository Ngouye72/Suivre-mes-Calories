from functools import wraps
from flask import request, jsonify
import jwt
from models import User
from datetime import datetime, timedelta
import os

def generate_token(user_id):
    """Génère un token JWT pour l'utilisateur"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
        algorithm='HS256'
    )

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Vérification de la présence du token dans les headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Token invalide'}), 401

        if not token:
            return jsonify({'error': 'Token manquant'}), 401

        try:
            # Décodage du token
            data = jwt.decode(
                token,
                os.getenv('JWT_SECRET_KEY', 'your-secret-key'),
                algorithms=['HS256']
            )
            
            # Récupération de l'utilisateur
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 401

            # Ajout de l'utilisateur à la requête
            request.user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401

        return f(*args, **kwargs)

    return decorated

def check_role(roles):
    """Décorateur pour vérifier les rôles de l'utilisateur"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.user:
                return jsonify({'error': 'Non autorisé'}), 401

            if request.user.role not in roles:
                return jsonify({'error': 'Permission insuffisante'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator

def hash_password(password):
    """Hash le mot de passe de l'utilisateur"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def check_password(user, password):
    """Vérifie le mot de passe de l'utilisateur"""
    return check_password_hash(user.password, password)

class AuthError(Exception):
    """Exception personnalisée pour les erreurs d'authentification"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
