#!/bin/bash

# Variables de configuration
HOST="http://localhost:5000"
USERS=100
SPAWN_RATE=10
RUNTIME="10m"
REPORT_DIR="reports/load_tests"

# Création du dossier de rapports
mkdir -p $REPORT_DIR

# Date pour le nom du rapport
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Exécution des tests avec Locust
echo "Démarrage des tests de charge..."
echo "Host: $HOST"
echo "Nombre d'utilisateurs: $USERS"
echo "Taux de spawn: $SPAWN_RATE/seconde"
echo "Durée: $RUNTIME"

locust \
    --host=$HOST \
    --users=$USERS \
    --spawn-rate=$SPAWN_RATE \
    --run-time=$RUNTIME \
    --headless \
    --csv=$REPORT_DIR/report_$TIMESTAMP \
    --html=$REPORT_DIR/report_$TIMESTAMP.html \
    -f locustfile.py

echo "Tests terminés. Rapports générés dans $REPORT_DIR"
