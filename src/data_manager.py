"""
Gestion locale des données.
Le dashboard lit toujours depuis les fichiers CSV locaux.
Aucun appel API au chargement → Zéro plantage.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = "data"


def get_available_assets():
    """
    Retourne la liste des actifs disponibles localement
    """
    if not os.path.exists(DATA_DIR):
        return []
    
    assets = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            symbol = filename.replace(".csv", "")
            assets.append(symbol)
    
    return sorted(assets)


def load_asset(symbol, start_date=None, end_date=None):
    """
    Charge les données d'un actif depuis le fichier local
    """
    filepath = f"{DATA_DIR}/{symbol}.csv"
    
    if not os.path.exists(filepath):
        print(f"⚠️ {symbol} non trouvé dans {DATA_DIR}/")
        return None
    
    try:
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        
        # S'assurer qu'on a une colonne Close
        if "Close" not in df.columns:
            # Prendre la première colonne numérique
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df = df[[numeric_cols[0]]]
                df.columns = ["Close"]
            else:
                return None
        
        # Filtrer par date si demandé
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        return df["Close"]
        
    except Exception as e:
        print(f"❌ Erreur lecture {symbol}: {e}")
        return None


def load_portfolio(symbols, start_date=None, end_date=None):
    """
    Charge les données de plusieurs actifs
    """
    data = {}
    
    for symbol in symbols:
        series = load_asset(symbol, start_date, end_date)
        if series is not None and len(series) > 20:
            data[symbol] = series
    
    if not data:
        return None
    
    # Aligner les dates
    df = pd.DataFrame(data).dropna()
    return df


def load_returns(symbols, start_date=None, end_date=None):
    """
    Charge les rendements logarithmiques
    """
    prices = load_portfolio(symbols, start_date, end_date)
    
    if prices is None or prices.empty:
        return None
    
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns
