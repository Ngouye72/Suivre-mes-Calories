from datetime import datetime, timedelta
import re

def validate_date_range(args):
    """Valide et retourne une plage de dates à partir des arguments de requête"""
    try:
        # Par défaut, on prend les 30 derniers jours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # Si des dates spécifiques sont fournies
        if 'start_date' in args and 'end_date' in args:
            start_date = datetime.strptime(args['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(args['end_date'], '%Y-%m-%d')

            # Vérification de la cohérence des dates
            if start_date > end_date:
                raise ValueError("La date de début doit être antérieure à la date de fin")

            # Limitation de la plage de dates à 1 an maximum
            if (end_date - start_date).days > 365:
                raise ValueError("La plage de dates ne peut pas dépasser un an")

        return start_date, end_date

    except ValueError as e:
        raise ValueError(f"Format de date invalide: {str(e)}")

def validate_meal_entry(data):
    """Valide les données d'entrée d'un repas"""
    required_fields = ['food_id', 'quantity', 'date']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Champ requis manquant: {field}")

    try:
        # Validation de la date
        if isinstance(data['date'], str):
            datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')

        # Validation de la quantité
        quantity = float(data['quantity'])
        if quantity <= 0:
            raise ValueError("La quantité doit être positive")

        # Validation des nutriments si présents
        if 'nutrients' in data:
            if not isinstance(data['nutrients'], dict):
                raise ValueError("Les nutriments doivent être un dictionnaire")
            for nutrient, value in data['nutrients'].items():
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Valeur invalide pour le nutriment {nutrient}")

    except (ValueError, TypeError) as e:
        raise ValueError(f"Données invalides: {str(e)}")

    return True

def validate_weather_data(data):
    """Valide les données météorologiques"""
    required_fields = ['temperature', 'humidity', 'conditions', 'date']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Champ requis manquant: {field}")

    try:
        # Validation de la température
        temp = float(data['temperature'])
        if temp < -50 or temp > 50:
            raise ValueError("Température hors limites (-50°C à 50°C)")

        # Validation de l'humidité
        humidity = float(data['humidity'])
        if humidity < 0 or humidity > 100:
            raise ValueError("L'humidité doit être entre 0 et 100%")

        # Validation de la date
        if isinstance(data['date'], str):
            datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')

    except (ValueError, TypeError) as e:
        raise ValueError(f"Données météo invalides: {str(e)}")

    return True

def validate_social_context(data):
    """Valide les données de contexte social"""
    required_fields = ['context_type', 'date']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Champ requis manquant: {field}")

    valid_contexts = ['seul', 'famille', 'amis', 'collègues', 'restaurant']
    if data['context_type'] not in valid_contexts:
        raise ValueError(f"Type de contexte invalide. Valeurs possibles: {', '.join(valid_contexts)}")

    try:
        # Validation de la date
        if isinstance(data['date'], str):
            datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')

        # Validation de la taille du groupe si présente
        if 'group_size' in data:
            group_size = int(data['group_size'])
            if group_size < 1:
                raise ValueError("La taille du groupe doit être positive")

        # Validation de la durée si présente
        if 'duration' in data:
            duration = int(data['duration'])
            if duration < 0:
                raise ValueError("La durée doit être positive")

    except (ValueError, TypeError) as e:
        raise ValueError(f"Données de contexte social invalides: {str(e)}")

    return True

def validate_registration(data):
    """Valide les données d'inscription"""
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Champ requis manquant: {field}")

    # Validation de l'email
    email = data['email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Format d'email invalide")

    # Validation du mot de passe
    password = data['password']
    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une majuscule")
    if not re.search(r"[a-z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une minuscule")
    if not re.search(r"\d", password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre")

    # Validation des champs optionnels
    if 'height' in data:
        height = float(data['height'])
        if height <= 0 or height > 300:
            raise ValueError("Taille invalide (doit être entre 0 et 300 cm)")

    if 'weight' in data:
        weight = float(data['weight'])
        if weight <= 0 or weight > 500:
            raise ValueError("Poids invalide (doit être entre 0 et 500 kg)")

    if 'age' in data:
        age = int(data['age'])
        if age < 0 or age > 120:
            raise ValueError("Âge invalide (doit être entre 0 et 120 ans)")

    if 'gender' in data and data['gender'] not in ['M', 'F', 'autre']:
        raise ValueError("Genre invalide (doit être 'M', 'F' ou 'autre')")

    if 'activity_level' in data and data['activity_level'] not in ['sedentaire', 'leger', 'modere', 'actif', 'tres_actif']:
        raise ValueError("Niveau d'activité invalide")

    return True

def validate_profile_update(data):
    """Valide les données de mise à jour du profil"""
    if not data:
        raise ValueError("Aucune donnée fournie pour la mise à jour")

    # Validation des champs si présents
    if 'height' in data:
        height = float(data['height'])
        if height <= 0 or height > 300:
            raise ValueError("Taille invalide (doit être entre 0 et 300 cm)")

    if 'weight' in data:
        weight = float(data['weight'])
        if weight <= 0 or weight > 500:
            raise ValueError("Poids invalide (doit être entre 0 et 500 kg)")

    if 'age' in data:
        age = int(data['age'])
        if age < 0 or age > 120:
            raise ValueError("Âge invalide (doit être entre 0 et 120 ans)")

    if 'gender' in data and data['gender'] not in ['M', 'F', 'autre']:
        raise ValueError("Genre invalide (doit être 'M', 'F' ou 'autre')")

    if 'activity_level' in data and data['activity_level'] not in ['sedentaire', 'leger', 'modere', 'actif', 'tres_actif']:
        raise ValueError("Niveau d'activité invalide")

    if 'password' in data:
        password = data['password']
        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r"[a-z]", password):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r"\d", password):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")

    if 'dietary_restrictions' in data and not isinstance(data['dietary_restrictions'], list):
        raise ValueError("Les restrictions alimentaires doivent être une liste")

    if 'health_conditions' in data and not isinstance(data['health_conditions'], list):
        raise ValueError("Les conditions de santé doivent être une liste")

    if 'goals' in data and not isinstance(data['goals'], list):
        raise ValueError("Les objectifs doivent être une liste")

    return True
