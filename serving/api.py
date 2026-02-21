from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
import joblib
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import csv
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from urllib.parse import urlencode

app = FastAPI(title='crypto prediction API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROD_DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', 'prod_data.csv'))
RETRAIN_THRESHOLD = int(os.getenv('RETRAIN_THRESHOLD', '10'))
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/investbuddy-alert')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')

# --- Variables globales : modèles chargés au démarrage ---
models = {}

# --- Modèles Pydantic ---
class CurrencyData(BaseModel):
    currency: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float
    RSI: float
    ATR: float
    VolumeChange: float
    SMA_20: float
    EMA_50: float

class NotifyRequest(BaseModel):
    currency: str
    prediction: dict
    input_data: dict
    user_email: str
    user_name: str = "Investisseur"


# --- Chargement des modèles au démarrage ---
def load_models():
    global models
    for currency in ['BTCUSDT', 'ETHUSDT']:
        try:
            models[currency] = {
                'vol': joblib.load(os.path.join(BASE_DIR, 'artifacts', f'{currency}_model_volatility.pickle')),
                'dir': joblib.load(os.path.join(BASE_DIR, 'artifacts', f'{currency}_model_direction.pickle')),
                'scaler': joblib.load(os.path.join(BASE_DIR, 'artifacts', f'{currency}_scaler.pickle')),
            }
            print(f"✅ Models loaded for {currency}")
        except Exception as e:
            print(f"⚠️ Could not load models for {currency}: {e}")

@app.on_event("startup")
async def startup_event():
    load_models()


