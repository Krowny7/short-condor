"""
Module de données de marché réelles
Récupère les prix et volatilité historiques depuis Yahoo Finance
Compatible avec l'interface principale (app.py)
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple, Optional

# === Symboles disponibles avec noms lisibles ===
AVAILABLE_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "META": "Meta",
    "NVDA": "NVIDIA",
    "JPM": "JPMorgan",
    "JNJ": "Johnson & Johnson",
    "V": "Visa",
}


class MarketDataProvider:
    """Fournisseur de données de marché réelles via yfinance"""
    
    def __init__(self, symbol: str, period: str = "1y"):
        """
        Initialiser le fournisseur de données
        
        Args:
            symbol: Code de l'action (ex: "AAPL")
            period: Période historique ("1y", "6mo", "3mo", etc.)
        """
        self.symbol = symbol.upper()
        self.period = period
        self.data: Optional[pd.DataFrame] = None
        self.last_price: Optional[float] = None
        self.volatility: Optional[float] = None
        self.fetch_data()
    
    # === Récupération des données ===
    def fetch_data(self) -> bool:
        """Récupérer les données depuis Yahoo Finance"""
        try:
            self.data = yf.download(
                self.symbol,
                period=self.period,
                progress=False,
                auto_adjust=True
            )
            if self.data.empty:
                return False

            # Prix actuel (dernière clôture)
            last_close = self.data["Close"].iloc[-1]
            self.last_price = float(last_close.item() if hasattr(last_close, "item") else last_close)

            # Volatilité historique annualisée
            returns = self.data["Close"].pct_change().dropna()
            vol_value = returns.std() * np.sqrt(252)
            self.volatility = float(vol_value.item() if hasattr(vol_value, "item") else vol_value)

            return True
        except Exception as e:
            print(f"[Erreur] Récupération des données pour {self.symbol}: {str(e)}")
            return False

    # === Méthodes simples ===
    def get_price(self) -> Optional[float]:
        """Obtenir le prix actuel"""
        return self.last_price
    
    def get_volatility(self) -> Optional[float]:
        """Volatilité annualisée (décimal, ex: 0.25)"""
        return self.volatility
    
    def get_volatility_percent(self) -> Optional[float]:
        """Volatilité en % (ex: 25.0)"""
        return None if self.volatility is None else self.volatility * 100
    
    # === Résumé synthétique pour app.py ===
    def get_summary(self) -> dict:
        """Obtenir un résumé prêt pour affichage dans app.py"""
        return {
            "symbol": self.symbol,
            "name": AVAILABLE_STOCKS.get(self.symbol, self.symbol),
            "price": self.last_price,
            "volatility": self.volatility,             # décimal (0.23)
            "volatility_pct": self.get_volatility_percent(),  # pour l’affichage
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

    # === Historique des prix ===
    def get_price_history(self, days: int = 60) -> pd.DataFrame:
        """Historique des prix sur N jours"""
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        return self.data[["Close"]].tail(days).copy()

    # === Historique de la volatilité roulante ===
    def get_volatility_history(self, window: int = 30) -> pd.DataFrame:
        """Volatilité roulante annualisée"""
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        returns = self.data["Close"].pct_change()
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)

        return pd.DataFrame({
            "Date": rolling_vol.index,
            "Volatilité": rolling_vol.values
        }).tail(window * 2)


# === Fonctions utilitaires globales ===
def get_stock_price_and_volatility(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """Retourne (prix, volatilité en décimal)"""
    provider = MarketDataProvider(symbol, period="1y")
    if provider.data is None or provider.data.empty:
        return None, None
    return provider.get_price(), provider.get_volatility()


def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """Valider qu’un symbole est reconnu par Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        if "currentPrice" in info or "regularMarketPrice" in info:
            return True, f"{symbol.upper()} valide"
        else:
            return False, f"{symbol.upper()} non trouvé"
    except Exception as e:
        return False, f"Erreur: {str(e)}"


# === Test local ===
if __name__ == "__main__":
    print("=== Test MarketDataProvider ===\n")
    for symbol in ["AAPL", "TSLA", "MSFT"]:
        provider = MarketDataProvider(symbol)
        summary = provider.get_summary()
        print(f"{summary['name']} ({summary['symbol']}):")
        print(f"  Prix: ${summary['price']:.2f}")
        print(f"  Volatilité: {summary['volatility_pct']:.2f}%")
        print()
