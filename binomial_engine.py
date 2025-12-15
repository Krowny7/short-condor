"""
Module for Binomial Option Pricing using Cox-Ross-Rubinstein (CRR) Model
Uses numerical differentiation for Greeks calculation - NO scipy dependency
"""

import numpy as np
from typing import Dict, List


class BinomialModel:
    """
    Binomial option pricing model using Cox-Ross-Rubinstein approach.

    Parameters:
    -----------
    S : float
        Current spot price of the underlying asset
    K : float
        Strike price of the option
    r : float
        Risk-free interest rate (annual, decimal)
    T : float
        Time to maturity (in years)
    sigma : float
        Volatility (annual, decimal)
    N : int
        Number of steps in the binomial tree
    """

    def __init__(self, S: float, K: float, r: float, T: float, sigma: float, N: int):
        self.S = float(S)
        self.K = float(K)
        self.r = float(r)
        self.T = float(T)
        self.sigma = float(sigma)
        self.N = int(N)

        if self.S <= 0:
            raise ValueError("S must be > 0")
        if self.K <= 0:
            raise ValueError("K must be > 0")
        if self.T <= 0:
            raise ValueError("T must be > 0")
        if self.sigma <= 0:
            raise ValueError("sigma must be > 0")
        if self.N < 1:
            raise ValueError("N must be >= 1")

        self.dt = self.T / self.N

        # CRR parameters
        self.u = np.exp(self.sigma * np.sqrt(self.dt))
        self.d = 1.0 / self.u

        disc = np.exp(self.r * self.dt)
        self.q = (disc - self.d) / (self.u - self.d)

        # If parameters imply arbitrage, we fail clearly (better than silent wrong prices)
        if not (0.0 < self.q < 1.0):
            raise ValueError(
                f"Invalid risk-neutral probability q={self.q:.6f}. "
                f"Check inputs (r, sigma, T, N)."
            )

    def price_call(self) -> float:
        """Price a European call option using binomial tree."""
        option_values = np.zeros(self.N + 1)

        for j in range(self.N + 1):
            S_T = self.S * (self.u ** (self.N - j)) * (self.d ** j)
            option_values[j] = max(S_T - self.K, 0.0)

        df = np.exp(-self.r * self.dt)
        for i in range(self.N - 1, -1, -1):
            new_values = np.zeros(i + 1)
            for j in range(i + 1):
                new_values[j] = df * (self.q * option_values[j] + (1.0 - self.q) * option_values[j + 1])
            option_values = new_values

        return float(option_values[0])

    def price_put(self) -> float:
        """Price a European put option using binomial tree."""
        option_values = np.zeros(self.N + 1)

        for j in range(self.N + 1):
            S_T = self.S * (self.u ** (self.N - j)) * (self.d ** j)
            option_values[j] = max(self.K - S_T, 0.0)

        df = np.exp(-self.r * self.dt)
        for i in range(self.N - 1, -1, -1):
            new_values = np.zeros(i + 1)
            for j in range(i + 1):
                new_values[j] = df * (self.q * option_values[j] + (1.0 - self.q) * option_values[j + 1])
            option_values = new_values

        return float(option_values[0])

    def get_tree_data(self) -> Dict:
        """
        Get tree structure for visualization (useful for small N).
        Returns dict with stock prices + call/put prices at each node.
        """
        if self.N > 10:
            return {"error": "Tree too large for visualization (N > 10)"}

        tree_data = {
            "stock_prices": {},
            "call_prices": {},
            "put_prices": {},
            "parameters": {
                "S": self.S,
                "K": self.K,
                "r": self.r,
                "T": self.T,
                "sigma": self.sigma,
                "N": self.N,
                "u": self.u,
                "d": self.d,
                "q": self.q,
                "dt": self.dt,
            },
        }

        # Stock tree
        for i in range(self.N + 1):
            tree_data["stock_prices"][i] = {}
            for j in range(i + 1):
                tree_data["stock_prices"][i][j] = self.S * (self.u ** (i - j)) * (self.d ** j)

        df = np.exp(-self.r * self.dt)

        # Call tree
        call_last = {}
        for j in range(self.N + 1):
            call_last[j] = max(tree_data["stock_prices"][self.N][j] - self.K, 0.0)
        tree_data["call_prices"][self.N] = call_last

        for i in range(self.N - 1, -1, -1):
            tree_data["call_prices"][i] = {}
            for j in range(i + 1):
                tree_data["call_prices"][i][j] = df * (
                    self.q * tree_data["call_prices"][i + 1][j] +
                    (1.0 - self.q) * tree_data["call_prices"][i + 1][j + 1]
                )

        # Put tree
        put_last = {}
        for j in range(self.N + 1):
            put_last[j] = max(self.K - tree_data["stock_prices"][self.N][j], 0.0)
        tree_data["put_prices"][self.N] = put_last

        for i in range(self.N - 1, -1, -1):
            tree_data["put_prices"][i] = {}
            for j in range(i + 1):
                tree_data["put_prices"][i][j] = df * (
                    self.q * tree_data["put_prices"][i + 1][j] +
                    (1.0 - self.q) * tree_data["put_prices"][i + 1][j + 1]
                )

        return tree_data

    @staticmethod
    def price_range_at_maturity(
        S: float, K: float, r: float, T: float, sigma: float, N: int,
        spot_range: np.ndarray, option_type: str = "call"
    ) -> np.ndarray:
        """Intrinsic payoff at maturity (payoff diagram)."""
        if option_type.lower() == "call":
            return np.maximum(spot_range - K, 0.0)
        if option_type.lower() == "put":
            return np.maximum(K - spot_range, 0.0)
        raise ValueError("option_type must be 'call' or 'put'")

    def calculate_greeks(self, spot_range: np.ndarray, option_type: str = "call") -> Dict[str, np.ndarray]:
        """
        Greeks via finite differences (Delta, Gamma, Theta, Vega)
        - Delta/Gamma : central difference in spot
        - Theta : difference by removing 1 day
        - Vega : bump sigma

        Returns arrays aligned with spot_range.
        """
        option_type = option_type.lower().strip()
        if option_type not in ("call", "put"):
            raise ValueError("option_type must be 'call' or 'put'")

        greeks = {"delta": [], "gamma": [], "theta": [], "vega": []}

        for S in spot_range:
            S = float(S)
            if S <= 0:
                greeks["delta"].append(np.nan)
                greeks["gamma"].append(np.nan)
                greeks["theta"].append(np.nan)
                greeks["vega"].append(np.nan)
                continue

            # Base price
            base_model = BinomialModel(S, self.K, self.r, self.T, self.sigma, self.N)
            V0 = base_model.price_call() if option_type == "call" else base_model.price_put()

            # Spot bump (min absolute bump + relative bump)
            bump = max(0.5, 0.005 * S)
            S_up = S + bump
            S_dn = max(1e-6, S - bump)

            m_up = BinomialModel(S_up, self.K, self.r, self.T, self.sigma, self.N)
            V_up = m_up.price_call() if option_type == "call" else m_up.price_put()

            m_dn = BinomialModel(S_dn, self.K, self.r, self.T, self.sigma, self.N)
            V_dn = m_dn.price_call() if option_type == "call" else m_dn.price_put()

            delta = (V_up - V_dn) / (S_up - S_dn)
            gamma = (V_up - 2.0 * V0 + V_dn) / ((0.5 * (S_up - S_dn)) ** 2)

            # Theta : remove 1 day
            theta_bump = 1.0 / 365.0
            T_new = max(self.T - theta_bump, 1e-6)
            m_t = BinomialModel(S, self.K, self.r, T_new, self.sigma, self.N)
            V_t = m_t.price_call() if option_type == "call" else m_t.price_put()
            theta = (V_t - V0) / theta_bump  # per year, negative is usual for long options

            # Vega : bump sigma
            vol_bump = max(0.001, 0.005 * self.sigma)
            m_v = BinomialModel(S, self.K, self.r, self.T, self.sigma + vol_bump, self.N)
            V_v = m_v.price_call() if option_type == "call" else m_v.price_put()
            vega = (V_v - V0) / vol_bump  # per 1.00 vol (i.e. per +100%)

            greeks["delta"].append(delta)
            greeks["gamma"].append(gamma)
            greeks["theta"].append(theta)
            greeks["vega"].append(vega)

        return {k: np.array(v, dtype=float) for k, v in greeks.items()}


