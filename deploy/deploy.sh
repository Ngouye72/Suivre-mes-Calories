#!/bin/bash

# Variables d'environnement
ENV=${1:-production}
VERSION=$(git describe --tags --always)
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chargement des variables d'environnement
if [ -f "$DEPLOY_DIR/.env.$ENV" ]; then
    source "$DEPLOY_DIR/.env.$ENV"
else
    echo "Fichier .env.$ENV non trouvé"
    exit 1
fi

echo "🚀 Déploiement de l'application en $ENV (version: $VERSION)"

# Vérification prérequis
echo "✨ Vérification des prérequis..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker requis mais non installé"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose requis mais non installé"; exit 1; }

# Backup base de données
echo "💾 Backup de la base de données..."
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose -f docker-compose.prod.yml exec db pg_dump -U $DB_USER $DB_NAME > "backups/$BACKUP_FILE"

# Build des images
echo "🏗️ Build des images Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Arrêt des conteneurs existants
echo "⏹️ Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml down

# Démarrage des nouveaux conteneurs
echo "▶️ Démarrage des nouveaux conteneurs..."
docker-compose -f docker-compose.prod.yml up -d

# Vérification de la santé des services
echo "🏥 Vérification de la santé des services..."
sleep 10

check_health() {
    local service=$1
    local max_retries=30
    local retry=0
    
    echo "Vérification de $service..."
    while [ $retry -lt $max_retries ]; do
        if docker-compose -f docker-compose.prod.yml ps $service | grep -q "healthy"; then
            echo "✅ $service est opérationnel"
            return 0
        fi
        echo "⏳ Attente de $service... ($retry/$max_retries)"
        sleep 2
        ((retry++))
    done
    
    echo "❌ $service n'est pas opérationnel après $max_retries tentatives"
    return 1
}

services=("db" "cache" "api" "nginx")
failed=false

for service in "${services[@]}"; do
    if ! check_health $service; then
        failed=true
    fi
done

if [ "$failed" = true ]; then
    echo "❌ Certains services ne sont pas opérationnels"
    echo "📜 Logs des conteneurs :"
    docker-compose -f docker-compose.prod.yml logs
    
    echo "⏮️ Restauration du backup..."
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d db
    sleep 10
    cat "backups/$BACKUP_FILE" | docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER $DB_NAME
    
    exit 1
fi

# Migration base de données
echo "🔄 Migration de la base de données..."
docker-compose -f docker-compose.prod.yml exec api flask db upgrade

# Nettoyage
echo "🧹 Nettoyage..."
docker system prune -f

# Vérification finale
echo "🔍 Vérification finale..."
curl -f http://localhost:5000/health || { echo "❌ L'API n'est pas accessible"; exit 1; }

echo "✅ Déploiement terminé avec succès!"

# Notification Slack
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Déploiement $ENV v$VERSION terminé avec succès!\"}" \
        $SLACK_WEBHOOK_URL
fi
