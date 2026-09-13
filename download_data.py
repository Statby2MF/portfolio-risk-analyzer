"""
Télécharge et stocke les données localement.
Actions US (5 ans) + Toutes les actions BRVM (historique complet).
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# 50 ACTIONS US
# ============================================================
US_STOCKS = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "GOOGL": "Alphabet",
    "AMZN": "Amazon", "META": "Meta", "TSLA": "Tesla", "AVGO": "Broadcom",
    "AMD": "AMD", "INTC": "Intel", "QCOM": "Qualcomm", "TXN": "Texas Instruments",
    "ORCL": "Oracle", "CRM": "Salesforce", "ADBE": "Adobe", "NFLX": "Netflix",
    "CSCO": "Cisco", "IBM": "IBM", "NOW": "ServiceNow", "PANW": "Palo Alto",
    "BRK-B": "Berkshire Hathaway", "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs",
    "MS": "Morgan Stanley", "BLK": "BlackRock", "AXP": "American Express",
    "LLY": "Eli Lilly", "UNH": "UnitedHealth", "JNJ": "Johnson & Johnson",
    "ABBV": "AbbVie", "MRK": "Merck", "PFE": "Pfizer", "TMO": "Thermo Fisher",
    "WMT": "Walmart", "COST": "Costco", "PG": "Procter & Gamble",
    "KO": "Coca-Cola", "PEP": "PepsiCo", "MCD": "McDonald's", "NKE": "Nike",
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
    "UNXC": "Uniwax", "UNLC": "Unilever CI",
    "CABO": "Cabo", "ORGT": "Oragroup",
}


def download_us_stock(symbol, period="5y"):
    """
    Télécharge une action US sur 5 ans depuis Yahoo Finance
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            return None
        
        df = data[["Close"]].copy()
        
        # S'assurer que l'index est bien un DatetimeIndex
        df.index = pd.to_datetime(df.index, utc=True)
        df.index = df.index.tz_localize(None)
        df.index.name = "Date"
        
        # Convertir les prix en numérique
        df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
        df = df.dropna()
        
        filepath = f"{DATA_DIR}/US_{symbol}.csv"
        df.to_csv(filepath)
        return df
    except Exception as e:
        print(f"   ⚠️ {symbol}: {e}")
        return None


def download_brvm_stock(ticker):
    """
    Télécharge une action BRVM (historique complet disponible)
    """
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
        
        filepath = f"{DATA_DIR}/BRVM_{ticker}.csv"
        df.to_csv(filepath)
        return df
    except Exception as e:
        return None


def analyze_data_quality():
    """
    Analyse la qualité des données téléchargées
    """
    print("\n" + "=" * 60)
    print("📊 ANALYSE DE LA QUALITÉ DES DONNÉES")
    print("=" * 60)
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    if not files:
        print("❌ Aucune donnée")
        return
    
    stats = []
    for filename in files:
        filepath = f"{DATA_DIR}/{filename}"
        try:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            
            if len(df) < 2:
                continue
            
            # Convertir en numérique
            if "Close" in df.columns:
                prices = pd.to_numeric(df["Close"], errors='coerce').dropna()
            else:
                prices = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna()
            
            if len(prices) < 10:
                continue
            
            debut = prices.index[0].strftime('%Y-%m-%d')
            fin = prices.index[-1].strftime('%Y-%m-%d')
            nb_points = len(prices)
            annees = (prices.index[-1] - prices.index[0]).days / 365.25
            
            stats.append({
                "Fichier": filename.replace('.csv', ''),
                "Points": nb_points,
                "Début": debut,
                "Fin": fin,
                "Années": round(annees, 1),
            })
        except:
            continue
    
    if not stats:
        print("❌ Aucune donnée valide")
        return
    
    df_stats = pd.DataFrame(stats).sort_values("Années", ascending=False)
    
    print(f"\n📈 {len(df_stats)} actifs avec données valides")
    print("-" * 60)
    
    # Top 10 par durée
    print("\n🏆 Top 10 (plus longue historique) :")
    for _, row in df_stats.head(10).iterrows():
        print(f"   • {row['Fichier']:20s} | {row['Points']:5d} points | {row['Années']:.1f} ans | {row['Début']} → {row['Fin']}")
    
    # Statistiques globales
    print(f"\n📊 Statistiques globales :")
    print(f"   • Durée moyenne : {df_stats['Années'].mean():.1f} ans")
    print(f"   • Durée médiane : {df_stats['Années'].median():.1f} ans")
    print(f"   • Nombre de points moyen : {int(df_stats['Points'].mean())}")
    
    # Actifs avec plus de 3 ans
    long_history = df_stats[df_stats['Années'] >= 3]
    print(f"\n✅ {len(long_history)} actifs avec ≥ 3 ans d'historique")
    
    return df_stats


def main():
    print("=" * 60)
    print("📥 TÉLÉCHARGEMENT DES DONNÉES")
    print("   50 actions US (5 ans) + Toutes les actions BRVM")
    print("=" * 60)
    
    # 1. Actions US
    print("\n📈 ACTIONS US (5 ans)")
    print("-" * 60)
    success_us = 0
    for symbol, name in US_STOCKS.items():
        print(f"📥 {symbol} ({name})...")
        result = download_us_stock(symbol, period="5y")
        if result is not None:
            success_us += 1
    print(f"\n✅ {success_us}/{len(US_STOCKS)} actions US téléchargées")
    
    # 2. Actions BRVM
    print("\n🌍 ACTIONS BRVM (historique complet)")
    print("-" * 60)
    success_brvm = 0
    for ticker, name in BRVM_STOCKS.items():
        print(f"📥 {ticker} ({name})...")
        result = download_brvm_stock(ticker)
        if result is not None:
            success_brvm += 1
    print(f"\n✅ {success_brvm}/{len(BRVM_STOCKS)} actions BRVM téléchargées")
    
    # 3. Analyse qualité
    analyze_data_quality()
    
    print("\n" + "=" * 60)
    print("✅ TÉLÉCHARGEMENT TERMINÉ")
    print("=" * 60)


if __name__ == "__main__":
    main()
