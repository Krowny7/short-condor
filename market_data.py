"""
Module de données de marché réelles
Récupère les prix et volatilité historiques depuis Yahoo Finance
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Optional


# Symboles disponibles avec noms lisibles
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
        self.data = None
        self.last_price = None
        self.volatility = None
        self.fetch_data()
    
    def fetch_data(self) -> bool:
        """
        Récupérer les données depuis Yahoo Finance
        
        Returns:
            True si succès, False sinon
        """
        try:
            self.data = yf.download(self.symbol, period=self.period, progress=False, auto_adjust=True)
            
            if self.data.empty:
                return False
            
            # Prix actuel (dernière fermeture)
            self.last_price = float(self.data['Close'].iloc[-1].item() if hasattr(self.data['Close'].iloc[-1], 'item') else self.data['Close'].iloc[-1])
            
            # Volatilité historique annualisée
            returns = self.data['Close'].pct_change()
            vol_value = returns.std() * np.sqrt(252)
            self.volatility = float(vol_value.item() if hasattr(vol_value, 'item') else vol_value)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {self.symbol}: {str(e)}")
            return False
    
    def get_price(self) -> Optional[float]:
        """Obtenir le prix actuel de l'action"""
        return self.last_price
    
    def get_volatility(self) -> Optional[float]:
        """Obtenir la volatilité historique annualisée (0-1)"""
        return self.volatility
    
    def get_volatility_percent(self) -> Optional[float]:
        """Obtenir la volatilité en pourcentage (0-100)"""
        if self.volatility is None:
            return None
        return self.volatility * 100
    
    def get_summary(self) -> dict:
        """Obtenir un résumé des données"""
        return {
            "symbol": self.symbol,
            "name": AVAILABLE_STOCKS.get(self.symbol, self.symbol),
            "price": self.last_price,
            "volatility": self.volatility,
            "volatility_pct": self.get_volatility_percent(),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
    
    def get_price_history(self, days: int = 60) -> pd.DataFrame:
        """Obtenir l'historique des prix des N derniers jours"""
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        
        return self.data[['Close']].tail(days).copy()
    
    def get_volatility_history(self, window: int = 30) -> pd.DataFrame:
        """Calculer la volatilité roulante"""
        if self.data is None or self.data.empty:
            return pd.DataFrame()
        
        returns = self.data['Close'].pct_change()
        rolling_vol = returns.rolling(window).std() * np.sqrt(252)
        
        return pd.DataFrame({
            'Date': rolling_vol.index,
            'Volatilité': rolling_vol.values
        }).tail(window * 2)


def get_stock_price_and_volatility(symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Fonction simple pour obtenir prix et volatilité
    
    Args:
        symbol: Code de l'action
    
    Returns:
        Tuple (prix, volatilité en décimal)
    """
    provider = MarketDataProvider(symbol, period="1y")
    
    if provider.data is None or provider.data.empty:
        return None, None
    
    return provider.get_price(), provider.get_volatility()


def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Valider que le symbole existe et est accessible
    
    Args:
        symbol: Code de l'action
    
    Returns:
        Tuple (valide, message)
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Vérifier si on a des données valides
        if 'currentPrice' in info or 'regularMarketPrice' in info:
            return True, f"{symbol.upper()} valide"
        else:
            return False, f"{symbol.upper()} non trouvé"
    except Exception as e:
        return False, f"Erreur: {str(e)}"


if __name__ == "__main__":
    # Test du module
    print("=== Test MarketDataProvider ===\n")
    
    for symbol in ["AAPL", "TSLA", "MSFT"]:
        provider = MarketDataProvider(symbol)
        summary = provider.get_summary()
        
        print(f"{summary['name']} ({summary['symbol']}):")
        print(f"  Prix: €{summary['price']:.2f}")
        print(f"  Volatilité: {summary['volatility_pct']:.2f}%")
        print()
