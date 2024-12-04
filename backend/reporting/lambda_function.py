import os
import json
from report_generator import ReportGenerator

def lambda_handler(event, context):
    """Fonction Lambda pour générer et envoyer les rapports quotidiens"""
    try:
        # Initialisation du générateur
        generator = ReportGenerator()
        
        # Génération du rapport
        report_content = generator.generate_daily_report()
        
        # Sauvegarde dans S3
        report_url = generator.save_report(report_content, 'daily')
        
        if report_url:
            # Envoi de la notification
            generator.send_report_notification(report_url)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Rapport généré avec succès',
                    'url': report_url
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Erreur lors de la génération du rapport'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Erreur: {str(e)}'
            })
        }
