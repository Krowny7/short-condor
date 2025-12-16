from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
import math
import numpy as np


@dataclass
class BinomialModel:
    """
    CRR binomial model (European options).

    Parameters
    ----------
    S : spot
    K : strike
    r : risk-free annual rate (decimal)
    T : time to maturity in years
    sigma : annual volatility (decimal)
    N : number of binomial steps
    """
    S: float
    K: float
    r: float
    T: float
    sigma: float
    N: int

    def _params(self):
        if self.N <= 0:
            raise ValueError("N must be >= 1")
        if self.T <= 0:
            raise ValueError("T must be > 0")
        if self.S <= 0:
            raise ValueError("S must be > 0")
        if self.sigma < 0:
            raise ValueError("sigma must be >= 0")

        dt = self.T / self.N
        if dt <= 0:
            raise ValueError("Invalid dt")

        # CRR
        u = math.exp(self.sigma * math.sqrt(dt)) if self.sigma > 0 else 1.0
        d = 1.0 / u if u != 0 else 0.0

        disc = math.exp(-self.r * dt)
        a = math.exp(self.r * dt)

        if abs(u - d) < 1e-14:
            # sigma ~ 0, degenerate: set q=0.5
            q = 0.5
        else:
            q = (a - d) / (u - d)

        # Clamp to avoid tiny numeric issues
        q = max(0.0, min(1.0, q))

        return dt, u, d, q, disc

    def price_call(self) -> float:
        return self._price(option_type="call")

    def price_put(self) -> float:
        return self._price(option_type="put")

    def _price(self, option_type: str) -> float:
        dt, u, d, q, disc = self._params()

        # Terminal stock prices: S * u^j * d^(N-j)
        j = np.arange(self.N + 1)
        ST = self.S * (u ** j) * (d ** (self.N - j))

        if option_type == "call":
            values = np.maximum(ST - self.K, 0.0)
        else:
            values = np.maximum(self.K - ST, 0.0)

        # Backward induction
        for _ in range(self.N):
            values = disc * (q * values[1:] + (1.0 - q) * values[:-1])

        return float(values[0])

    def get_tree_data(self) -> Dict[str, Any]:
        """
        Return dict trees as triangular dicts {i:{j:value}}
        i = time level (0..N)
        j = node index (0..i) = number of up moves
        """
        try:
            dt, u, d, q, disc = self._params()
        except Exception as e:
            return {"error": str(e)}

        stock_prices: Dict[int, Dict[int, float]] = {}
        call_prices: Dict[int, Dict[int, float]] = {}
        put_prices: Dict[int, Dict[int, float]] = {}

        # Stock tree
        for i in range(self.N + 1):
            stock_prices[i] = {}
            for j in range(i + 1):
                stock_prices[i][j] = float(self.S * (u ** j) * (d ** (i - j)))

        # Terminal option values
        call_prices[self.N] = {}
        put_prices[self.N] = {}
        for j in range(self.N + 1):
            ST = stock_prices[self.N][j]
            call_prices[self.N][j] = float(max(ST - self.K, 0.0))
            put_prices[self.N][j] = float(max(self.K - ST, 0.0))

        # Backward
        for i in range(self.N - 1, -1, -1):
            call_prices[i] = {}
            put_prices[i] = {}
            for j in range(i + 1):
                call_up = call_prices[i + 1][j + 1]
                call_dn = call_prices[i + 1][j]
                put_up = put_prices[i + 1][j + 1]
                put_dn = put_prices[i + 1][j]

                call_prices[i][j] = float(disc * (q * call_up + (1.0 - q) * call_dn))
                put_prices[i][j] = float(disc * (q * put_up + (1.0 - q) * put_dn))

        return {
            "stock_prices": stock_prices,
            "call_prices": call_prices,
            "put_prices": put_prices,
        }


class MultiLegGreeksCalculator:
    """
    Compute strategy greeks by finite differences using BinomialModel.

    legs = list of dict:
      {"K": float, "type": "call"/"put", "sign": +1/-1}
    """

    def __init__(
        self,
        spot_range: np.ndarray,
        legs: List[dict],
        interest_rate: float,
        time_to_maturity: float,
        volatility: float,
        n_steps: int,
    ):
        self.spot_range = np.asarray(spot_range, dtype=float)
        self.legs = legs
        self.r = float(interest_rate)
        self.T = float(time_to_maturity)
        self.sigma = float(volatility)
        self.N = int(n_steps)

    def _price_strategy(self, S: float, T: float | None = None, sigma: float | None = None) -> float:
        T_ = self.T if T is None else float(T)
        sig_ = self.sigma if sigma is None else float(sigma)

        total = 0.0
        for leg in self.legs:
            m = BinomialModel(
                S=float(S),
                K=float(leg["K"]),
                r=self.r,
                T=T_,
                sigma=sig_,
                N=self.N,
            )
            if leg["type"] == "call":
                px = m.price_call()
            else:
                px = m.price_put()
            total += float(leg["sign"]) * px
        return float(total)

    def calculate_strategy_greeks(self) -> dict:
        # Prices along spot curve
        V = np.array([self._price_strategy(S) for S in self.spot_range], dtype=float)

        # Bumps
        # delta/gamma: bump in spot
        dS = np.maximum(0.01 * self.spot_range, 0.50)  # at least 0.50 currency unit
        V_up = np.array([self._price_strategy(S + bump) for S, bump in zip(self.spot_range, dS)], dtype=float)
        V_dn = np.array([self._price_strategy(max(1e-9, S - bump)) for S, bump in zip(self.spot_range, dS)], dtype=float)

        delta = (V_up - V_dn) / (2.0 * dS)
        gamma = (V_up - 2.0 * V + V_dn) / (dS ** 2)

        # Theta: 1 day
        dT = 1.0 / 365.0
        T_dn = max(1e-6, self.T - dT)
        V_Tdn = np.array([self._price_strategy(S, T=T_dn) for S in self.spot_range], dtype=float)
        theta = (V_Tdn - V) / dT  # dV/dT (approx). Often reported negative for decay; here it's derivative.

        # Vega: +1% vol bump (0.01 in decimal)
        dSig = 0.01
        V_sig_up = np.array([self._price_strategy(S, sigma=self.sigma + dSig) for S in self.spot_range], dtype=float)
        vega = (V_sig_up - V) / dSig

        return {"price": V, "delta": delta, "gamma": gamma, "theta": theta, "vega": vega}

    def get_greeks_at_spot(self, spot: float) -> dict:
        # Compute at single point with same method
        S = float(spot)
        V = self._price_strategy(S)

        dS = max(0.01 * S, 0.50)
        V_up = self._price_strategy(S + dS)
        V_dn = self._price_strategy(max(1e-9, S - dS))
        delta = (V_up - V_dn) / (2.0 * dS)
        gamma = (V_up - 2.0 * V + V_dn) / (dS ** 2)

        dT = 1.0 / 365.0
        T_dn = max(1e-6, self.T - dT)
        V_Tdn = self._price_strategy(S, T=T_dn)
        theta = (V_Tdn - V) / dT

        dSig = 0.01
        V_sig_up = self._price_strategy(S, sigma=self.sigma + dSig)
        vega = (V_sig_up - V) / dSig

        return {"price": V, "delta": delta, "gamma": gamma, "theta": theta, "vega": vega}
