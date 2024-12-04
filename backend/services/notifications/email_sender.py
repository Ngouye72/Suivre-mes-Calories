import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@suivremescalories.com')
        self.templates = self._load_templates()

    def _load_templates(self):
        """Charge les templates d'email"""
        templates = {}
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        # Template de notification générale
        with open(os.path.join(template_dir, 'notification.html'), 'r', encoding='utf-8') as f:
            templates['notification'] = Template(f.read())
        
        # Template de rapport quotidien
        with open(os.path.join(template_dir, 'daily_report.html'), 'r', encoding='utf-8') as f:
            templates['daily_report'] = Template(f.read())
        
        # Template d'alerte
        with open(os.path.join(template_dir, 'alert.html'), 'r', encoding='utf-8') as f:
            templates['alert'] = Template(f.read())
        
        return templates

    def send(self, to_email, subject, body, template_name='notification', template_data=None):
        """Envoie un email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Utilisation du template si spécifié
            if template_name and template_data:
                html_content = self.templates[template_name].render(**template_data)
            else:
                html_content = body

            # Ajout du contenu HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Ajout du contenu texte simple
            text_part = MIMEText(self._html_to_text(html_content), 'plain')
            msg.attach(text_part)

            # Connexion au serveur SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email envoyé avec succès à {to_email}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
            raise

    def send_batch(self, emails):
        """Envoie des emails en lot"""
        results = []
        for email in emails:
            try:
                success = self.send(
                    to_email=email['to'],
                    subject=email['subject'],
                    body=email['body'],
                    template_name=email.get('template_name'),
                    template_data=email.get('template_data')
                )
                results.append({
                    'to': email['to'],
                    'success': success
                })
            except Exception as e:
                results.append({
                    'to': email['to'],
                    'success': False,
                    'error': str(e)
                })
        return results

    def _html_to_text(self, html):
        """Convertit le HTML en texte simple"""
        # Implémentation basique - à améliorer selon les besoins
        text = html
        text = text.replace('<br>', '\n')
        text = text.replace('</p>', '\n\n')
        text = text.replace('</div>', '\n')
        
        # Suppression des balises HTML restantes
        while '<' in text and '>' in text:
            start = text.find('<')
            end = text.find('>')
            if start < end:
                text = text[:start] + text[end+1:]
        
        return text.strip()

    def validate_email(self, email):
        """Valide une adresse email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
