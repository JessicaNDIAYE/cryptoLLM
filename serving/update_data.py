from binance.client import Client
import pandas as pd
import pandas_ta as ta
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

def update_crypto_data():
    client = Client(tld = 'us')
    currencies = ['BTCUSDT', 'ETHUSDT']

    os.makedirs('artifacts', exist_ok=True)

    for currency in currencies:
        # Récupération des données historiques
        klines = client.get_historical_klines(currency, Client.KLINE_INTERVAL_6HOUR, "1 Jan, 2025")
        df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                     'Close time', 'Quote asset volume', 'Number of trades',
                                        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Conversion des types
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)

        # Calcul des indicateurs techniques
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['VolumeChange'] = df['Volume'].pct_change()
        df['Price_prediction'] = df['Close'].shift(-4)

        df['Target_Direction'] = (df['Price_prediction'] > df['Close']).astype(int)

        df['Log_Return'] = (df['Close'] / df['Close'].shift(1))

        df['volatility'] = df['Log_Return'].rolling(window=4).std()

        df['Target_Volatility'] = df['volatility'].shift(-4)

        df.dropna(inplace=True)

        colonnes = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']

        X = df[colonnes]
        y_vol = df['Target_Volatility']
        y_dir = df['Target_Direction']

        SS = StandardScaler()
        X_scaled = SS.fit_transform(X)
        model_vol = RandomForestRegressor(n_estimators=100, random_state=42)
        model_dir = RandomForestRegressor(n_estimators=100, random_state=42)

        model_vol.fit(X_scaled, y_vol)
        model_dir.fit(X_scaled, y_dir)

        ref_df = pd.DataFrame(X_scaled, columns=colonnes)
        ref_df['target_vol'] = y_vol.values
        ref_df['target_dir'] = y_dir.values
        ref_df.to_csv(f'data/{currency}_ref_data.csv', index=False)

        prefix = f"artifacts/{currency}_"
        joblib.dump(model_vol, f"{prefix}model_volatility.pickle")
        joblib.dump(model_dir, f"{prefix}model_direction.pickle")
        joblib.dump(SS, f"{prefix}scaler.pickle")

    print("Mise à jour terminée.")

if __name__ == "__main__":
    update_crypto_data()