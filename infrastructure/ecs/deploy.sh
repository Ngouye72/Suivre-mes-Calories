#!/bin/bash

# Variables d'environnement requises
# AWS_ACCOUNT_ID
# AWS_REGION
# ECR_REPOSITORY
# IMAGE_TAG

# Configuration AWS
aws configure set default.region ${AWS_REGION}

# Login ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build et push de l'image
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}

# Mise à jour de la task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Mise à jour du service ECS
aws ecs update-service \
  --cluster nutrition-cluster \
  --service nutrition-service \
  --task-definition nutrition-app \
  --force-new-deployment

# Attente de la stabilisation du déploiement
aws ecs wait services-stable \
  --cluster nutrition-cluster \
  --services nutrition-service
