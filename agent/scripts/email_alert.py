"""
Script de surveillance de la volatilité des cryptomonnaies et d'envoi d'alertes email.
Inclut des liens Human-in-the-Loop pour validation/correction des prédictions.
Exécution recommandée : Toutes les 6 heures (via entrypoint.sh ou cron).
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import pandas_ta as ta
from binance.client import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests
from dotenv import load_dotenv
import logging
from typing import List, Dict, Tuple

#  Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

#  Configuration 
VOLATILITY_THRESHOLD = float(os.getenv('VOLATILITY_THRESHOLD', '0.02'))

SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD'),
    'from_email': os.getenv('FROM_EMAIL', 'alerts@investbuddy.com')
}

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'investbuddy'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# URL de l'API de prédiction pour les liens de feedback
PREDICTION_API_URL = os.getenv('PREDICTION_API_URL', 'http://localhost:8080')

SYMBOL_MAPPING = {
    'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT',
    'XRP': 'XRPUSDT', 'ADA': 'ADAUSDT', 'DOGE': 'DOGEUSDT',
    'BNB': 'BNBUSDT', 'LINK': 'LINKUSDT', 'AVAX': 'AVAXUSDT'
}

# Base de données 

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        logger.error(f"Erreur DB: {e}")
        return None


def get_all_cryptocurrencies() -> List[str]:
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT nom FROM Money")
        cryptos = [row[0] for row in cursor.fetchall()]
        logger.info(f"{len(cryptos)} cryptomonnaies trouvées")
        return cryptos
    except Error as e:
        logger.error(f"Erreur récupération cryptos: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_users_subscribed_to_crypto(crypto_name: str) -> List[Tuple[str, str, str]]:
    connection = get_db_connection()
    if not connection:
        return []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT email, nom, prenom FROM User")
        users = cursor.fetchall()
        logger.info(f"{len(users)} utilisateurs trouvés pour {crypto_name}")
        return users
    except Error as e:
        logger.error(f"Erreur récupération utilisateurs: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Binance : calcul de volatilité 

def get_crypto_data(crypto_name: str) -> Tuple[float, float, Dict, Dict]:
    """
    Retourne (volatilité, changement de prix, détails, input_data pour /feedback)
    """
    symbol = SYMBOL_MAPPING.get(crypto_name)
    if not symbol:
        logger.warning(f"Pas de mapping Binance pour {crypto_name}")
        return 0.0, 0.0, {}, {}

    try:
        client = Client(tld='us')
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=60
        )

        df = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])

        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Indicateurs techniques
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['VolumeChange'] = df['Volume'].pct_change()
        df.dropna(inplace=True)

        last = df.iloc[-1]
        volatility = df['Close'].pct_change().std() * 100
        price_change = ((last['Close'] - df.iloc[0]['Close']) / df.iloc[0]['Close']) * 100

        details = {
            'symbol': symbol,
            'current_price': last['Close'],
            'high_24h': df['High'].max(),
            'low_24h': df['Low'].min(),
            'volume_24h': df['Volume'].sum(),
            'price_change': price_change
        }

        # Input data pour construire les liens de feedback
        input_data = {
            'Open': float(last['Open']),
            'High': float(last['High']),
            'Low': float(last['Low']),
            'Close': float(last['Close']),
            'Volume': float(last['Volume']),
            'RSI': float(last['RSI']),
            'ATR': float(last['ATR']),
            'VolumeChange': float(last['VolumeChange']),
            'SMA_20': float(last['SMA_20']),
            'EMA_50': float(last['EMA_50']),
        }

        logger.info(f"{crypto_name} - Volatilité: {volatility:.2f}%, Variation: {price_change:.2f}%")
        return volatility, price_change, details, input_data

    except Exception as e:
        logger.error(f"Erreur Binance pour {crypto_name}: {e}")
        return 0.0, 0.0, {}, {}


def get_prediction(currency: str, input_data: Dict) -> Dict:
    """Appelle l'API /predict pour obtenir la prédiction ML"""
    try:
        payload = {"currency": currency, **input_data}
        r = requests.post(f"{PREDICTION_API_URL}/predict", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json().get('prediction', {})
    except Exception as e:
        logger.error(f"Erreur appel /predict: {e}")
    return {}


# ── Envoi email avec liens Human-in-the-Loop ─────────────────────────

def send_alert_email(user_email: str, user_name: str, crypto_name: str,
                     volatility: float, price_change: float, details: Dict,
                     prediction: Dict, feedback_confirm_url: str, feedback_deny_url: str) -> bool:
    """
    Envoie un email d'alerte avec des boutons de validation Human-in-the-Loop.
    """
    if not all([SMTP_CONFIG['username'], SMTP_CONFIG['password']]):
        logger.error("Configuration SMTP incomplète. Vérifiez votre fichier .env")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"InvestBuddy - Alerte Volatilité sur {crypto_name}"
        msg['From'] = SMTP_CONFIG['from_email']
        msg['To'] = user_email

        direction = prediction.get('direction', 'N/A')
        vol_pred = prediction.get('volatility', volatility / 100)
        dir_color = "#4CAF50" if direction == "up" else "#f44336"
        dir_arrow = "UP" if direction == "up" else "DOWN"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: Arial, sans-serif; background: #f0f4ff; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white;
                         border-radius: 15px; overflow: hidden;
                         box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .alert-box {{ background: #fff3cd; border-left: 4px solid #ffc107;
                          padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .stats {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .stat-row {{ display: flex; justify-content: space-between;
                         padding: 8px 0; border-bottom: 1px solid #eee; }}
            .prediction-box {{ background: #e8f4fd; border-left: 4px solid #2196F3;
                               padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .feedback-section {{ text-align: center; background: #f0f7ff;
                                  padding: 25px; border-radius: 10px; margin: 25px 0; }}
            .btn-confirm {{ display: inline-block; padding: 14px 30px; background: #4CAF50;
                            color: white !important; text-decoration: none;
                            border-radius: 8px; margin: 8px; font-weight: bold; }}
            .btn-deny {{ display: inline-block; padding: 14px 30px; background: #f44336;
                         color: white !important; text-decoration: none;
                         border-radius: 8px; margin: 8px; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #888;
                       font-size: 0.85em; background: #f8f9fa; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>InvestBuddy</h1>
              <p>Alerte de volatilité détectée</p>
            </div>
            <div class="content">
              <p>Bonjour <strong>{user_name}</strong>,</p>
              <div class="alert-box">
                <strong>Forte variation détectée sur {crypto_name}</strong><br>
                Notre système de surveillance a identifié une activité inhabituelle.
              </div>

              <div class="stats">
                <h3>Statistiques de marché (24h)</h3>
                <div class="stat-row">
                  <span>Prix actuel</span>
                  <strong>${details.get('current_price', 0):,.2f}</strong>
                </div>
                <div class="stat-row">
                  <span>Plus haut 24h</span>
                  <strong>${details.get('high_24h', 0):,.2f}</strong>
                </div>
                <div class="stat-row">
                  <span>Plus bas 24h</span>
                  <strong>${details.get('low_24h', 0):,.2f}</strong>
                </div>
                <div class="stat-row">
                  <span>Variation de prix</span>
                  <strong style="color: {'#4CAF50' if price_change >= 0 else '#f44336'}">
                    {'+' if price_change >= 0 else ''}{price_change:.2f}%
                  </strong>
                </div>
                <div class="stat-row">
                  <span>Volatilité calculée</span>
                  <strong style="color: #f44336">{volatility:.4f}%</strong>
                </div>
              </div>

              <div class="prediction-box">
                <h3>Prédiction du modèle IA</h3>
                <div class="stat-row">
                  <span>Direction prédite</span>
                  <strong style="color: {dir_color}">{dir_arrow} {direction.upper()}</strong>
                </div>
                <div class="stat-row">
                  <span>Volatilité prédite</span>
                  <strong>{vol_pred:.6f}</strong>
                </div>
              </div>

              <div class="feedback-section">
                <h3>La prédiction vous semble-t-elle correcte ?</h3>
                <p>Votre retour améliore notre modèle d'IA. Cliquez sur un bouton ci-dessous :</p>
                <a href="{feedback_confirm_url}" class="btn-confirm">
                  Oui, je confirme la prédiction
                </a>
                <br>
                <a href="{feedback_deny_url}" class="btn-deny">
                  Non, je corrige la prédiction
                </a>
                <p style="font-size: 0.8em; color: #888; margin-top: 15px;">
                  En cliquant, vous aidez InvestBuddy à améliorer ses prédictions.
                </p>
              </div>
            </div>
            <div class="footer">
              <p>Cet email a été envoyé automatiquement par InvestBuddy.</p>
              <p>
                <a href="http://localhost:5173">Ouvrir InvestBuddy</a> |
                <a href="http://localhost:5173/settings">Gérer mes alertes</a>
              </p>
            </div>
          </div>
        </body>
        </html>
        """

        text_content = f"""
InvestBuddy - Alerte Volatilité sur {crypto_name}

Bonjour {user_name},

Forte variation détectée sur {crypto_name} :
- Prix actuel : ${details.get('current_price', 0):,.2f}
- Variation : {price_change:.2f}%
- Volatilité : {volatility:.4f}%
- Prédiction IA : {direction.upper()} (volatilité prédite : {vol_pred:.6f})

La prédiction vous semble-t-elle correcte ?
CONFIRMER : {feedback_confirm_url}
CORRIGER  : {feedback_deny_url}

Merci pour votre retour - InvestBuddy
        """

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)

        logger.info(f"Email envoyé à {user_email} pour {crypto_name}")
        return True

    except Exception as e:
        logger.error(f"Erreur envoi email à {user_email}: {e}")
        return False


# ── Fonction principale ────────────────────────────────────────────────

def check_volatility_and_alert():
    """
    1. Récupère toutes les cryptomonnaies de la DB
    2. Calcule leur volatilité via Binance
    3. Si seuil dépassé → appelle /predict → construit les liens feedback → envoie email
    """
    logger.info("=" * 60)
    logger.info("Début surveillance volatilité InvestBuddy")
    logger.info(f"Seuil de volatilité : {VOLATILITY_THRESHOLD}%")

    cryptos = get_all_cryptocurrencies()
    if not cryptos:
        logger.warning("Aucune crypto trouvée en base")
        return

    alerts_sent = 0
    alerts_failed = 0

    for crypto in cryptos:
        logger.info(f"\n── Analyse de {crypto} ──")
        volatility, price_change, details, input_data = get_crypto_data(crypto)

        if not input_data:
            continue

        if volatility > VOLATILITY_THRESHOLD:
            logger.warning(f"{crypto} - Volatilité critique : {volatility:.4f}%")

            # Obtenir la prédiction ML
            symbol = SYMBOL_MAPPING.get(crypto, crypto + 'USDT')
            prediction = get_prediction(symbol, input_data)
            if not prediction:
                prediction = {'direction': 'unknown', 'volatility': volatility / 100}

            # Construire les liens de feedback
            vol_pred = prediction.get('volatility', volatility / 100)
            direc = prediction.get('direction', 'unknown')
            params = "&".join([f"{k}={v}" for k, v in input_data.items()])

            feedback_confirm_url = (
                f"{PREDICTION_API_URL}/feedback?currency={symbol}&label=confirm"
                f"&prediction_vol={vol_pred}&prediction_dir={direc}&{params}"
            )
            feedback_deny_url = (
                f"{PREDICTION_API_URL}/feedback?currency={symbol}&label=deny"
                f"&prediction_vol={vol_pred}&prediction_dir={direc}&{params}"
            )

            # Récupérer les utilisateurs et envoyer les alertes
            users = get_users_subscribed_to_crypto(crypto)
            for user_email, user_nom, user_prenom in users:
                user_name = f"{user_prenom} {user_nom}".strip() or user_email
                success = send_alert_email(
                    user_email=user_email,
                    user_name=user_name,
                    crypto_name=crypto,
                    volatility=volatility,
                    price_change=price_change,
                    details=details,
                    prediction=prediction,
                    feedback_confirm_url=feedback_confirm_url,
                    feedback_deny_url=feedback_deny_url
                )
                if success:
                    alerts_sent += 1
                else:
                    alerts_failed += 1
        else:
            logger.info(f"{crypto} - Volatilité normale : {volatility:.4f}%")

    logger.info("\n" + "=" * 60)
    logger.info(f"Alertes envoyées : {alerts_sent} | Échecs : {alerts_failed}")
    logger.info("=" * 60)


if __name__ == "__main__":
    check_volatility_and_alert()
