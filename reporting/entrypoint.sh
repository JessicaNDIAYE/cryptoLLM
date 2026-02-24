#!/bin/bash

echo "Lancement initial du monitoring Evidently..."
python project.py

echo "Démarrage de l'UI Evidently..."
evidently ui --workspace /app/workspace --host 0.0.0.0 --port 8082 &

# Boucle infinie : monitoring toutes les 12 heures (43200 sec)
while true
do
    sleep 43200
    echo "Monitoring périodique Evidently (toutes les 12h)..."
    python project.py
done