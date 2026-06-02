# InvestBuddy — Plateforme MLOps Crypto

**InvestBuddy** est un écosystème financier intelligent conçu pour démocratiser l'investissement crypto tout en maîtrisant les risques. Il combine un moteur de prédiction ML, un agent IA pédagogique (RAG), un pipeline MLOps complet et une boucle Human-in-the-Loop.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌──────┐  ┌───────────────┐  │
│  │  webapp  │  │ prediction-  │  │agent │  │   evidently   │  │
│  │ React/   │  │    api       │  │ api  │  │  (monitoring) │  │
│  │  Vite    │  │  FastAPI     │  │FastA │  │               │  │
│  │ :5173    │  │   :8080      │  │:4000 │  │    :8082      │  │
│  └────┬─────┘  └──────┬───────┘  └──┬───┘  └───────┬───────┘  │
│       │               │              │               │          │
│       └───────────────┴──────────────┴───────────────┘          │
│                              │                                  │
│                    ┌─────────┴──────────┐                       │
│                    │      mysql :3306   │                       │
│                    └────────────────────┘                       │
│                                                                 │
│  ┌──────────────────────────────────────┐                       │
│  │         n8n :5678                    │                       │
│  │  (orchestrateur + emails de feedback)│                       │
│  └──────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Port | Rôle |
|---|---|---|
| `webapp` | 5173 | Frontend React + Vite (dashboard, chat, prédictions) |
| `prediction-api` | 8080 | API FastAPI : prédiction ML, auth, feedback, réentraînement |
| `agent-api` | 4000 | API FastAPI : RAG financier, analyse de risque (GPT-4o-mini) |
| `evidently` | 8082 | Monitoring de data drift (Evidently AI) |
| `n8n` | 5678 | Orchestrateur : envoi d'emails Human-in-the-Loop |
| `mysql` | 3306 | Base de données utilisateurs |

---

## Fonctionnalités

### Prédiction ML (`prediction-api`)
- Modèles RandomForest entraînés sur données OHLCV + indicateurs techniques (RSI, ATR, SMA, EMA)
- Prédiction de la **volatilité** et de la **direction** (hausse/baisse) pour BTC et ETH
- Endpoint `/predict` — prédiction en temps réel
- Endpoint `/notify` — envoi d'un email de feedback via n8n
- Endpoint `/feedback` — collecte du retour utilisateur (Human-in-the-Loop) dans `prod_data.csv`
- Endpoint `/retrain/{currency}` — réentraînement automatique déclenché par drift ou seuil de feedback

### Agent IA RAG (`agent-api`)
- Base vectorielle FAISS alimentée par actualités crypto et dataset FinRAD
- Embeddings OpenAI (`text-embedding-3-small`) + LLM `gpt-4o-mini`
- Endpoint `/ask` — questions sur la finance crypto
- Endpoint `/analyzeRisk` — analyse de risque enrichie par : Fear & Greed Index, Funding Rate Binance, actualités récentes et prédiction ML

### Monitoring (`evidently`)
- Détection de **data drift** entre données de référence et données de production
- Trigger automatique de réentraînement si le score de drift dépasse le seuil (0.3)
- Dashboard Evidently accessible sur `:8082`

### Human-in-the-Loop (`n8n`)
- L'utilisateur reçoit un email après une prédiction importante
- Deux liens : **Confirmer** ou **Corriger** la prédiction
- Le choix est stocké dans `prod_data.csv` et sert à améliorer le modèle

---

## Démarrage

### Prérequis
- Docker et Docker Compose installés

### Configuration

**`agent/.env`**
```
OPENAI_API_KEY=sk-...
```

**`n8n/.env`**
```
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_FROM_EMAIL=
OPENAI_API_KEY=
N8N_WEBHOOK_URL=
WEBHOOK_URL=
N8N_BASIC_AUTH_ACTIVE=
N8N_USER_MANAGEMENT_DISABLED=
N8N_DEFAULT_USER_EMAIL=
N8N_DEFAULT_USER_PASSWORD=
N8N_SKIP_SETUP_WIZARD=
N8N_ENCRYPTION_KEY=
GENERIC_TIMEZONE=Europe/Paris
```

### Lancement

```bash
docker compose up --build
```

Après le démarrage, aller sur `http://localhost:5678` pour **activer le workflow n8n** importé automatiquement.

---

## Structure du projet

```
cryptoLLM/
├── agent/                  # Agent RAG (FastAPI, FAISS, OpenAI)
│   ├── main.py             # API /ask et /analyzeRisk
│   ├── risk_analyzer.py    # Retriever FAISS + LLM
│   ├── search_engine.py    # Recherche dans ChromaDB
│   ├── rag_edu_logic.py    # Logique RAG éducative
│   └── data/education/     # Dataset FinRAD
├── serving/                # API de prédiction ML (FastAPI)
│   ├── api.py              # /predict, /notify, /feedback, /retrain
│   ├── artifacts/          # Modèles et scalers sérialisés (.pickle)
│   └── data/               # Données de référence par devise
├── webapp/                 # Frontend React + Vite + TailwindCSS
│   └── src/app/
│       ├── pages/          # Dashboard, AskAI, Login, Register
│       └── components/     # ChatInterface, RiskCard, MagicAnalysis...
├── reporting/              # Monitoring Evidently AI
│   └── project.py          # Génération rapports + trigger réentraînement
├── n8n/                    # Orchestrateur n8n
│   └── workflows/          # Workflow email Human-in-the-Loop
├── bd/
│   └── init.sql            # Schéma MySQL (table User)
├── data/                   # Données OHLCV BTC/ETH + prod_data.csv
└── docker-compose.yaml
```

---

## Stack Technologique

| Catégorie | Outils |
|---|---|
| Frontend | React, Vite, TailwindCSS, shadcn/ui |
| Backend ML | FastAPI, scikit-learn, RandomForest, joblib |
| Agent IA | LangChain, OpenAI GPT-4o-mini, FAISS, ChromaDB |
| Monitoring | Evidently AI |
| Orchestration | n8n (workflows + emails) |
| Base de données | MySQL 8.0 |
| Données marché | Binance API (OHLCV BTC/ETH) |
| Conteneurisation | Docker, Docker Compose |
