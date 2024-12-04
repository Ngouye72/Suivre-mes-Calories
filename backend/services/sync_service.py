from datetime import datetime, timedelta
from models import db, MealEntry, WeatherData, SocialContext, SyncLog
from sqlalchemy import and_, or_
import json
import hashlib

class SyncService:
    def __init__(self):
        self.batch_size = 100
        self.sync_window = timedelta(days=30)  # Synchronise les 30 derniers jours par défaut

    def generate_hash(self, data):
        """Génère un hash pour les données"""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def get_changes_since(self, user_id, last_sync):
        """Récupère les changements depuis la dernière synchronisation"""
        changes = {
            'meals': [],
            'weather': [],
            'social': [],
            'deleted': []
        }

        # Récupération des repas modifiés
        meals = MealEntry.query.filter(
            and_(
                MealEntry.user_id == user_id,
                MealEntry.updated_at >= last_sync
            )
        ).all()

        for meal in meals:
            changes['meals'].append(meal.to_dict())

        # Récupération des données météo
        weather = WeatherData.query.filter(
            WeatherData.date >= last_sync
        ).all()

        for w in weather:
            changes['weather'].append(w.to_dict())

        # Récupération des contextes sociaux
        social = SocialContext.query.filter(
            and_(
                SocialContext.user_id == user_id,
                SocialContext.updated_at >= last_sync
            )
        ).all()

        for s in social:
            changes['social'].append(s.to_dict())

        # Récupération des éléments supprimés
        deleted = SyncLog.query.filter(
            and_(
                SyncLog.user_id == user_id,
                SyncLog.action == 'delete',
                SyncLog.timestamp >= last_sync
            )
        ).all()

        for d in deleted:
            changes['deleted'].append({
                'type': d.entity_type,
                'id': d.entity_id,
                'timestamp': d.timestamp.isoformat()
            })

        return changes

    def apply_changes(self, user_id, changes):
        """Applique les changements reçus du client"""
        try:
            # Traitement des repas
            for meal_data in changes.get('meals', []):
                meal_id = meal_data.get('id')
                meal = MealEntry.query.get(meal_id) if meal_id else None

                if meal:
                    # Mise à jour du repas existant
                    if meal.hash != self.generate_hash(meal_data):
                        for key, value in meal_data.items():
                            if key != 'id':
                                setattr(meal, key, value)
                        meal.updated_at = datetime.utcnow()
                else:
                    # Création d'un nouveau repas
                    meal = MealEntry(**meal_data)
                    meal.user_id = user_id
                    db.session.add(meal)

            # Traitement des contextes sociaux
            for social_data in changes.get('social', []):
                social_id = social_data.get('id')
                social = SocialContext.query.get(social_id) if social_id else None

                if social:
                    if social.hash != self.generate_hash(social_data):
                        for key, value in social_data.items():
                            if key != 'id':
                                setattr(social, key, value)
                        social.updated_at = datetime.utcnow()
                else:
                    social = SocialContext(**social_data)
                    social.user_id = user_id
                    db.session.add(social)

            # Traitement des suppressions
            for delete_data in changes.get('deleted', []):
                entity_type = delete_data['type']
                entity_id = delete_data['id']

                if entity_type == 'meal':
                    MealEntry.query.filter_by(id=entity_id, user_id=user_id).delete()
                elif entity_type == 'social':
                    SocialContext.query.filter_by(id=entity_id, user_id=user_id).delete()

                # Enregistrement de la suppression
                log = SyncLog(
                    user_id=user_id,
                    action='delete',
                    entity_type=entity_type,
                    entity_id=entity_id
                )
                db.session.add(log)

            db.session.commit()
            return True, "Synchronisation réussie"

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def handle_conflicts(self, server_data, client_data):
        """Gère les conflits de synchronisation"""
        resolved_data = {}

        for key in server_data:
            if key in client_data:
                # Si les deux versions ont le même timestamp, on garde la version serveur
                if server_data[key]['updated_at'] >= client_data[key]['updated_at']:
                    resolved_data[key] = server_data[key]
                else:
                    resolved_data[key] = client_data[key]
            else:
                resolved_data[key] = server_data[key]

        return resolved_data

    def cleanup_old_sync_logs(self, days=30):
        """Nettoie les anciens logs de synchronisation"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        SyncLog.query.filter(SyncLog.timestamp < cutoff_date).delete()
        db.session.commit()

    def verify_data_integrity(self, user_id):
        """Vérifie l'intégrité des données"""
        integrity_issues = []

        # Vérification des repas
        meals = MealEntry.query.filter_by(user_id=user_id).all()
        for meal in meals:
            current_hash = self.generate_hash(meal.to_dict())
            if meal.hash != current_hash:
                integrity_issues.append({
                    'type': 'meal',
                    'id': meal.id,
                    'issue': 'hash_mismatch'
                })

        # Vérification des contextes sociaux
        social_contexts = SocialContext.query.filter_by(user_id=user_id).all()
        for context in social_contexts:
            current_hash = self.generate_hash(context.to_dict())
            if context.hash != current_hash:
                integrity_issues.append({
                    'type': 'social',
                    'id': context.id,
                    'issue': 'hash_mismatch'
                })

        return integrity_issues
