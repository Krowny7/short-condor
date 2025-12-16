# strategy_manager.py
"""
Gestion de la stratégie : Short Iron Condor (credit) en binomial CRR.

Structure (K1 < K2 < K3 < K4) :
- Long Put  K1  (aile basse)
- Short Put K2  (put vendu)
- Short Call K3 (call vendu)
- Long Call K4  (aile haute)

Profit si S(T) reste dans la zone centrale [K2, K3].
Pertes limitées par les ailes.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from binomial_engine import BinomialModel


@dataclass
class StrategyParams:
    S: float
    K1: float
    K2: float
    K3: float
    K4: float
    r: float       # taux en décimal (ex: 0.025)
    T: float       # maturité en années
    sigma: float   # vol en décimal (ex: 0.30)
    N: int         # nb steps binomial
    multiplier: int = 100  # 100 actions par contrat (par défaut)


class ShortIronCondor:
    def __init__(self, params: StrategyParams):
        self.p = params
        self._validate()

    def _validate(self) -> None:
        p = self.p
        if not (p.K1 < p.K2 < p.K3 < p.K4):
            raise ValueError("Ordre des strikes invalide : il faut K1 < K2 < K3 < K4.")
        if p.S <= 0 or p.T <= 0 or p.sigma <= 0:
            raise ValueError("Paramètres invalides : S, T et sigma doivent être > 0.")
        if p.N < 2:
            raise ValueError("N doit être >= 2 pour un arbre binomial exploitable.")

    # ---------- Pricing (binomial CRR) ----------
    def _price_put(self, K: float) -> float:
        m = BinomialModel(S=self.p.S, K=float(K), r=self.p.r, T=self.p.T, sigma=self.p.sigma, N=self.p.N)
        return float(m.price_put())

    def _price_call(self, K: float) -> float:
        m = BinomialModel(S=self.p.S, K=float(K), r=self.p.r, T=self.p.T, sigma=self.p.sigma, N=self.p.N)
        return float(m.price_call())

    def legs_definition(self) -> List[Dict]:
        # sign = +1 long, -1 short
        return [
            {"type": "put",  "K": float(self.p.K1), "sign": +1, "label": "Long Put K1"},
            {"type": "put",  "K": float(self.p.K2), "sign": -1, "label": "Short Put K2"},
            {"type": "call", "K": float(self.p.K3), "sign": -1, "label": "Short Call K3"},
            {"type": "call", "K": float(self.p.K4), "sign": +1, "label": "Long Call K4"},
        ]

    def strategy_cost_per_share(self) -> float:
        """
        Coût initial par action (€/share) :
        somme(sign * prix_option)
        Si négatif => crédit reçu.
        """
        cost = 0.0
        for leg in self.legs_definition():
            if leg["type"] == "put":
                px = self._price_put(leg["K"])
            else:
                px = self._price_call(leg["K"])
            cost += leg["sign"] * px
        return float(cost)

    # ---------- Payoff ----------
    @staticmethod
    def _intrinsic_call(S: float, K: float) -> float:
        return max(S - K, 0.0)

    @staticmethod
    def _intrinsic_put(S: float, K: float) -> float:
        return max(K - S, 0.0)

    def payoff_at_maturity_per_share(self, ST: float) -> float:
        """
        Payoff à l’échéance par action (€/share),
        en incluant le cashflow initial (crédit/débit).
        """
        credit = -self.strategy_cost_per_share()  # si cost<0 => credit>0
        payoff = credit
        for leg in self.legs_definition():
            if leg["type"] == "put":
                intr = self._intrinsic_put(ST, leg["K"])
            else:
                intr = self._intrinsic_call(ST, leg["K"])
            payoff += leg["sign"] * intr
        return float(payoff)

    def payoff_curve_per_share(self, spot_range: np.ndarray) -> np.ndarray:
        return np.array([self.payoff_at_maturity_per_share(float(s)) for s in spot_range], dtype=float)

    # ---------- Infos / métriques ----------
    def breakevens(self) -> List[float]:
        """
        Approche numérique simple : on cherche les changements de signe du payoff.
        """
        p = self.p
        x = np.linspace(p.S * 0.5, p.S * 1.5, 2000)
        y = self.payoff_curve_per_share(x)
        sgn = np.sign(y)
        idx = np.where(np.diff(sgn) != 0)[0]
        bes: List[float] = []
        for i in idx:
            x0, x1 = x[i], x[i + 1]
            y0, y1 = y[i], y[i + 1]
            if (y1 - y0) == 0:
                continue
            # interpolation linéaire
            xb = x0 - y0 * (x1 - x0) / (y1 - y0)
            bes.append(float(xb))
        bes = sorted(list(set([round(b, 6) for b in bes])))
        return bes

    def get_strategy_details(self) -> Dict:
        """
        Détails "présentables" pour l'app.
        Tout est en €/share ici (l'app multiplie ensuite par multiplier).
        """
        p = self.p
        cost = self.strategy_cost_per_share()
        credit = -cost

        # payoff à l’échéance sur une grille large
        spot_grid = np.linspace(p.S * 0.5, p.S * 1.5, 2000)
        payoff_grid = self.payoff_curve_per_share(spot_grid)

        max_profit = float(np.max(payoff_grid))
        max_loss = float(np.min(payoff_grid))

        legs = []
        for leg in self.legs_definition():
            legs.append({
                "leg": leg["label"],
                "type": leg["type"],
                "strike": leg["K"],
                "position": "LONG" if leg["sign"] > 0 else "SHORT",
                "sign": leg["sign"],
            })

        return {
            "net_cost_per_share": float(cost),
            "net_credit_per_share": float(credit),
            "max_profit_per_share": float(max_profit),
            "max_loss_per_share": float(max_loss),
            "breakeven_points": self.breakevens(),
            "legs": legs,
        }


class StrategyExecutor:
    """
    Gestion du capital : combien de contrats max acheter/vendre selon la perte max.
    Ici on se base sur la perte max à l’échéance (approx).
    """

    def __init__(self, capital: float):
        self.capital = float(capital)

    def max_quantity(self, strategy: ShortIronCondor) -> int:
        d = strategy.get_strategy_details()
        max_loss_per_share = float(d["max_loss_per_share"])  # négatif
        if max_loss_per_share >= 0:
            return 0
        max_loss_per_contract = abs(max_loss_per_share) * strategy.p.multiplier
        if max_loss_per_contract <= 0:
            return 0
        return int(self.capital // max_loss_per_contract)

    def get_execution_summary(self, strategy: ShortIronCondor, qty: int) -> Dict:
        d = strategy.get_strategy_details()
        max_loss_per_contract = abs(float(d["max_loss_per_share"])) * strategy.p.multiplier
        total_max_loss = max_loss_per_contract * int(qty)
        util = 0.0 if self.capital <= 0 else (total_max_loss / self.capital) * 100.0
        remaining = self.capital - total_max_loss
        return {
            "qty": int(qty),
            "max_loss_per_contract": float(max_loss_per_contract),
            "total_max_loss": float(total_max_loss),
            "capital_utilization_pct": float(util),
            "capital_remaining": float(remaining),
        }
