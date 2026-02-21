# n8n — Orchestrateur IA InvestBuddy

## Description

n8n est l'orchestrateur qui gère les notifications automatiques et le cycle **Human-in-the-Loop** du projet InvestBuddy.

### Flux de traitement

```
Prédiction ML (forte volatilité)
        ↓
  POST /notify  (prediction-api)
        ↓
  Webhook n8n   (http://n8n:5678/webhook/investbuddy-alert)
        ↓
  Nœud IF : volatilité > 0.02 ?
        ↓ OUI
  OpenAI GPT-3.5 → génère message personnalisé
        ↓
  Envoi email HTML avec 2 boutons :
    ✅ "Confirmer la prédiction"  → GET /feedback?label=confirm&...
    ❌ "Corriger la prédiction"   → GET /feedback?label=deny&...
        ↓
  Utilisateur clique → prediction-api stocke dans prod_data.csv
        ↓
  Si lignes % RETRAIN_THRESHOLD == 0 → Réentraînement automatique
```

---

## Démarrage

### 1. Lancer tous les services avec Docker Compose

```bash
# Copier le fichier de configuration
cp .env.example .env
# Remplir les valeurs dans .env (SMTP, OpenAI, etc.)

# Démarrer tout
docker-compose up -d
```

### 2. Accéder à l'interface n8n

Ouvrir : **http://localhost:5678**

### 3. Importer le workflow

1. Dans n8n, aller dans **Workflows** → **Import from file**
2. Sélectionner `n8n/workflows/investbuddy_alert.json`
3. Configurer les credentials (voir section suivante)
4. **Activer le workflow** (toggle en haut à droite)

---

## Configuration des Credentials dans n8n

### OpenAI API
- Aller dans **Credentials** → **Add credential** → **OpenAI**
- Renseigner votre `OPENAI_API_KEY`

### SMTP (Gmail)
- Aller dans **Credentials** → **Add credential** → **SMTP**
- Host : `smtp.gmail.com`
- Port : `587`
- User : votre email Gmail
- Password : **Mot de passe d'application** (pas votre mot de passe normal)
  - Générer sur : https://myaccount.google.com/apppasswords
  - Activer d'abord : Authentification à 2 facteurs

---

## Variables d'environnement requises

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SMTP_USERNAME` | Email Gmail expéditeur | `alerts@gmail.com` |
| `SMTP_PASSWORD` | Mot de passe d'application Gmail | `xxxx xxxx xxxx xxxx` |
| `SMTP_FROM_EMAIL` | Email affiché | `alerts@investbuddy.com` |
| `OPENAI_API_KEY` | Clé API OpenAI | `sk-proj-...` |

---

## Tester le workflow manuellement

```bash
curl -X POST http://localhost:5678/webhook/investbuddy-alert \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "BTCUSDT",
    "prediction": {"volatility": 0.05, "direction": "down"},
    "user_email": "test@example.com",
    "user_name": "Jean Dupont",
    "feedback_confirm_url": "http://localhost:8080/feedback?currency=BTCUSDT&label=confirm&prediction_vol=0.05&prediction_dir=down&Open=95000&High=96000&Low=94000&Close=95500&Volume=1000&RSI=45&ATR=200&VolumeChange=0.01&SMA_20=95000&EMA_50=94000",
    "feedback_deny_url": "http://localhost:8080/feedback?currency=BTCUSDT&label=deny&prediction_vol=0.05&prediction_dir=down&Open=95000&High=96000&Low=94000&Close=95500&Volume=1000&RSI=45&ATR=200&VolumeChange=0.01&SMA_20=95000&EMA_50=94000"
  }'
```

---

## Architecture des endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `POST /predict` | prediction-api:8080 | Prédiction ML (volatilité + direction) |
| `POST /notify` | prediction-api:8080 | Déclenche alerte n8n |
| `GET /feedback` | prediction-api:8080 | Reçoit le feedback utilisateur, stocke dans prod_data.csv |
| `POST /webhook/investbuddy-alert` | n8n:5678 | Webhook d'entrée n8n |