class MultiLegGreeksCalculator:
    """
    Greeks calculator for multi-leg strategies.
    Uses BinomialModel.calculate_greeks per leg, then sums with signs.
    """

    def __init__(
        self,
        spot_range: np.ndarray,
        legs: List[Dict],
        interest_rate: float,
        time_to_maturity: float,
        volatility: float,
        n_steps: int = 50,
    ):
        self.spot_range = np.array(spot_range, dtype=float)
        self.legs = legs
        self.r = float(interest_rate)
        self.T = float(time_to_maturity)
        self.sigma = float(volatility)
        self.N = int(n_steps)

        self.legs_greeks = self._compute_legs_greeks()

    def _compute_legs_greeks(self) -> List[Dict]:
        legs_greeks = []

        for leg in self.legs:
            K = float(leg["K"])
            option_type = leg["type"].lower().strip()
            sign = float(leg["sign"])

            # Dummy model (real prices computed inside calculate_greeks anyway)
            model = BinomialModel(
                S=float(self.spot_range[0]),
                K=K,
                r=self.r,
                T=self.T,
                sigma=self.sigma,
                N=self.N,
            )

            greeks = model.calculate_greeks(self.spot_range, option_type)

            legs_greeks.append({
                "delta": greeks["delta"],
                "gamma": greeks["gamma"],
                "theta": greeks["theta"],
                "vega": greeks["vega"],
                "sign": sign,
                "K": K,
                "type": option_type,
            })

        return legs_greeks

    def calculate_strategy_greeks(self) -> Dict[str, np.ndarray]:
        strategy_greeks = {
            "delta": np.zeros_like(self.spot_range, dtype=float),
            "gamma": np.zeros_like(self.spot_range, dtype=float),
            "theta": np.zeros_like(self.spot_range, dtype=float),
            "vega": np.zeros_like(self.spot_range, dtype=float),
        }

        for lg in self.legs_greeks:
            s = lg["sign"]
            strategy_greeks["delta"] += s * lg["delta"]
            strategy_greeks["gamma"] += s * lg["gamma"]
            strategy_greeks["theta"] += s * lg["theta"]
            strategy_greeks["vega"] += s * lg["vega"]

        return strategy_greeks

    def get_greeks_at_spot(self, spot: float) -> Dict[str, float]:
        spot = float(spot)
        idx = int(np.argmin(np.abs(self.spot_range - spot)))
        g = self.calculate_strategy_greeks()
        return {
            "delta": float(g["delta"][idx]),
            "gamma": float(g["gamma"][idx]),
            "theta": float(g["theta"][idx]),
            "vega": float(g["vega"][idx]),
        }
