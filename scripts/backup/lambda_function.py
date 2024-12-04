import json
import os
import boto3
from datetime import datetime
import logging
from backup_manager import BackupManager

# Configuration du logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Fonction Lambda pour gérer les backups automatiques
    
    Event format:
    {
        "action": "backup"|"restore"|"list"|"cleanup",
        "backup_key": "optional-backup-key-for-restore"
    }
    """
    try:
        # Initialisation du backup manager
        backup_manager = BackupManager(
            bucket_name=os.environ['BACKUP_BUCKET'],
            db_name=os.environ['DB_NAME'],
            db_user=os.environ['DB_USER'],
            retention_days=int(os.environ.get('RETENTION_DAYS', 30))
        )
        
        action = event.get('action', 'backup')
        
        if action == 'backup':
            # Création d'un nouveau backup
            backup_file = backup_manager.create_backup()
            if not backup_file:
                raise Exception("Échec de la création du backup")
                
            # Upload vers S3
            if not backup_manager.upload_to_s3(backup_file):
                raise Exception("Échec de l'upload vers S3")
                
            # Nettoyage du fichier local
            os.remove(backup_file)
            
            # Nettoyage des anciens backups
            backup_manager.cleanup_old_backups()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Backup créé et uploadé avec succès',
                    'file': backup_file
                })
            }
            
        elif action == 'restore':
            # Restauration d'un backup spécifique
            backup_key = event.get('backup_key')
            if not backup_key:
                raise ValueError("backup_key requis pour la restauration")
                
            success = backup_manager.restore_backup(backup_key)
            
            return {
                'statusCode': 200 if success else 500,
                'body': json.dumps({
                    'status': 'success' if success else 'error',
                    'message': f"Restauration {'réussie' if success else 'échouée'}"
                })
            }
            
        elif action == 'list':
            # Liste des backups disponibles
            backups = backup_manager.list_backups()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'backups': backups
                })
            }
            
        elif action == 'cleanup':
            # Nettoyage manuel des anciens backups
            backup_manager.cleanup_old_backups()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Nettoyage des anciens backups effectué'
                })
            }
            
        else:
            raise ValueError(f"Action non supportée: {action}")
            
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }

if __name__ == "__main__":
    # Test local
    test_event = {
        "action": "backup"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
