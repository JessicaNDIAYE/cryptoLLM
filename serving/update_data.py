from sklearn.metrics import mean_absolute_error, accuracy_score

from binance.client import Client
import pandas as pd
import pandas_ta as ta
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

def update_crypto_data():
    client = Client(tld = 'us')
    currencies = ['BTCUSDT', 'ETHUSDT'] # , 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'SHIBUSDT', 'BNBUSDT','LINKUSDT', 'AVAXUSDT', 'TRXUSDT']

    os.makedirs('artifacts', exist_ok=True)

    for currency in currencies:
        # Récupération des données historiques
        klines = client.get_historical_klines(currency, Client.KLINE_INTERVAL_6HOUR, "1 Jan, 2023")
        df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                     'Close time', 'Quote asset volume', 'Number of trades',
                                        'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        
        # Conversion des types
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)

        # Calcul des indicateurs techniques
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['MACD'] = ta.macd(df['Close'])['MACD_12_26_9']
        bb = ta.bbands(df['Close'], length=20, std=2)
        upper_col = [c for c in bb.columns if c.startswith('BBU')][0]
        lower_col = [c for c in bb.columns if c.startswith('BBL')][0]

        df['BB_width'] = bb[upper_col] - bb[lower_col]
        for i in range(1, 4):
            df[f'Lag_Close_{i}'] = df['Close'].shift(i)

        #Targets
        df['Price_Next_24h'] = df['Close'].shift(-4)
        df['Target_Direction'] = (df['Price_Next_24h'] > df['Close']).astype(int)
        df['Log_Return'] = (df['Close'] / df['Close'].shift(1))
        df['volatility'] = df['Log_Return'].rolling(window=4).std()
        df['Target_Volatility'] = df['volatility'].shift(-4)

        df.dropna(inplace=True)

        colonnes = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'MACD', 'BB_width', 'Lag_Close_1']

        X = df[colonnes]

        # Split des données en train/test
        split = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_v_train, y_v_test = df['Target_Volatility'].iloc[:split], df['Target_Volatility'].iloc[split:]
        y_d_train, y_d_test = df['Target_Direction'].iloc[:split], df['Target_Direction'].iloc[split:]

        # Normalisation
        SS = StandardScaler()
        X_train_scaled = SS.fit_transform(X_train)
        X_test_scaled = SS.transform(X_test)

        # Entraînement des modèles
        model_vol = RandomForestRegressor(n_estimators=100, random_state=42)
        model_dir = RandomForestRegressor(n_estimators=100, random_state=42)
        model_vol.fit(X_train_scaled, y_v_train)
        model_dir.fit(X_train_scaled, y_d_train)

        v_pred = model_vol.predict(X_test_scaled)
        d_pred = (model_dir.predict(X_test_scaled) > 0.5).astype(int)
        
        print(f"📈 Performance {currency}:")
        print(f"   - MAE Volatilité : {mean_absolute_error(y_v_test, v_pred):.5f}")
        print(f"   - Accuracy Direction : {accuracy_score(y_d_test, d_pred)*100:.2f}%")

        df.to_csv(f'data/{currency}_ref_data.csv', index=False)

        prefix = f"artifacts/{currency}_"
        joblib.dump(model_vol, f"{prefix}model_volatility.pickle")
        joblib.dump(model_dir, f"{prefix}model_direction.pickle")
        joblib.dump(SS, f"{prefix}scaler.pickle")

    print("Mise à jour terminée.")

if __name__ == "__main__":
    update_crypto_data()