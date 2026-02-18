"""
Script de surveillance de la volatilité des cryptomonnaies et d'envoi d'alertes email
Exécution recommandée : Toutes les 6 heures (via cron/tâche planifiée)
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_alerts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# ==================== CONFIGURATION ====================
# Seuil de volatilité négative (en %) - à ajuster selon vos besoins
VOLATILITY_THRESHOLD = -5.0  # -5% de volatilité

# Configuration email (à configurer dans votre .env)
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),  # Par défaut Gmail
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD'),
    'from_email': os.getenv('FROM_EMAIL', 'alerts@investbuddy.com')
}

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'investbuddy'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Mapping des symboles Binance vers les noms dans votre DB
SYMBOL_MAPPING = {
    'BTC': 'BTCUSDT',
    'ETH': 'ETHUSDT',
    'SOL': 'SOLUSDT',
    'XRP': 'XRPUSDT',
    'ADA': 'ADAUSDT',
    'DOGE': 'DOGEUSDT',
    'USDT': 'USDTUSDT',
    'SHIB': 'SHIBUSDT',
    'LINK': 'LINKUSDT',
    'BNB': 'BNBUSDT',
    'TRX': 'TRXUSDT',
    'AVAX': 'AVAXUSDT',
    'USDC': 'USDCUSDT'
}

# ==================== FONCTIONS BASE DE DONNÉES ====================

def get_db_connection():
    """Établit une connexion à la base de données MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

