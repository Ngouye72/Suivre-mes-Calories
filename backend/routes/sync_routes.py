from flask import Blueprint, request, jsonify
from services.sync_service import SyncService
from utils.auth import require_auth
from models import db, SyncLog
from datetime import datetime

sync_bp = Blueprint('sync', __name__)
sync_service = SyncService()

@sync_bp.route('/sync', methods=['POST'])
@require_auth
def synchronize():
    """Point d'entrée principal pour la synchronisation"""
    try:
        data = request.get_json()
        user_id = request.user.id
        last_sync = data.get('last_sync')
        client_changes = data.get('changes', {})

        if last_sync:
            last_sync = datetime.fromisoformat(last_sync)
        else:
            last_sync = datetime.min

        # Récupération des changements côté serveur
        server_changes = sync_service.get_changes_since(user_id, last_sync)

        # Application des changements du client
        success, message = sync_service.apply_changes(user_id, client_changes)
        if not success:
            return jsonify({
                'error': f"Erreur lors de l'application des changements: {message}"
            }), 400

        # Création d'un log de synchronisation
        sync_log = SyncLog(
            user_id=user_id,
            action='sync',
            details=f"Synchronisation réussie: {len(client_changes)} changements appliqués"
        )
        db.session.add(sync_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'server_changes': server_changes,
            'sync_timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f"Erreur de synchronisation: {str(e)}"
        }), 500

@sync_bp.route('/sync/status', methods=['GET'])
@require_auth
def sync_status():
    """Vérifie le statut de synchronisation"""
    try:
        user_id = request.user.id
        
        # Récupération du dernier log de synchronisation
        last_sync = SyncLog.query.filter_by(
            user_id=user_id,
            action='sync'
        ).order_by(SyncLog.timestamp.desc()).first()

        # Vérification de l'intégrité des données
        integrity_issues = sync_service.verify_data_integrity(user_id)

        return jsonify({
            'last_sync': last_sync.timestamp.isoformat() if last_sync else None,
            'integrity_issues': integrity_issues,
            'status': 'ok' if not integrity_issues else 'issues_detected'
        }), 200

    except Exception as e:
        return jsonify({
            'error': f"Erreur lors de la vérification du statut: {str(e)}"
        }), 500

@sync_bp.route('/sync/repair', methods=['POST'])
@require_auth
def repair_data():
    """Répare les problèmes d'intégrité des données"""
    try:
        user_id = request.user.id
        integrity_issues = sync_service.verify_data_integrity(user_id)

        if not integrity_issues:
            return jsonify({
                'message': "Aucun problème d'intégrité détecté"
            }), 200

        # Réparation des problèmes détectés
        for issue in integrity_issues:
            if issue['type'] == 'meal':
                meal = MealEntry.query.get(issue['id'])
                if meal:
                    meal.hash = sync_service.generate_hash(meal.to_dict())
            elif issue['type'] == 'social':
                context = SocialContext.query.get(issue['id'])
                if context:
                    context.hash = sync_service.generate_hash(context.to_dict())

        db.session.commit()

        return jsonify({
            'message': f"{len(integrity_issues)} problèmes réparés",
            'repaired_items': integrity_issues
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f"Erreur lors de la réparation: {str(e)}"
        }), 500

@sync_bp.route('/sync/cleanup', methods=['POST'])
@require_auth
def cleanup_sync_logs():
    """Nettoie les anciens logs de synchronisation"""
    try:
        days = int(request.args.get('days', 30))
        sync_service.cleanup_old_sync_logs(days)
        
        return jsonify({
            'message': f"Nettoyage des logs plus vieux que {days} jours effectué"
        }), 200

    except Exception as e:
        return jsonify({
            'error': f"Erreur lors du nettoyage: {str(e)}"
        }), 500
