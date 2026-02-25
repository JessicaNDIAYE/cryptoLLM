from sklearn.metrics import mean_absolute_error, accuracy_score

from binance.client import Client
import pandas as pd
import pandas_ta as ta
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

def get_sentiment_features(csv_path, target_currency):
    """Charge et nettoie les news pour enrichir le Random Forest"""
    try:
        df_news = pd.read_csv(csv_path, low_memory=False)
        #Nettoyage des colonnes numériques
        for col in ['positive', 'negative', 'toxic', 'important']:
            if col in df_news.columns:
                df_news[col] = pd.to_numeric(df_news[col], errors='coerce').fillna(0)
        
        df_news['newsDatetime'] = pd.to_datetime(df_news['newsDatetime'], errors='coerce')
        df_news = df_news.dropna(subset=['newsDatetime'])
        
        # Filtrage par crypto
        target = target_currency.replace('USDT', '')
        df_news['currencies'] = df_news['currencies'].astype(str)
        mask = df_news['currencies'].str.contains(target, case=False, na=False)
        df_specific = df_news[mask].copy()
        
        if len(df_specific) < 5: df_specific = df_news.copy()

        df_specific['net_sentiment'] = df_specific['positive'] - df_specific['negative']
        
        # Agrégation par heure pour le merge
        return df_specific.groupby(df_specific['newsDatetime'].dt.floor('h')).agg({
            'net_sentiment': 'mean',
            'toxic': 'mean',
            'important': 'sum'
        }).reset_index().rename(columns={'newsDatetime': 'merge_time'})
    except Exception as e:
        print(f"⚠️ Erreur news: {e}. On continue sans news.")
        return pd.DataFrame()

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

        news_df = get_sentiment_features('../data/news_currencies_source_joinedResult/news_currencies_source_joinedResult.csv', currency)

        # Fusion des données de marché avec les features de sentiment
        if not news_df.empty:
            df['merge_key'] = pd.to_datetime(df['Open time'], unit='ms').astype('int64') // 10**9
            news_df['merge_key'] = pd.to_datetime(news_df['merge_time']).astype('int64') // 10**9

            df = df.sort_values('merge_key')
            news_df = news_df.sort_values('merge_key')

            # Fusion sur les timestamps (entiers)
            df = pd.merge_asof(
                df,
                news_df[['merge_key', 'net_sentiment', 'toxic', 'important']],
                on='merge_key', 
                direction='backward'
            )
        else:
            df['net_sentiment'], df['toxic'], df['important'] = 0, 0, 0
        
        df[['net_sentiment', 'toxic', 'important']] = df[['net_sentiment', 'toxic', 'important']].fillna(0)


        # Calcul des indicateurs techniques
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9'] if macd is not None else 0
        
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None:
            df['BB_width'] = bb.iloc[:, 2] - bb.iloc[:, 0]
        else:
            df['BB_width'] = 0
        df[f'Lag_Close_1'] = df['Close'].shift(1)

        #Targets
        df['Target_Direction'] = (df['Close'].shift(-4) > df['Close']).astype(int)
        df['volatility'] = df['Close'].pct_change().rolling(window=4).std()
        df['Target_Volatility'] = df['volatility'].shift(-4)

        df.dropna(inplace=True)

        colonnes = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'MACD', 'BB_width', 
                    'Lag_Close_1', 'net_sentiment', 'toxic', 'important']

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