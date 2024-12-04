#!/usr/bin/env python3
import requests
import json
import os
import sys
from datetime import datetime

def send_test_alert(webhook_url: str, environment: str = "production"):
    """Envoie une alerte test à Slack"""
    
    payload = {
        "text": "🧪 Test Alert System",
        "attachments": [
            {
                "color": "#36a64f",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Environnement:* {environment}\n*Date:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ Le système d'alertes est correctement configuré!"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "🔍 Test automatique du système de monitoring"
                            }
                        ]
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("✅ Test alert envoyée avec succès!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'envoi de l'alerte: {str(e)}")
        return False

def verify_slack_config(config_file: str) -> bool:
    """Vérifie la configuration Slack dans le fichier alertmanager"""
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        # Vérifie les éléments essentiels
        required_elements = [
            'slack_api_url',
            'channel',
            'send_resolved',
            'title',
            'text'
        ]
        
        missing = [elem for elem in required_elements if elem not in content]
        
        if missing:
            print(f"❌ Configuration incomplète. Éléments manquants: {', '.join(missing)}")
            return False
            
        print("✅ Configuration Slack valide!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la configuration: {str(e)}")
        return False

if __name__ == "__main__":
    # Récupère l'URL webhook depuis les variables d'environnement
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL non définie dans les variables d'environnement")
        sys.exit(1)
        
    # Vérifie la configuration
    config_file = "../alertmanager.yml"
    if not verify_slack_config(config_file):
        sys.exit(1)
        
    # Envoie une alerte test
    if not send_test_alert(webhook_url):
        sys.exit(1)
        
    print("✅ Tests terminés avec succès!")
