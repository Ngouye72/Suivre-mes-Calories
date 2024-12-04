from twilio.rest import Client
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SMSSender:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)

    def send(self, phone_number, message):
        """Envoie un SMS"""
        try:
            if not self.client:
                raise ValueError("Configuration Twilio manquante")

            if not self._validate_phone_number(phone_number):
                raise ValueError("Numéro de téléphone invalide")

            # Envoi du SMS
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )

            logger.info(f"SMS envoyé avec succès: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du SMS: {str(e)}")
            raise

    def send_batch(self, messages):
        """Envoie des SMS en lot"""
        results = []
        for msg in messages:
            try:
                success = self.send(
                    phone_number=msg['to'],
                    message=msg['message']
                )
                results.append({
                    'to': msg['to'],
                    'success': success
                })
            except Exception as e:
                results.append({
                    'to': msg['to'],
                    'success': False,
                    'error': str(e)
                })
        return results

    def _validate_phone_number(self, phone_number):
        """Valide un numéro de téléphone"""
        import re
        # Format international E.164
        pattern = r'^\+[1-9]\d{1,14}$'
        return re.match(pattern, phone_number) is not None

    def format_phone_number(self, phone_number):
        """Formate un numéro de téléphone au format E.164"""
        # Supprime tous les caractères non numériques
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Ajoute le préfixe international si nécessaire
        if not cleaned.startswith('33'):
            cleaned = '33' + cleaned.lstrip('0')
        
        return f'+{cleaned}'
