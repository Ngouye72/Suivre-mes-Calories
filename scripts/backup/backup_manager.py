import boto3
import os
import logging
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional
import pytz

class BackupManager:
    def __init__(self, 
                 bucket_name: str,
                 db_name: str,
                 db_user: str,
                 retention_days: int = 30):
        self.bucket_name = bucket_name
        self.db_name = db_name
        self.db_user = db_user
        self.retention_days = retention_days
        self.s3 = boto3.client('s3')
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def create_backup(self) -> Optional[str]:
        """Crée un backup de la base de données"""
        try:
            timestamp = datetime.now(pytz.UTC).strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_{self.db_name}_{timestamp}.sql"
            
            # Création du backup avec pg_dump
            cmd = [
                'pg_dump',
                '-U', self.db_user,
                '-F', 'c',  # Format personnalisé
                '-b',  # Inclut les large objects
                '-v',  # Mode verbose
                '-f', backup_file,
                self.db_name
            ]
            
            self.logger.info(f"Création du backup: {backup_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erreur pg_dump: {result.stderr}")
                
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du backup: {str(e)}")
            return None
            
    def upload_to_s3(self, file_path: str) -> bool:
        """Upload le backup vers S3"""
        try:
            self.logger.info(f"Upload vers S3: {file_path}")
            
            # Upload avec metadata
            self.s3.upload_file(
                file_path,
                self.bucket_name,
                f"backups/{os.path.basename(file_path)}",
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'database': self.db_name,
                        'timestamp': datetime.now(pytz.UTC).isoformat()
                    }
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'upload: {str(e)}")
            return False
            
    def cleanup_old_backups(self):
        """Supprime les anciens backups selon la rétention"""
        try:
            self.logger.info("Nettoyage des anciens backups...")
            
            # Calcul de la date limite
            cutoff_date = datetime.now(pytz.UTC) - timedelta(days=self.retention_days)
            
            # Liste des backups
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='backups/'
            )
            
            if 'Contents' not in response:
                return
                
            # Suppression des vieux backups
            for obj in response['Contents']:
                last_modified = obj['LastModified']
                if last_modified < cutoff_date:
                    self.logger.info(f"Suppression: {obj['Key']}")
                    self.s3.delete_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage: {str(e)}")
            
    def list_backups(self) -> List[dict]:
        """Liste tous les backups disponibles"""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='backups/'
            )
            
            backups = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Récupération des metadata
                    head = self.s3.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
                    backups.append({
                        'file': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'metadata': head.get('Metadata', {})
                    })
                    
            return backups
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la liste des backups: {str(e)}")
            return []
            
    def restore_backup(self, backup_key: str) -> bool:
        """Restaure un backup depuis S3"""
        try:
            self.logger.info(f"Restauration du backup: {backup_key}")
            
            # Téléchargement du backup
            local_file = f"/tmp/{os.path.basename(backup_key)}"
            self.s3.download_file(
                self.bucket_name,
                backup_key,
                local_file
            )
            
            # Restauration avec pg_restore
            cmd = [
                'pg_restore',
                '-U', self.db_user,
                '-d', self.db_name,
                '-v',
                '--clean',  # Nettoie la DB avant restauration
                '--if-exists',
                local_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Nettoyage
            os.remove(local_file)
            
            if result.returncode != 0:
                raise Exception(f"Erreur pg_restore: {result.stderr}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la restauration: {str(e)}")
            return False

if __name__ == "__main__":
    # Configuration depuis les variables d'environnement
    backup_manager = BackupManager(
        bucket_name=os.getenv('AWS_BACKUP_BUCKET'),
        db_name=os.getenv('DB_NAME'),
        db_user=os.getenv('DB_USER'),
        retention_days=int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    )
    
    # Création et upload d'un nouveau backup
    backup_file = backup_manager.create_backup()
    if backup_file:
        if backup_manager.upload_to_s3(backup_file):
            print("✅ Backup créé et uploadé avec succès")
            # Nettoyage du fichier local
            os.remove(backup_file)
            
            # Nettoyage des anciens backups
            backup_manager.cleanup_old_backups()
        else:
            print("❌ Erreur lors de l'upload du backup")
    else:
        print("❌ Erreur lors de la création du backup")
