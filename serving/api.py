from fastapi import FastAPI, HTTPException
import joblib
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app =  FastAPI(title='crypto prediction API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Autorise votre frontend
    allow_credentials=True,
    allow_methods=["*"], # Autorise tous les verbes (POST, etc.)
    allow_headers=["*"], # Autorise tous les headers
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

@app.post('/predict')
async def predict(data: CurrencyData):
    prefix = data.currency.upper()
    model_vol_path = os.path.join(BASE_DIR, 'artifacts', f'{prefix}_model_volatility.pickle')
    model_dir_path = os.path.join(BASE_DIR, 'artifacts', f'{prefix}_model_direction.pickle')
    scaler_path = os.path.join(BASE_DIR, 'artifacts', f'{prefix}_scaler.pickle')
    
    try:
        # Chargement des modèles spécifiques
        model_vol = joblib.load(model_vol_path)
        model_dir = joblib.load(model_dir_path)
        scaler = joblib.load(scaler_path)

        input_data = [[
            data.Open, data.High, data.Low, data.Close, data.Volume,
            data.RSI, data.ATR, data.VolumeChange, data.SMA_20, data.EMA_50
        ]]
        
        input_scaled = scaler.transform(input_data)
        vol_pred = model_vol.predict(input_scaled)[0]
        dir_pred = model_dir.predict(input_scaled)[0]
        
        return {
            "currency": data.currency,
            "prediction": {
                'volatility': float(vol_pred),
                'direction': "up" if dir_pred == 1 else "down",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)