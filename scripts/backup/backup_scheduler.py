import boto3
import json
from typing import Dict, Any

class BackupScheduler:
    def __init__(self, region: str = 'eu-west-1'):
        self.eventbridge = boto3.client('events', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        
    def create_backup_rule(self, 
                          rule_name: str,
                          schedule: str,
                          lambda_function: str,
                          description: str = "Backup automatique de la base de données") -> Dict[str, Any]:
        """
        Crée une règle EventBridge pour les backups automatiques
        
        Args:
            rule_name: Nom de la règle
            schedule: Expression cron ou rate (ex: "cron(0 2 * * ? *)" pour 2h du matin)
            lambda_function: ARN de la fonction Lambda à déclencher
            description: Description de la règle
        """
        try:
            # Création de la règle
            response = self.eventbridge.put_rule(
                Name=rule_name,
                ScheduleExpression=schedule,
                State='ENABLED',
                Description=description
            )
            
            # Configuration de la cible (Lambda)
            target_id = f"{rule_name}-target"
            self.eventbridge.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': target_id,
                        'Arn': lambda_function,
                        'Input': json.dumps({
                            'action': 'backup',
                            'timestamp': '${aws:timestamp}'
                        })
                    }
                ]
            )
            
            # Ajout de la permission à Lambda
            self.lambda_client.add_permission(
                FunctionName=lambda_function,
                StatementId=f"{rule_name}-permission",
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=response['RuleArn']
            )
            
            return {
                'status': 'success',
                'rule_arn': response['RuleArn'],
                'message': f"Règle de backup créée: {rule_name}"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la création de la règle: {str(e)}"
            }
            
    def update_backup_schedule(self,
                             rule_name: str,
                             new_schedule: str) -> Dict[str, Any]:
        """
        Met à jour la planification d'une règle existante
        
        Args:
            rule_name: Nom de la règle à modifier
            new_schedule: Nouvelle expression de planification
        """
        try:
            response = self.eventbridge.put_rule(
                Name=rule_name,
                ScheduleExpression=new_schedule
            )
            
            return {
                'status': 'success',
                'rule_arn': response['RuleArn'],
                'message': f"Planification mise à jour: {rule_name}"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la mise à jour: {str(e)}"
            }
            
    def disable_backup_rule(self, rule_name: str) -> Dict[str, Any]:
        """Désactive une règle de backup"""
        try:
            self.eventbridge.disable_rule(Name=rule_name)
            return {
                'status': 'success',
                'message': f"Règle désactivée: {rule_name}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la désactivation: {str(e)}"
            }
            
    def enable_backup_rule(self, rule_name: str) -> Dict[str, Any]:
        """Active une règle de backup"""
        try:
            self.eventbridge.enable_rule(Name=rule_name)
            return {
                'status': 'success',
                'message': f"Règle activée: {rule_name}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de l'activation: {str(e)}"
            }
            
    def delete_backup_rule(self, rule_name: str) -> Dict[str, Any]:
        """Supprime une règle de backup et ses cibles"""
        try:
            # Suppression des cibles
            self.eventbridge.remove_targets(
                Rule=rule_name,
                Ids=[f"{rule_name}-target"]
            )
            
            # Suppression de la règle
            self.eventbridge.delete_rule(Name=rule_name)
            
            return {
                'status': 'success',
                'message': f"Règle supprimée: {rule_name}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la suppression: {str(e)}"
            }
            
    def list_backup_rules(self) -> Dict[str, Any]:
        """Liste toutes les règles de backup"""
        try:
            response = self.eventbridge.list_rules(
                NamePrefix='backup-'
            )
            
            rules = []
            for rule in response['Rules']:
                # Récupération des cibles pour chaque règle
                targets = self.eventbridge.list_targets_by_rule(
                    Rule=rule['Name']
                )
                
                rules.append({
                    'name': rule['Name'],
                    'schedule': rule['ScheduleExpression'],
                    'state': rule['State'],
                    'targets': targets['Targets']
                })
                
            return {
                'status': 'success',
                'rules': rules
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la liste des règles: {str(e)}"
            }

if __name__ == "__main__":
    # Exemple d'utilisation
    scheduler = BackupScheduler()
    
    # Création d'une règle de backup quotidien à 2h du matin
    result = scheduler.create_backup_rule(
        rule_name="backup-daily",
        schedule="cron(0 2 * * ? *)",
        lambda_function="arn:aws:lambda:eu-west-1:123456789012:function:backup-function",
        description="Backup quotidien de la base de données"
    )
    
    print(result)
