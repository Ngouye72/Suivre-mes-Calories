from firebase_admin import messaging, credentials, initialize_app
import os
import json
import logging
from models import db, User, DeviceToken

logger = logging.getLogger(__name__)

class PushSender:
    def __init__(self):
        self._initialize_firebase()
        
    def _initialize_firebase(self):
        """Initialise Firebase Admin SDK"""
        try:
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                initialize_app(cred)
            else:
                logger.warning("Chemin des credentials Firebase non trouvé")
        except Exception as e:
            logger.error(f"Erreur d'initialisation Firebase: {str(e)}")

    def send(self, user_id, title, message, data=None):
        """Envoie une notification push"""
        try:
            # Récupération des tokens de l'utilisateur
            device_tokens = DeviceToken.query.filter_by(
                user_id=user_id,
                active=True
            ).all()

            if not device_tokens:
                logger.info(f"Aucun token trouvé pour l'utilisateur {user_id}")
                return False

            # Construction du message
            push_message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message
                ),
                data=data or {},
                tokens=[token.token for token in device_tokens]
            )

            # Envoi de la notification
            response = messaging.send_multicast(push_message)
            
            # Gestion des résultats
            self._handle_send_response(response, device_tokens)
            
            return response.success_count > 0

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification push: {str(e)}")
            raise

    def _handle_send_response(self, response, device_tokens):
        """Gère la réponse de l'envoi des notifications"""
        for idx, result in enumerate(response.responses):
            token = device_tokens[idx]
            
            if not result.success:
                if self._is_token_invalid(result.exception):
                    # Désactivation du token invalide
                    token.active = False
                    db.session.add(token)
                
                logger.error(f"Échec d'envoi pour le token {token.token}: {result.exception}")
            
        db.session.commit()

    def _is_token_invalid(self, exception):
        """Vérifie si l'erreur indique un token invalide"""
        if isinstance(exception, messaging.UnregisteredError):
            return True
        if isinstance(exception, messaging.InvalidArgumentError):
            return True
        return False

    def register_device(self, user_id, token, device_info=None):
        """Enregistre un nouveau token d'appareil"""
        try:
            existing_token = DeviceToken.query.filter_by(
                token=token
            ).first()

            if existing_token:
                # Mise à jour du token existant
                existing_token.user_id = user_id
                existing_token.active = True
                existing_token.device_info = device_info
                existing_token.updated_at = datetime.utcnow()
            else:
                # Création d'un nouveau token
                new_token = DeviceToken(
                    user_id=user_id,
                    token=token,
                    device_info=device_info,
                    active=True
                )
                db.session.add(new_token)

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du token: {str(e)}")
            db.session.rollback()
            raise

    def unregister_device(self, token):
        """Désactive un token d'appareil"""
        try:
            device_token = DeviceToken.query.filter_by(token=token).first()
            if device_token:
                device_token.active = False
                device_token.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la désactivation du token: {str(e)}")
            db.session.rollback()
            raise

    def send_topic_message(self, topic, title, message, data=None):
        """Envoie une notification à un topic"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Message envoyé au topic {topic}: {response}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi au topic: {str(e)}")
            raise

    def subscribe_to_topic(self, tokens, topic):
        """Abonne des tokens à un topic"""
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"Abonnement au topic {topic}: {response.success_count} succès, {response.failure_count} échecs")
            return response.success_count > 0

        except Exception as e:
            logger.error(f"Erreur lors de l'abonnement au topic: {str(e)}")
            raise

    def unsubscribe_from_topic(self, tokens, topic):
        """Désabonne des tokens d'un topic"""
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"Désabonnement du topic {topic}: {response.success_count} succès, {response.failure_count} échecs")
            return response.success_count > 0

        except Exception as e:
            logger.error(f"Erreur lors du désabonnement du topic: {str(e)}")
            raise