# --- Endpoint /predict ---
@app.post('/predict')
async def predict(data: CurrencyData):
    prefix = data.currency.upper()
    if prefix not in models:
        raise HTTPException(status_code=404, detail=f"No model found for currency: {prefix}")
    try:
        m = models[prefix]
        input_data = [[
            data.Open, data.High, data.Low, data.Close, data.Volume,
            data.RSI, data.ATR, data.VolumeChange, data.SMA_20, data.EMA_50
        ]]
        input_scaled = m['scaler'].transform(input_data)
        vol_pred = float(m['vol'].predict(input_scaled)[0])
        dir_score = float(m['dir'].predict(input_scaled)[0])
        dir_pred = "up" if dir_score >= 0.5 else "down"

        return {
            "currency": data.currency,
            "prediction": {
                "volatility": vol_pred,
                "direction": dir_pred,
                "direction_score": dir_score,
            },
            "input_data": data.model_dump(exclude={"currency"})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Endpoint /notify : déclenche l'alerte n8n (Human-in-the-Loop) ---
@app.post('/notify')
async def notify_user(request: NotifyRequest, background_tasks: BackgroundTasks):
    """
    Envoie les données de prédiction à n8n qui génère et envoie
    un email avec des liens de validation (Human-in-the-Loop).
    """
    try:
        inp = request.input_data or {}
        vol = request.prediction.get('volatility', 0)
        direc = request.prediction.get('direction', 'unknown')
        currency = request.currency

        print(f"📤 /notify called with:")
        print(f"   currency: {currency}")
        print(f"   prediction: {request.prediction}")
        print(f"   input_data: {inp}")

        # Construction des paramètres avec encodage URL correct
        # Valeurs par défaut si input_data est incomplet
        default_input = {
            'Open': 42000, 'High': 43000, 'Low': 41500, 'Close': 42500,
            'Volume': 1000, 'RSI': 55, 'ATR': 0.02, 'VolumeChange': 0.1, 
            'SMA_20': 42000, 'EMA_50': 41000
        }
        
        # Fusion avec les valeurs fournies
        for key in default_input:
            if key not in inp or inp[key] is None:
                inp[key] = default_input[key]
        
        # Paramètres de base
        base_params = {
            "currency": currency,
            "prediction_vol": vol,
            "prediction_dir": direc,
        }
        
        # Construire les URLs de feedback
        confirm_params = urlencode({**base_params, **inp, "label": "confirm"})
        deny_params = urlencode({**base_params, **inp, "label": "deny"})
        
        feedback_confirm = f"{API_BASE_URL}/feedback?{confirm_params}"
        feedback_deny = f"{API_BASE_URL}/feedback?{deny_params}"

        print(f"   feedback_confirm_url: {feedback_confirm}")
        print(f"   feedback_deny_url: {feedback_deny}")

        n8n_payload = {
            "currency": currency,
            "prediction": request.prediction,
            "user_email": request.user_email,
            "user_name": request.user_name,
            "feedback_confirm_url": feedback_confirm,
            "feedback_deny_url": feedback_deny,
        }

        background_tasks.add_task(call_n8n_webhook, n8n_payload)
        return {"status": "notification_scheduled", "recipient": request.user_email, "urls_generated": True}
    except Exception as e:
        print(f"❌ Error in /notify: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def call_n8n_webhook(payload: dict):
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        print(f"n8n webhook response: {r.status_code}")
    except Exception as e:
        print(f"n8n webhook error: {e}")


# --- Endpoint /feedback : reçu depuis les liens dans les emails ---
@app.get('/feedback', response_class=HTMLResponse)
async def receive_feedback(
    currency: str,
    label: str,
    prediction_vol: float,
    prediction_dir: str,
    Open: float,
    High: float,
    Low: float,
    Close: float,
    Volume: float,
    RSI: float,
    ATR: float,
    VolumeChange: float,
    SMA_20: float,
    EMA_50: float,
    background_tasks: BackgroundTasks
):
    """
    Appelé depuis les liens dans les emails de feedback.
    Stocke le retour utilisateur dans prod_data.csv.
    Déclenche le réentraînement si seuil atteint.
    """
    try:
        prefix = currency.upper()
        columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']
        raw_values = [Open, High, Low, Close, Volume, RSI, ATR, VolumeChange, SMA_20, EMA_50]

        # Normaliser avec le scaler existant
        if prefix in models:
            scaled = models[prefix]['scaler'].transform([raw_values])[0].tolist()
        else:
            scaled = raw_values

        # Déduire la vraie direction selon le feedback
        if label == "confirm":
            true_dir = 1 if prediction_dir == "up" else 0
        else:
            true_dir = 0 if prediction_dir == "up" else 1

        row = dict(zip(columns, scaled))
        row['target_vol'] = prediction_vol
        row['target_dir'] = true_dir
        row['currency'] = prefix

        # Écriture dans prod_data.csv
        file_exists = os.path.exists(PROD_DATA_PATH) and os.path.getsize(PROD_DATA_PATH) > 0
        with open(PROD_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        # Compter les lignes pour le trigger de réentraînement
        with open(PROD_DATA_PATH, 'r') as f:
            line_count = max(0, sum(1 for _ in f) - 1)

        print(f"📝 Feedback saved [{label}] for {prefix}. Total prod rows: {line_count}")

        action_color = "#4CAF50" if label == "confirm" else "#f44336"
        action_text = "✅ Prédiction confirmée" if label == "confirm" else "❌ Prédiction corrigée"

        html = f"""
        <html>
        <head>
          <style>
            body {{ font-family: Arial, sans-serif; background: #f0f4ff; display: flex;
                   justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 15px;
                    text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 500px; }}
            h1 {{ color: {action_color}; }}
            .logo {{ font-size: 1.8em; font-weight: bold; color: #667eea; margin-bottom: 20px; }}
            .btn {{ display: inline-block; padding: 12px 25px; background: #667eea; color: white;
                   text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: bold; }}
            .info {{ color: #555; background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 15px 0; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo">📈 InvestBuddy</div>
            <h1>{action_text}</h1>
            <div class="info">
              <p><strong>Crypto :</strong> {currency}</p>
              <p><strong>Direction prédite :</strong> {prediction_dir}</p>
              <p><strong>Volatilité :</strong> {prediction_vol:.6f}</p>
            </div>
            <p style="color: #888;">Votre retour aide notre IA à s'améliorer. Merci ! 🙏</p>
            <a href="http://localhost:5173" class="btn">Retour sur InvestBuddy</a>
          </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Réentraînement automatique ---
def retrain_models(currency: str):
    global models
    try:
        print(f"🔄 Starting retraining for {currency}...")
        ref_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'data', f'{currency}_ref_data.csv'))

        ref_df = pd.read_csv(ref_path)
        prod_df = pd.read_csv(PROD_DATA_PATH)

        if 'currency' in prod_df.columns:
            prod_df = prod_df[prod_df['currency'] == currency]
            prod_df = prod_df.drop(columns=['currency'], errors='ignore')

        combined = pd.concat([ref_df, prod_df], ignore_index=True).dropna()

        cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']
        X = combined[cols]
        y_vol = combined['target_vol']
        y_dir = combined['target_dir']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model_vol = RandomForestRegressor(n_estimators=100, random_state=42)
        model_dir = RandomForestRegressor(n_estimators=100, random_state=42)
        model_vol.fit(X_scaled, y_vol)
        model_dir.fit(X_scaled, y_dir)

        # Sauvegarde des artefacts
        prefix = f"{currency}_"
        joblib.dump(model_vol, os.path.join(BASE_DIR, 'artifacts', f'{prefix}model_volatility.pickle'))
        joblib.dump(model_dir, os.path.join(BASE_DIR, 'artifacts', f'{prefix}model_direction.pickle'))
        joblib.dump(scaler, os.path.join(BASE_DIR, 'artifacts', f'{prefix}scaler.pickle'))

        # Mise à jour des variables globales
        models[currency] = {'vol': model_vol, 'dir': model_dir, 'scaler': scaler}
        print(f"✅ Retraining done for {currency} on {len(combined)} samples")
    except Exception as e:
        print(f"❌ Retraining error for {currency}: {e}")

@app.post("/retrain/{currency}")
async def retrain_endpoint(currency: str, background_tasks: BackgroundTasks):

    prefix = currency.upper()

    if prefix not in ["BTCUSDT", "ETHUSDT"]:
        raise HTTPException(status_code=400, detail="Unsupported currency")

    background_tasks.add_task(retrain_models, prefix)

    return {
        "status": "retraining_started",
        "currency": prefix
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)