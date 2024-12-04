from datetime import datetime
from models import db, User, Notification, NotificationPreference
from services.notifications.email_sender import EmailSender
from services.notifications.push_sender import PushSender
from services.notifications.sms_sender import SMSSender
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.email_sender = EmailSender()
        self.push_sender = PushSender()
        self.sms_sender = SMSSender()

    def create_notification(self, user_id, title, message, notification_type, priority='normal'):
        """Crée une nouvelle notification"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                created_at=datetime.utcnow(),
                status='pending'
            )
            db.session.add(notification)
            db.session.commit()
            
            # Envoi immédiat pour les notifications prioritaires
            if priority == 'high':
                self.send_notification(notification)
            
            return notification

        except Exception as e:
            logger.error(f"Erreur lors de la création de la notification: {str(e)}")
            db.session.rollback()
            raise

    def send_notification(self, notification):
        """Envoie une notification via les canaux appropriés"""
        try:
            user = User.query.get(notification.user_id)
            if not user:
                raise ValueError("Utilisateur non trouvé")

            preferences = NotificationPreference.query.filter_by(user_id=user.id).first()
            if not preferences:
                preferences = self.create_default_preferences(user.id)

            sent = False
            
            # Email
            if preferences.email_enabled:
                try:
                    self.email_sender.send(
                        to_email=user.email,
                        subject=notification.title,
                        body=notification.message
                    )
                    sent = True
                except Exception as e:
                    logger.error(f"Erreur d'envoi email: {str(e)}")

            # Push
            if preferences.push_enabled:
                try:
                    self.push_sender.send(
                        user_id=user.id,
                        title=notification.title,
                        message=notification.message,
                        data={'notification_id': notification.id}
                    )
                    sent = True
                except Exception as e:
                    logger.error(f"Erreur d'envoi push: {str(e)}")

            # SMS
            if preferences.sms_enabled and notification.priority == 'high':
                try:
                    self.sms_sender.send(
                        phone_number=user.phone_number,
                        message=f"{notification.title}: {notification.message}"
                    )
                    sent = True
                except Exception as e:
                    logger.error(f"Erreur d'envoi SMS: {str(e)}")

            # Mise à jour du statut
            notification.status = 'sent' if sent else 'failed'
            notification.sent_at = datetime.utcnow() if sent else None
            db.session.commit()

            return sent

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification: {str(e)}")
            notification.status = 'failed'
            db.session.commit()
            raise

    def create_default_preferences(self, user_id):
        """Crée des préférences de notification par défaut"""
        preferences = NotificationPreference(
            user_id=user_id,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False,
            quiet_hours_start='22:00',
            quiet_hours_end='07:00',
            frequency='immediate'
        )
        db.session.add(preferences)
        db.session.commit()
        return preferences

    def update_preferences(self, user_id, preferences_data):
        """Met à jour les préférences de notification"""
        try:
            preferences = NotificationPreference.query.filter_by(user_id=user_id).first()
            if not preferences:
                preferences = self.create_default_preferences(user_id)

            for key, value in preferences_data.items():
                if hasattr(preferences, key):
                    setattr(preferences, key, value)

            db.session.commit()
            return preferences

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des préférences: {str(e)}")
            db.session.rollback()
            raise

    def get_user_notifications(self, user_id, status=None, limit=50):
        """Récupère les notifications d'un utilisateur"""
        query = Notification.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
            
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id, user_id):
        """Marque une notification comme lue"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.read_at = datetime.utcnow()
                notification.status = 'read'
                db.session.commit()
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors du marquage de la notification: {str(e)}")
            db.session.rollback()
            raise

    def delete_notification(self, notification_id, user_id):
        """Supprime une notification"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la notification: {str(e)}")
            db.session.rollback()
            raise

    def cleanup_old_notifications(self, days=30):
        """Nettoie les anciennes notifications"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            Notification.query.filter(
                Notification.created_at < cutoff_date,
                Notification.status.in_(['sent', 'read'])
            ).delete()
            db.session.commit()

        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des notifications: {str(e)}")
            db.session.rollback()
            raise
