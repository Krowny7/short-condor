from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import numpy as np

from binomial_engine import BinomialModel


@dataclass
class StrategyParams:
    S: float
    K1: float
    K2: float
    K3: float
    K4: float
    r: float
    T: float
    sigma: float
    N: int
    multiplier: int = 100


class ShortIronCondor:
    """
    Short Iron Condor (credit structure):
      +P(K1)  -P(K2)  -C(K3)  +C(K4)
    Profit zone (typical): between K2 and K3.
    """

    def __init__(self, params: StrategyParams):
        self.p = params
        if not (self.p.K1 < self.p.K2 < self.p.K3 < self.p.K4):
            raise ValueError("Strikes must satisfy K1 < K2 < K3 < K4")

    def legs_definition(self) -> List[Dict[str, Any]]:
        return [
            {"type": "put", "K": self.p.K1, "sign": +1, "label": "Long Put (wing)"},
            {"type": "put", "K": self.p.K2, "sign": -1, "label": "Short Put"},
            {"type": "call", "K": self.p.K3, "sign": -1, "label": "Short Call"},
            {"type": "call", "K": self.p.K4, "sign": +1, "label": "Long Call (wing)"},
        ]

    def price_leg(self, opt_type: str, K: float) -> float:
        m = BinomialModel(S=self.p.S, K=K, r=self.p.r, T=self.p.T, sigma=self.p.sigma, N=self.p.N)
        return m.price_call() if opt_type == "call" else m.price_put()

    def net_cost_per_share(self) -> float:
        """
        Sum(sign * option_price). Negative => credit received.
        """
        total = 0.0
        for leg in self.legs_definition():
            px = self.price_leg(leg["type"], leg["K"])
            total += float(leg["sign"]) * float(px)
        return float(total)

    def payoff_at_maturity(self, ST: float) -> float:
        """
        Payoff per share at expiry (ignores premium). This is the intrinsic payoff of legs.
        We will convert to P&L by adding the premium (net credit/debit) outside if needed.
        But in this project we consider P&L = intrinsic - net_cost (because net_cost is paid today).
        """
        ST = float(ST)
        K1, K2, K3, K4 = self.p.K1, self.p.K2, self.p.K3, self.p.K4

        # Intrinsics
        long_put_K1 = max(K1 - ST, 0.0)
        short_put_K2 = -max(K2 - ST, 0.0)
        short_call_K3 = -max(ST - K3, 0.0)
        long_call_K4 = max(ST - K4, 0.0)

        intrinsic = long_put_K1 + short_put_K2 + short_call_K3 + long_call_K4

        # P&L per share: intrinsic - net_cost (paid today; if net_cost negative, subtracting it adds credit)
        return float(intrinsic - self.net_cost_per_share())

    def payoff_curve(self, spot_array: np.ndarray) -> np.ndarray:
        spot_array = np.asarray(spot_array, dtype=float)
        return np.array([self.payoff_at_maturity(s) for s in spot_array], dtype=float)

    def _key_points_for_extrema(self) -> List[float]:
        mid = 0.5 * (self.p.K2 + self.p.K3)
        return [0.0, self.p.K1, self.p.K2, mid, self.p.K3, self.p.K4, self.p.K4 * 2.0]

    def max_profit_loss(self) -> Tuple[float, float]:
        pts = self._key_points_for_extrema()
        vals = [self.payoff_at_maturity(x) for x in pts]
        return float(max(vals)), float(min(vals))

    def breakevens(self) -> List[float]:
        """
        Generic numeric breakeven detection by scanning.
        """
        lo = max(1e-9, self.p.K1 * 0.5)
        hi = self.p.K4 * 1.5
        grid = np.linspace(lo, hi, 2000)
        y = np.array([self.payoff_at_maturity(x) for x in grid], dtype=float)

        bes = []
        for i in range(len(grid) - 1):
            y0, y1 = y[i], y[i + 1]
            if y0 == 0.0:
                bes.append(float(grid[i]))
            if y0 * y1 < 0:
                # linear interpolation
                x0, x1 = grid[i], grid[i + 1]
                xb = x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
                bes.append(float(xb))

        # clean duplicates
        bes_sorted = sorted(bes)
        cleaned = []
        for b in bes_sorted:
            if not cleaned or abs(b - cleaned[-1]) > 1e-2:
                cleaned.append(b)
        return cleaned

    def get_strategy_details(self) -> Dict[str, Any]:
        legs_rows = []
        for leg in self.legs_definition():
            px = self.price_leg(leg["type"], leg["K"])
            legs_rows.append(
                {
                    "Jambe": leg["label"],
                    "Type": leg["type"].upper(),
                    "Strike": float(leg["K"]),
                    "Position": "LONG" if leg["sign"] > 0 else "SHORT",
                    "Prix (€/action)": float(px),
                    "Signe": int(leg["sign"]),
                }
            )

        net = self.net_cost_per_share()
        max_p, max_l = self.max_profit_loss()
        bes = self.breakevens()

        return {
            "legs": legs_rows,
            "net_cost": float(net),
            "max_profit": float(max_p),
            "max_loss": float(max_l),
            "breakeven_points": bes,
        }


class StrategyExecutor:
    """
    Simple capital sizing:
    - Find max loss per contract
    - qty = floor(capital / max_loss_per_contract)
    """

    def __init__(self, capital: float):
        self.capital = float(capital)

    def max_quantity(self, strategy: ShortIronCondor) -> int:
        max_profit, max_loss = strategy.max_profit_loss()  # per share
        # max_loss is minimum (negative). Loss per share is abs(min)
        loss_per_share = abs(float(max_loss))
        loss_per_contract = loss_per_share * strategy.p.multiplier

        if loss_per_contract <= 0:
            return 0
        return int(self.capital // loss_per_contract)

    def get_execution_summary(self, strategy: ShortIronCondor, quantity: int) -> Dict[str, float]:
        max_profit, max_loss = strategy.max_profit_loss()
        loss_per_contract = abs(float(max_loss)) * strategy.p.multiplier
        total_max_loss = float(quantity) * loss_per_contract

        utilization = 0.0 if self.capital <= 0 else 100.0 * total_max_loss / self.capital
        remaining = self.capital - total_max_loss

        return {
            "total_max_loss": float(total_max_loss),
            "capital_utilization_pct": float(utilization),
            "capital_remaining": float(remaining),
        }
