from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd

# You need yfinance in requirements.txt for Streamlit Cloud
import yfinance as yf


AVAILABLE_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)",
    "TSLA": "Tesla",
    "META": "Meta",
    "NVDA": "NVIDIA",
}


@dataclass
class MarketDataProvider:
    ticker: str
    period: str = "1y"

    data: Optional[pd.DataFrame] = None

    def __post_init__(self):
        self.data = self._fetch()

    def _fetch(self) -> Optional[pd.DataFrame]:
        try:
            df = yf.download(self.ticker, period=self.period, auto_adjust=True, progress=False)
            if df is None or df.empty:
                return None
            return df
        except Exception:
            return None

    def get_summary(self) -> Dict[str, Any]:
        if self.data is None or self.data.empty:
            raise ValueError("No market data loaded")

        close = self.data["Close"].dropna()
        price = float(close.iloc[-1])

        # Realized volatility (annualized) from daily log returns
        rets = np.log(close / close.shift(1)).dropna()
        vol_daily = float(np.std(rets, ddof=1)) if len(rets) > 1 else 0.0
        vol_annual = vol_daily * np.sqrt(252.0)

        return {
            "price": price,
            "volatility": float(vol_annual),           # decimal
            "volatility_pct": float(vol_annual * 100), # %
        }
