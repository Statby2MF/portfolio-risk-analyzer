"""
Télécharge et stocke les données localement.
Toutes les actions BRVM + 50 actions US majeures.
"""
import os
import requests
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 50 ACTIONS US (Top capitalisation)
# ============================================================
US_STOCKS = {
    # Technologie
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "AMD": "AMD", "INTC": "Intel", "QCOM": "Qualcomm", "TXN": "Texas Instruments",
    "ORCL": "Oracle", "CRM": "Salesforce", "ADBE": "Adobe", "NFLX": "Netflix",
    "CSCO": "Cisco", "IBM": "IBM", "NOW": "ServiceNow", "PANW": "Palo Alto",
    # Finance
    "BRK-B": "Berkshire Hathaway", "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs",
    "MS": "Morgan Stanley", "BLK": "BlackRock", "AXP": "American Express",
    # Santé
    "LLY": "Eli Lilly", "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson",
    "ABBV": "AbbVie", "MRK": "Merck", "PFE": "Pfizer", "TMO": "Thermo Fisher",
    # Consommation
    "WMT": "Walmart", "COST": "Costco", "PG": "Procter & Gamble",
    "KO": "Coca-Cola", "PEP": "PepsiCo", "MCD": "McDonald's", "NKE": "Nike",
    # Énergie / Industrie
    "XOM": "Exxon Mobil", "CVX": "Chevron", "CAT": "Caterpillar", "BA": "Boeing",
    "GE": "General Electric", "HON": "Honeywell",
}

# ============================================================
# TOUTES LES ACTIONS BRVM
# ============================================================
BRVM_STOCKS = {
    "ABJC": "Servair Abidjan", "BICC": "BICI Côte d'Ivoire", "BNBC": "Bernabé",
    "BOAB": "Bank of Africa Bénin", "BOABF": "Bank of Africa Burkina",
    "BOAC": "Bank of Africa CI", "BOAM": "Bank of Africa Mali",
    "BOAN": "Bank of Africa Niger", "BOAS": "Bank of Africa Sénégal",
    "CABC": "Sicable CI", "CBIBF": "Coris Bank", "CFAC": "CFAO Motors CI",
    "CIEC": "CIE CI", "ECOC": "Ecobank CI", "ETIT": "Ecobank Transnational",
    "FTSC": "Filtisac", "NEIC": "NEI-CEDA", "ONTBF": "Onatel",
    "ORAC": "Orange CI", "ORGT": "Oragroup", "PALC": "Palm CI",
    "PRSC": "Prisca", "SAFC": "Safca", "SAPC": "SAPC", "SDCC": "Sodeci",
    "SDSC": "Africa Global Logistics", "SGBC": "Société Générale CI",
    "SICC": "Sicoc", "SIVC": "Sivom", "SLBC": "Solibra",
    "SMBC": "SMB CI", "SNTS": "Sonatel", "SOAC": "Sodefor",
    "SPHC": "Saph", "STAC": "Setao", "STBC": "Sitab",
    "TTLC": "TotalEnergies CI", "TTLS": "TotalEnergies Sénégal",
    "UNXC": "Uniwax", "UNLC": "Unilever CI", "NEIC": "NEI-CEDA",
    "CABO": "Cabo", "FTSC": "Filtisac", "ORGT": "Oragroup", "SAFC": "Safca",
    "STAC": "Setao", "SIVC": "Sivom",
}


def download_us_stock(symbol, period="5y"):
    """Télécharge une action US depuis Yahoo Finance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            return None
        
        df = data[["Close"]].copy()
        # Ajouter le suffixe US pour distinguer
        filepath = f"{DATA_DIR}/US_{symbol}.csv"
        df.to_csv(filepath)
        return df
    except Exception as e:
        print(f"   ❌ {symbol}: {e}")
        return None


def download_brvm_stock(ticker):
    """Télécharge une action BRVM depuis le dépôt GitHub automatique"""
    try:
        url = f"https://raw.githubusercontent.com/Fredysessie/brvm-data-public/main/data/{ticker}/{ticker}.daily.csv"
        
        df = pd.read_csv(url)
        
        if df.empty:
            return None
        
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        
        if "Close" in df.columns:
            df = df[["Close"]]
        else:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                df = df[[numeric_cols[-1]]]
                df.columns = ["Close"]
        
        # Ajouter le suffixe BRVM pour distinguer
        filepath = f"{DATA_DIR}/BRVM_{ticker}.csv"
        df.to_csv(filepath)
        return df
    except Exception as e:
        print(f"   ❌ {ticker}: {e}")
        return None


def main():
    print("=" * 60)
    print("📥 TÉLÉCHARGEMENT DES DONNÉES")
    print("   50 actions US + Toutes les actions BRVM")
    print("=" * 60)
    
    # 1. Actions US
    print("\n📈 ACTIONS US (Top 50)")
    print("-" * 60)
    success_us = 0
    for symbol, name in US_STOCKS.items():
        print(f"📥 {symbol} ({name})...")
        if download_us_stock(symbol):
            success_us += 1
    print(f"\n✅ {success_us}/{len(US_STOCKS)} actions US téléchargées")
    
    # 2. Actions BRVM
    print("\n🌍 ACTIONS BRVM (Toutes)")
    print("-" * 60)
    success_brvm = 0
    for ticker, name in BRVM_STOCKS.items():
        print(f"📥 {ticker} ({name})...")
        if download_brvm_stock(ticker):
            success_brvm += 1
    print(f"\n✅ {success_brvm}/{len(BRVM_STOCKS)} actions BRVM téléchargées")
    
    print("\n" + "=" * 60)
    print("✅ TÉLÉCHARGEMENT TERMINÉ")
    print("=" * 60)
    
    # Compter les fichiers
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    us_files = [f for f in files if f.startswith('US_')]
    brvm_files = [f for f in files if f.startswith('BRVM_')]
    print(f"\n📊 {len(us_files)} fichiers US")
    print(f"📊 {len(brvm_files)} fichiers BRVM")


if __name__ == "__main__":
    main()