def get_all_cryptocurrencies() -> List[str]:
    """Récupère la liste de toutes les cryptomonnaies dans la base de données"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT nom FROM Money")
        cryptos = [row[0] for row in cursor.fetchall()]
        logger.info(f"{len(cryptos)} cryptomonnaies trouvées dans la base")
        return cryptos
    except Error as e:
        logger.error(f"Erreur lors de la récupération des cryptomonnaies: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_users_subscribed_to_crypto(crypto_name: str) -> List[Tuple[str, str, str]]:
    """
    Récupère les utilisateurs abonnés à une cryptomonnaie spécifique
    Retourne une liste de tuples (email, nom, prenom)
    """
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        # Note: Adaptez cette requête selon votre schéma de base de données
        # Si vous avez une table de subscriptions, modifiez cette requête
        query = """
        SELECT DISTINCT u.email, u.nom, u.prenom 
        FROM User u
        -- Si vous avez une table de subscriptions, décommentez les lignes suivantes:
        -- JOIN Subscription s ON u.email = s.user_email
        -- JOIN Money m ON s.money_id = m.id
        -- WHERE m.nom = %s
        """
        
        # Version simplifiée - tous les utilisateurs reçoivent les alertes
        # À remplacer par la version avec subscriptions quand elle existera
        query = "SELECT email, nom, prenom FROM User"
        
        cursor.execute(query, (crypto_name,))
        users = cursor.fetchall()
        logger.info(f"{len(users)} utilisateurs trouvés pour {crypto_name}")
        return users
    except Error as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ==================== FONCTIONS BINANCE ====================

def get_crypto_volatility(crypto_name: str) -> Tuple[float, float, Dict]:
    """
    Calcule la volatilité d'une cryptomonnaie
    Retourne: (volatilité actuelle, changement de prix, données détaillées)
    """
    symbol = SYMBOL_MAPPING.get(crypto_name)
    if not symbol:
        logger.warning(f"Pas de mapping Binance pour {crypto_name}")
        return 0.0, 0.0, {}
    
    try:
        # Connexion au client Binance
        client = Client(tld='us')
        
        # Récupération des données des dernières 24h
        klines = client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=24  # 24 heures de données
        )
        
        # Conversion en DataFrame
        data = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])
        
        # Nettoyage
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Calcul des rendements logarithmiques
        data['Log_Return'] = (data['Close'] / data['Close'].shift(1))
        
        # Calcul de la volatilité (écart-type des rendements)
        volatility = data['Log_Return'].std() * 100  # Conversion en pourcentage
        
        # Changement de prix sur 24h
        price_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
        
        # Prix actuel
        current_price = data['Close'].iloc[-1]
        
        # Données détaillées pour l'email
        details = {
            'symbol': symbol,
            'current_price': current_price,
            'high_24h': data['High'].max(),
            'low_24h': data['Low'].min(),
            'volume_24h': data['Volume'].sum(),
            'price_change': price_change
        }
        
        logger.info(f"{crypto_name} - Volatilité: {volatility:.2f}%, Variation: {price_change:.2f}%")
        
        return volatility, price_change, details
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul de volatilité pour {crypto_name}: {e}")
        return 0.0, 0.0, {}

# ==================== FONCTIONS EMAIL ====================

def send_alert_email(user_email: str, user_name: str, crypto_name: str, 
                     volatility: float, price_change: float, details: Dict):
    """
    Envoie un email d'alerte à un utilisateur
    """
    if not all([SMTP_CONFIG['username'], SMTP_CONFIG['password']]):
        logger.error("Configuration email incomplète. Vérifiez votre fichier .env")
        return False
    
    try:
        # Création du message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Alerte InvestBuddy: Forte variation sur {crypto_name}"
        msg['From'] = SMTP_CONFIG['from_email']
        msg['To'] = user_email
        
        # Construction du contenu HTML
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert {{ background: #fee; border-left: 4px solid #f44336; padding: 15px; margin: 20px 0; }}
                .stats {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .stat-item {{ display: flex; justify-content: space-between; margin: 10px 0; 
                             border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .negative {{ color: #f44336; font-weight: bold; }}
                .positive {{ color: #4CAF50; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #667eea;
                          color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>InvestBuddy - Alerte Volatilité</h1>
                </div>
                <div class="content">
                    <h2>Bonjour {user_name},</h2>
                    
                    <p>Notre système de surveillance a détecté une variation significative sur <strong>{crypto_name}</strong> qui pourrait vous intéresser.</p>
                    
                    <div class="alert">
                        <h3 style="margin-top: 0;">🚨 Alerte de volatilité</h3>
                        <p>La volatilité de <strong>{crypto_name}</strong> a atteint <span class="negative">{volatility:.2f}%</span> 
                           avec une variation de prix de <span class="negative">{price_change:.2f}%</span>.</p>
                    </div>
                    
                    <div class="stats">
                        <h3>📊 Statistiques 24h</h3>
                        <div class="stat-item">
                            <span>Prix actuel:</span>
                            <strong>${details.get('current_price', 0):,.2f}</strong>
                        </div>
                        <div class="stat-item">
                            <span>Plus haut 24h:</span>
                            <strong>${details.get('high_24h', 0):,.2f}</strong>
                        </div>
                        <div class="stat-item">
                            <span>Plus bas 24h:</span>
                            <strong>${details.get('low_24h', 0):,.2f}</strong>
                        </div>
                        <div class="stat-item">
                            <span>Volume 24h:</span>
                            <strong>${details.get('volume_24h', 0):,.0f}</strong>
                        </div>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="http://localhost:5173/trading" class="button">Voir sur InvestBuddy</a>
                    </p>
                    
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement par InvestBuddy.</p>
                        <p>Pour gérer vos alertes, rendez-vous dans vos <a href="http://localhost:5173/settings">paramètres</a>.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Version texte simple
        text_content = f"""
        InvestBuddy - Alerte Volatilité
        
        Bonjour {user_name},
        
        Notre système a détecté une variation significative sur {crypto_name}:
        
        Volatilité: {volatility:.2f}%
        Variation de prix: {price_change:.2f}%
        Prix actuel: ${details.get('current_price', 0):,.2f}
        
        Rendez-vous sur InvestBuddy pour plus de détails.
        
        Cet email a été envoyé automatiquement.
        """
        
        # Attacher les versions texte et HTML
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Envoi de l'email
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
        
        logger.info(f"Email envoyé avec succès à {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email à {user_email}: {e}")
        return False

# ==================== FONCTION PRINCIPALE ====================

def check_volatility_and_alert():
    """
    Fonction principale qui :
    1. Récupère toutes les cryptomonnaies
    2. Calcule leur volatilité
    3. Vérifie si le seuil négatif est dépassé
    4. Envoie des alertes aux utilisateurs concernés
    """
    logger.info("=" * 50)
    logger.info("Début de la surveillance de volatilité")
    logger.info(f"Seuil de volatilité négative: {VOLATILITY_THRESHOLD}%")
    
    # Récupération de toutes les cryptomonnaies
    cryptos = get_all_cryptocurrencies()
    
    if not cryptos:
        logger.warning("Aucune cryptomonnaie trouvée dans la base")
        return
    
    alerts_sent = 0
    alerts_failed = 0
    
    # Analyse de chaque cryptomonnaie
    for crypto in cryptos:
        logger.info(f"\nAnalyse de {crypto}...")
        
        # Calcul de la volatilité
        volatility, price_change, details = get_crypto_volatility(crypto)
        
        # Vérification du seuil (volatilité négative)
        if volatility < VOLATILITY_THRESHOLD:
            logger.warning(f"⚠️ {crypto} - Volatilité critique: {volatility:.2f}%")
            
            # Récupération des utilisateurs abonnés
            users = get_users_subscribed_to_crypto(crypto)
            
            if not users:
                logger.info(f"Aucun utilisateur abonné à {crypto}")
                continue
            
            # Envoi des alertes
            for user_email, user_nom, user_prenom in users:
                user_name = f"{user_prenom} {user_nom}"
                success = send_alert_email(
                    user_email=user_email,
                    user_name=user_name,
                    crypto_name=crypto,
                    volatility=volatility,
                    price_change=price_change,
                    details=details
                )
                
                if success:
                    alerts_sent += 1
                else:
                    alerts_failed += 1
                    
        else:
            logger.info(f"✅ {crypto} - Volatilité normale: {volatility:.2f}%")
    
    # Résumé
    logger.info("\n" + "=" * 50)
    logger.info("RÉSUMÉ DE L'EXÉCUTION")
    logger.info(f"Cryptomonnaies analysées: {len(cryptos)}")
    logger.info(f"Alertes envoyées avec succès: {alerts_sent}")
    logger.info(f"Échecs d'envoi: {alerts_failed}")
    logger.info("=" * 50)

# ==================== CONFIGURATION .ENV ====================

def create_env_template():
    """
    Crée un template .env pour la configuration
    """
    template = """
# Configuration de la base de données
DB_HOST=localhost
DB_NAME=investbuddy
DB_USER=root
DB_PASSWORD=votre_mot_de_passe

# Configuration email (Gmail exemple)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
FROM_EMAIL=alerts@investbuddy.com

# Seuil de volatilité (optionnel, défaut = -5.0)
VOLATILITY_THRESHOLD=-5.0
"""
    
    if not os.path.exists('.env'):
        with open('.env.example', 'w') as f:
            f.write(template)
        logger.info("Fichier .env.example créé. Renommez-le en .env et configurez-le.")

# ==================== POINT D'ENTRÉE ====================

if __name__ == "__main__":
    # Création du template .env si nécessaire
    create_env_template()
    
    # Exécution de la surveillance
    check_volatility_and_alert()