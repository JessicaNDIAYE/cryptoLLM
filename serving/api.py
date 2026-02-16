from fastapi import FastAPI
import joblib
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app =  FastAPI(title='crypto prediction API')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_vol_path = os.path.join(BASE_DIR, 'artifacts', 'model_volatility.pickle')
model_dir_path = os.path.join(BASE_DIR, 'artifacts', 'model_direction.pickle')
scaler_path = os.path.join(BASE_DIR, 'artifacts', 'scaler.pickle')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Autorise votre frontend
    allow_credentials=True,
    allow_methods=["*"], # Autorise tous les verbes (POST, etc.)
    allow_headers=["*"], # Autorise tous les headers
)

model_vol = joblib.load(model_vol_path)
model_dir = joblib.load(model_dir_path)
scaler = joblib.load(scaler_path)

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

@app.post('/predictBTC')
async def predict(data: CurrencyData):
    input_data = [[
        data.Open, data.High, data.Low, data.Close, data.Volume,
        data.RSI, data.ATR, data.VolumeChange, data.SMA_20, data.EMA_50
    ]]
    input_scaled = scaler.transform(input_data)
    vol_pred = model_vol.predict(input_scaled)[0]
    dir_pred = model_dir.predict(input_scaled)[0]
    
    return {
        "currency": "BTC",
        "prediction":{
            'volatility': float(vol_pred),
            'direction': "up" if dir_pred == 1 else "down",
        },
        "context": {
            "rsi": data.RSI,
            "atr": data.ATR,
            "sma_20": data.SMA_20,
            "ema_50": data.EMA_50
        },
        'message': f"Prediction : marché en {dir_pred} avec une volatilité de {vol_pred:.4f}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)