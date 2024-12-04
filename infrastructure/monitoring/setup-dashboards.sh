#!/bin/bash

# Variables requises
# AWS_REGION
# DASHBOARD_NAME

# Création/Mise à jour du dashboard principal
aws cloudwatch put-dashboard \
    --dashboard-name ${DASHBOARD_NAME} \
    --dashboard-body file://dashboards/main-dashboard.json

# Vérification du dashboard
aws cloudwatch get-dashboard \
    --dashboard-name ${DASHBOARD_NAME}

echo "Dashboard ${DASHBOARD_NAME} déployé avec succès"
