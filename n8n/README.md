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

## 🚀 Démarrage Rapide (Configuration Automatique)

### 1. Configurer les variables d'environnement

```bash
# Aller dans le dossier n8n
cd n8n

# Copier le fichier template
cp .env .env.local  # ou modifier directement .env

# Éditer le fichier .env avec vos valeurs
```

### 2. Variables obligatoires à remplir dans `n8n/.env`

| Variable | Description | Comment l'obtenir |
|----------|-------------|-------------------|
| `SMTP_HOST` | Serveur SMTP | `smtp.gmail.com` pour Gmail |
| `SMTP_PORT` | Port SMTP | `587` (TLS) |
| `SMTP_USERNAME` | Email expéditeur | Votre email Gmail |
| `SMTP_PASSWORD` | Mot de passe d'application | [Voir guide Gmail](#configuration-smtp-gmail) |
| `SMTP_FROM_EMAIL` | Email affiché | Votre email Gmail |
| `OPENAI_API_KEY` | Clé API OpenAI | https://platform.openai.com/api-keys |
| `N8N_ENCRYPTION_KEY` | Clé de chiffrement | **Changez cette valeur!** (string aléatoire) |

### 3. Lancer n8n avec Docker Compose

```bash
# Depuis la racine du projet
docker-compose --file docker-compose.yaml --file n8n/docker-compose.override.yml up -d n8n

# Ou pour tous les services
docker-compose --file docker-compose.yaml --file n8n/docker-compose.override.yml up -d
```

### 4. Accéder à n8n

- **Dashboard n8n** : http://localhost:5678
- **Webhook URL** : http://localhost:5678/webhook/investbuddy-alert

Le workflow et les credentials sont **automatiquement importés** au démarrage!

---

## 📧 Configuration SMTP Gmail

### Étape 1 : Activer l'authentification à 2 facteurs
1. Aller sur https://myaccount.google.com/security
2. Activer "Vérification en deux étapes"

### Étape 2 : Générer un mot de passe d'application
1. Aller sur https://myaccount.google.com/apppasswords
2. Sélectionner "Mail" et "Autre (nom personnalisé)"
3. Entrer "InvestBuddy n8n"
4. Cliquer "Générer"
5. **Copier le mot de passe à 16 caractères** (format: `xxxx xxxx xxxx xxxx`)

### Étape 3 : Configurer dans `.env`
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=votre-email@gmail.com
```

---

## 🔧 Configuration Manuelle (si besoin)

Si l'auto-configuration ne fonctionne pas, vous pouvez configurer manuellement :

### Importer le workflow
1. Ouvrir http://localhost:5678
2. Aller dans **Workflows** → **Import from file**
3. Sélectionner `n8n/workflows/working_workflow.json`

### Configurer les credentials

#### OpenAI API
1. **Credentials** → **Add credential** → **OpenAI**
2. Renseigner votre `API Key`

#### SMTP
1. **Credentials** → **Add credential** → **SMTP**
2. Remplir les champs avec vos paramètres SMTP

### Activer le workflow
1. Ouvrir le workflow importé
2. Cliquer sur le toggle **Active** en haut à droite

---

## 🧪 Tester le workflow

### Test rapide avec curl

```bash
curl -X POST http://localhost:5678/webhook/investbuddy-alert \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "BTCUSDT",
    "prediction": {"volatility": 0.05, "direction": "down"},
    "user_email": "votre-email@example.com",
    "user_name": "Test User",
    "feedback_confirm_url": "http://localhost:8080/feedback?currency=BTCUSDT&label=confirm&prediction_vol=0.05&prediction_dir=down&Open=95000&High=96000&Low=94000&Close=95500&Volume=1000&RSI=45&ATR=200&VolumeChange=0.01&SMA_20=95000&EMA_50=94000",
    "feedback_deny_url": "http://localhost:8080/feedback?currency=BTCUSDT&label=deny&prediction_vol=0.05&prediction_dir=down&Open=95000&High=96000&Low=94000&Close=95500&Volume=1000&RSI=45&ATR=200&VolumeChange=0.01&SMA_20=95000&EMA_50=94000"
  }'
```

### Résultat attendu
- Email reçu avec message généré par l'IA
- Deux boutons : ✅ Confirmer / ❌ Corriger

---

## 📁 Structure des fichiers n8n

```
n8n/
├── .env                      # Variables d'environnement (À CONFIGURER)
├── docker-compose.override.yml # Override Docker Compose pour n8n
├── init-n8n.sh              # Script d'auto-configuration
├── README.md                # Ce fichier
└── workflows/
    ├── working_workflow.json # Workflow actif à importer
    └── investbuddy_alert.json # Ancienne version (backup)
```

---

## 🔐 Sécurité

### Variables sensibles
- **Ne jamais commiter** le fichier `.env` avec de vraies valeurs
- Utiliser `.env.example` comme template
- Le `.gitignore` exclut déjà `.env`

### Clé de chiffrement
- `N8N_ENCRYPTION_KEY` protège les credentials stockés
- **Important** : Changez cette valeur en production!
- Générer une clé aléatoire : `openssl rand -hex 32`

---

## 🛠️ Dépannage

### n8n ne démarre pas
```bash
# Vérifier les logs
docker-compose logs n8n

# Redémarrer le service
docker-compose restart n8n
```

### Workflow non importé automatiquement
```bash
# Vérifier que le script s'est exécuté
docker-compose logs n8n | grep "InvestBuddy"

# Importer manuellement via l'interface
```

### Erreur SMTP
- Vérifier que le mot de passe d'application est correct
- Pour Gmail, s'assurer que l'authentification 2FA est active
- Tester avec un autre client SMTP

### Erreur OpenAI
- Vérifier que `OPENAI_API_KEY` commence par `sk-`
- Vérifier que la clé a des crédits disponibles
- Tester la clé : `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

---

## 📊 Architecture des endpoints

| Endpoint | Service | Méthode | Description |
|----------|---------|---------|-------------|
| `/predict` | prediction-api:8080 | POST | Prédiction ML (volatilité + direction) |
| `/notify` | prediction-api:8080 | POST | Déclenche alerte n8n |
| `/feedback` | prediction-api:8080 | GET | Reçoit le feedback utilisateur |
| `/webhook/investbuddy-alert` | n8n:5678 | POST | Webhook d'entrée n8n |

---

## 🔄 Mise à jour du workflow

1. Modifier le workflow dans n8n
2. Exporter : **Workflows** → **Export**
3. Sauvegarder dans `n8n/workflows/working_workflow.json`
4. Commiter les changements