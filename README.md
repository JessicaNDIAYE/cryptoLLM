# cryptoLLM

#  Projet MLOps : Explication et Prédiction de Crypto & Agent Conseiller

Ce projet met en œuvre un pipeline MLOps de bout en bout pour la prédiction de la volatilité des actifs crypto (BTC/ETH, etc.) et intègre un Agent IA intelligent pour la gestion des risques et le feedback automatisé (Human-in-the-Loop).

Il est basé sur l'architecture de déploiement continu et de monitoring demandée dans le cadre du projet DATA de Polytech Lyon.

---

##  Objectifs du Projet

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

##  Architecture du Projet

L'architecture est basée sur une série de services conteneurisés communiquant via un réseau Docker Compose (`prod_net`).

**Composants Clés :**

- **`serving`** : Contient l'API FastAPI et les modèles sérialisés (artefacts).
- **`webapp`** : Contient l'application Streamlit pour l'interface utilisateur.
- **`reporting`** : Contient le script Evidently pour le monitoring et la détection de dérive.
- **`data`** : Contient les données de référence (`ref_data.csv`) et les données de production/feedback (`prod_data.csv`).

---

##  Démarrage Rapide

### Prérequis

1. ]**Docker & Docker Compose :** Assurez-vous d'avoir installé Docker Desktop.
2. **Clés Binance (Optionnel) :** Non requises pour les données publiques, mais peuvent être nécessaires selon le volume d'appels.

### 1. Préparation du Modèle (Entraînement Initial)

Exécutez le scripts dans le dossier `data` pour :

1.  Récupérer les données historiques via l'API Binance.


###  Description

**InvestBuddy** est un écosystème financier intelligent conçu pour démocratiser l'investissement crypto tout en maîtrisant les risques. Le projet repose sur une architecture **MLOps industrielle** qui combine trois piliers :

1. Un **moteur prédictif** qui analyse la volatilité des marchés en temps réel pour optimiser la gestion de portefeuille.
2. Un **Agent IA pédagogique** qui utilise le RAG (Retrieval Augmented Generation) pour traduire des concepts financiers complexes en langage simple et accompagner l'utilisateur.
3. Un **pipeline de déploiement continu** qui surveille les performances du modèle, collecte le feedback humain, et déclenche automatiquement des réentraînements pour s'adapter aux changements brutaux du marché.

---

###  To-Do List détaillée du Projet

####  Étape 1 : Fondations & Agent Pédagogique (RAG) — **[x]**

- [x] ~~Ingestion de données financières (Dataset FinRAD)~~
- [x] ~~Mise en place de ChromaDB (Base vectorielle)~~
- [x] ~~Recherche sémantique avec OpenAI Embeddings~~
- [x] ~~API de Serving initiale avec FastAPI~~
- [x] ~~Interface Chat Next.js avec effet Typewriter~~
- [x] ~~Correction des erreurs CORS et intégration Frontend/Backend~~

#### Étape 2 : Intelligence Artificielle & Prédiction ML — **[À FAIRE ]**

* [x] ~~**Collecte de données de marché** : Script d'extraction via API Binance/YFinance (Prix OHLCV).~~
* [ ] **Feature Engineering** : Calcul des indicateurs techniques (RSI, Volatilité, Moyennes Mobiles).
* [ ] **Entraînement du modèle** : Création du modèle de prédiction de volatilité (RandomForest ou LSTM).
* [ ] **Export des Artefacts** : Sauvegarde du modèle et des scalers au format `.pkl` ou `.joblib`.
* [ ] **Endpoint `/predict**` : Intégration du modèle ML dans l'API FastAPI pour des prédictions en temps réel.

####  Étape 3 : Orchestration & Agent IA (n8n) — **[À FAIRE ]**

* [ ] **Workflow n8n** : Création du tunnel entre l'API et l'utilisateur.
* [ ] Lancer docker faire en sorte que tout marche avec docker.
* [ ] Attendre que Thibault fasse le docker 
* [ ] **Système de Notification** : Automatisation de l'envoi d'alertes par e-mail en cas de forte volatilité.
* [ ] **Human-in-the-Loop** : Mise en place des boutons de feedback dans les emails (Validation de la prédiction).
* [ ] **Stockage Feedback** : Enregistrement des retours utilisateurs dans `prod_data.csv`.

#### Étape 4 : Monitoring & MLOps Industriel — **[À FAIRE ]**
* [ ] Dockerfile pour les utilisateurs mysql .
* [ ] **Monitoring avec Evidently AI** : Dashboard de détection de Data Drift (comparaison `ref_data` vs `prod_data`).
* [ ] **Trigger de Réentraînement** : Script surveillant la taille de `prod_data.csv` pour relancer `train_model.py`.
* [ ] **Conteneurisation Docker** :
* [x] ~~Dockerfile pour l'API FastAPI~~.
* [x] ~~Dockerfile pour le Frontend Next.js.~~
* [ ] Docker Compose pour orchestrer l'API, la DB, n8n et le monitoring.

####  Étape 5 : Finalisation & Rapport — **[À FAIRE ]**

* [ ] **Tests unitaires** sur les routes critiques de l'API.
* [ ] **Rédaction du rapport technique** (Architecture, choix technologiques, analyse du drift).
* [ ] **Préparation de la soutenance** (Démonstration du cycle de réentraînement automatique).

---
