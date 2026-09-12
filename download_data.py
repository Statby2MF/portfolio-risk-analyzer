"""
Télécharge et stocke les données localement.
Actions US + BRVM uniquement (pas de crypto = pas de problème d'API).

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

# Actions US (via Yahoo Finance)
STOCK_ASSETS = {
    "SPY": "S&P 500 ETF",
    "GLD": "Or",
    "TLT": "Obligations US",
    "QQQ": "Nasdaq 100",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
}

# Actions BRVM (via le dépôt GitHub public)
BRVM_ASSETS = {
    "SNTS": "Sonatel",
    "ORAC": "Orange Côte d'Ivoire",
    "SGBC": "Société Générale CI",
    "ECOC": "Ecobank CI",
    "BOAB": "Bank of Africa",
    "CBIBF": "Coris Bank",
}


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
        else:
            # Prendre la dernière colonne numérique
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                df = df[[numeric_cols[-1]]]
                df.columns = ["Close"]
        
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
    print("   (Actions US + BRVM uniquement)")
    print("=" * 60)
    
    # 1. Actions US
    print("\n📈 ACTIONS US")
    print("-" * 60)
    for symbol, name in STOCK_ASSETS.items():
        print(f"📥 {symbol} ({name})...")
        download_stock_yahoo(symbol)
    
    # 2. Actions BRVM
    print("\n🌍 ACTIONS BRVM")
    print("-" * 60)
    for ticker, name in BRVM_ASSETS.items():
        print(f"📥 {ticker} ({name})...")
        download_brvm(ticker)
    
    print("\n" + "=" * 60)
    print("✅ TÉLÉCHARGEMENT TERMINÉ")
    print(f"📁 Données sauvegardées dans : {DATA_DIR}/")
    print("=" * 60)
    
    # Afficher les fichiers téléchargés
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    print(f"\n📊 {len(files)} fichiers disponibles :")
    for f in sorted(files):
        print(f"   • {f}")


if __name__ == "__main__":
    main()
