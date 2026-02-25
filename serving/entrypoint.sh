#!/bin/bash


echo "Lancement de la mise à jour initiale des données et modèles..."
python update_data.py

# 2. Lancer l'API FastAPI en arrière-plan
echo "Démarrage de l'API de prédiction..."
uvicorn api:app --host 0.0.0.0 --port 8080 &

# 3. Boucle infinie pour mettre à jour toutes les 6 heures
while true
do
    sleep 21600
    echo "Mise à jour périodique (toutes les 6h)..."
    python update_data.py
done