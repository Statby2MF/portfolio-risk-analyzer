"""
Télécharge et stocke les données localement.
Une seule fois. Ensuite le dashboard lit depuis les fichiers locaux.

Usage:
    python download_data.py
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# Dossier de stockage
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Actifs à télécharger
CRYPTO_ASSETS = {
    "bitcoin": "BTC-USD",
    "ethereum": "ETH-USD",
    "solana": "SOL-USD",
    "cardano": "cardano",
}

# Actions US (via Yahoo Finance comme fallback)
STOCK_ASSETS = {
    "SPY": "S&P 500 ETF",
    "GLD": "Or",
    "TLT": "Obligations US",
    "QQQ": "Nasdaq 100",
}

# Actions BRVM (via le dépôt GitHub public)
BRVM_ASSETS = {
    "SNTS": "Sonatel",
    "ORAC": "Orange Côte d'Ivoire",
    "SGBC": "Société Générale CI",
    "ECOC": "Ecobank CI",
}


def download_crypto_coinpaprika(coin_id, filename, days=730):
    """
    Télécharge l'historique d'une crypto depuis CoinPaprika (gratuit, sans clé)
    """
    try:
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}/historical"
        params = {"start": start_date, "interval": "1d"}
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ Erreur HTTP {response.status_code}")
            return None
        
        data = response.json()
        
        if not data or not isinstance(data, list):
            print(f"   ❌ Pas de données")
            return None
        
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        df = df.set_index("date")[["price"]]
        df.columns = ["Close"]
        
        filepath = f"{DATA_DIR}/{filename}.csv"
        df.to_csv(filepath)
        print(f"   ✅ {len(df)} points sauvegardés dans {filepath}")
        return df
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def download_stock_yahoo(symbol, period="2y"):
    """
    Télécharge l'historique d'une action depuis Yahoo Finance
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            print(f"   ❌ Pas de données")
            return None
        
        df = data[["Close"]].copy()
        filepath = f"{DATA_DIR}/{symbol}.csv"
        df.to_csv(filepath)
        print(f"   ✅ {len(df)} points sauvegardés dans {filepath}")
        return df
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def download_brvm(ticker):
    """
    Télécharge l'historique BRVM depuis le dépôt GitHub public
    """
    try:
        url = f"https://raw.githubusercontent.com/Fredysessie/brvm-data-public/main/data/{ticker}/{ticker}.daily.csv"
        
        df = pd.read_csv(url)
        
        if df.empty:
            print(f"   ❌ Pas de données")
            return None
        
        # Renommer les colonnes si nécessaire
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        
        # Garder uniquement le Close
        if "Close" in df.columns:
            df = df[["Close"]]
        
        filepath = f"{DATA_DIR}/{ticker}.csv"
        df.to_csv(filepath)
        print(f"   ✅ {len(df)} points sauvegardés dans {filepath}")
        return df
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def main():
    print("=" * 60)
    print("📥 TÉLÉCHARGEMENT DES DONNÉES")
    print("=" * 60)
    
    # 1. Cryptos
print("\n₿ CRYPTOMONNAIES")
print("-" * 60)
crypto_map = {
    "btc-bitcoin": "BTC-USD",
    "eth-ethereum": "ETH-USD",
    "sol-solana": "SOL-USD",
    "ada-cardano": "ADA-USD",
}
for coin_id, filename in crypto_map.items():
    print(f"📥 {filename}...")
    download_crypto_coinpaprika(coin_id, filename)
    
    # 2. Actions US
    print("\n📈 ACTIONS US")
    print("-" * 60)
    for symbol, name in STOCK_ASSETS.items():
        print(f"📥 {symbol} ({name})...")
        download_stock_yahoo(symbol)
    
    # 3. Actions BRVM
    print("\n🌍 ACTIONS BRVM")
    print("-" * 60)
    for ticker, name in BRVM_ASSETS.items():
        print(f"📥 {ticker} ({name})...")
        download_brvm(ticker)
    
    print("\n" + "=" * 60)
    print("✅ TÉLÉCHARGEMENT TERMINÉ")
    print(f"📁 Données sauvegardées dans : {DATA_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
