from fastapi import FastAPI
import joblib
from pydantic import BaseModel

app =  FastAPI('crypto prediction API')

model_vol = joblib.load('../artifacts/model_volatility.pickle')
model_dir = joblib.load('../artifacts/model_direction.pickle')
scaler = joblib.load('../artifacts/scaler.pickle')

class CurrencyData(BaseModel):
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
        'volatility': float(vol_pred),
        'direction': "up" if dir_pred == 1 else "down",
        'message': f"Prediction : marché en {dir_pred} avec une volatilité de {vol_pred:.4f}"
    }