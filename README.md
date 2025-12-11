# cryptoLLM

# 📈 Projet MLOps : Explication et Prédiction de Crypto & Agent Conseiller

Ce projet met en œuvre un pipeline MLOps de bout en bout pour la prédiction de la volatilité des actifs crypto (BTC/ETH, etc.) et intègre un Agent IA intelligent pour la gestion des risques et le feedback automatisé (Human-in-the-Loop).

Il est basé sur l'architecture de déploiement continu et de monitoring demandée dans le cadre du projet DATA de Polytech Lyon.

---

## 🎯 Objectifs du Projet

1.  **Prédiction de Volatilité :** Développer et déployer un modèle de série temporelle capable de prédire les périodes de forte volatilité sur un horizon de 1 à 2 jours.
2.  **MLOps Complet :** Mettre en place un pipeline d'entraînement, de déploiement et de monitoring automatisé et conteneurisé.
3.  **Agent IA Conseiller :** Intégrer un Agent IA (orchestrateur + LLM) pour analyser les prédictions et les événements du marché, et suggérer des ajustements de stratégie (conseil ou tâche automatique).
4.  **Boucle Human-in-the-Loop :** Créer un mécanisme pour recueillir le feedback utilisateur (ou la validation du conseil de l'Agent) et l'utiliser pour ré-entraîner et améliorer continuellement le modèle.

---

## 🛠️ Stack Technologique

| Catégorie             | Outils                   | Rôle dans le Projet                                      |
| :-------------------- | :----------------------- | :------------------------------------------------------- |
| **Import de Données** | Python, `python-binance` | Récupération des données historiques (OHLCV) de Binance. |

---

## 🏗️ Architecture du Projet

L'architecture est basée sur une série de services conteneurisés communiquant via un réseau Docker Compose (`prod_net`).

**Composants Clés :**

- **`serving`** : Contient l'API FastAPI et les modèles sérialisés (artefacts).
- **`webapp`** : Contient l'application Streamlit pour l'interface utilisateur.
- **`reporting`** : Contient le script Evidently pour le monitoring et la détection de dérive.
- **`data`** : Contient les données de référence (`ref_data.csv`) et les données de production/feedback (`prod_data.csv`).

---

## 🚀 Démarrage Rapide

### Prérequis

1. ]**Docker & Docker Compose :** Assurez-vous d'avoir installé Docker Desktop.
2. **Clés Binance (Optionnel) :** Non requises pour les données publiques, mais peuvent être nécessaires selon le volume d'appels.

### 1. Préparation du Modèle (Entraînement Initial)

Exécutez le scripts dans le dossier `data` pour :

1.  Récupérer les données historiques via l'API Binance.
