"""
Condor Strategy Implementation (Binomial CRR only)
- Call Condor: +C(K1) -C(K2) -C(K3) +C(K4)
- Iron Condor: +P(K1) -P(K2) -C(K3) +C(K4)

Greeks computed in binomial via finite differences (MultiLegGreeksCalculator).
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

from binomial_engine import BinomialModel, MultiLegGreeksCalculator


class StrategyType(Enum):
    CALL_CONDOR = "call_condor"
    IRON_CONDOR = "iron_condor"


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
    strategy_type: StrategyType = StrategyType.CALL_CONDOR
    multiplier: int = 100


class Condor:
    """
    Condor en binomial (European options).
    """

    def __init__(self, params: StrategyParams):
        if not (params.K1 < params.K2 < params.K3 < params.K4):
            raise ValueError(
                f"Pour un condor : K1 < K2 < K3 < K4. "
                f"Reçu : K1={params.K1}, K2={params.K2}, K3={params.K3}, K4={params.K4}"
            )

        self.params = params

        if params.strategy_type == StrategyType.CALL_CONDOR:
            # +C(K1) -C(K2) -C(K3) +C(K4)
            self.legs: List[Tuple[str, float, int]] = [
                ("call", params.K1, +1),
                ("call", params.K2, -1),
                ("call", params.K3, -1),
                ("call", params.K4, +1),
            ]
        else:
            # +P(K1) -P(K2) -C(K3) +C(K4)
            self.legs = [
                ("put",  params.K1, +1),
                ("put",  params.K2, -1),
                ("call", params.K3, -1),
                ("call", params.K4, +1),
            ]

    def _leg_price(self, spot: float, option_type: str, strike: float) -> float:
        m = BinomialModel(
            S=float(spot),
            K=float(strike),
            r=float(self.params.r),
            T=float(self.params.T),
            sigma=float(self.params.sigma),
            N=int(self.params.N),
        )
        return m.price_call() if option_type == "call" else m.price_put()

    def price(self, spot: float = None) -> float:
        """
        Valeur aujourd'hui (PV) de la stratégie, par action.
        > 0 : débit payé
        < 0 : crédit reçu
        """
        s = float(self.params.S) if spot is None else float(spot)
        total = 0.0
        for opt_type, K, sign in self.legs:
            px = self._leg_price(s, opt_type, K)
            total += sign * px
        return float(total)

    def strategy_cost(self) -> float:
        """Alias (pour compatibilité) : prix aujourd'hui par action."""
        return self.price(self.params.S)

    def payoff_at_maturity(self, spot_at_expiry: float) -> float:
        """
        P&L à l'échéance par action = somme(sign * intrinsic) - prix_initial
        (donc si crédit initial : prix_initial < 0 => on ajoute un gain)
        """
        ST = float(spot_at_expiry)
        intrinsic_sum = 0.0

        for opt_type, K, sign in self.legs:
            if opt_type == "call":
                intrinsic = max(ST - K, 0.0)
            else:
                intrinsic = max(K - ST, 0.0)
            intrinsic_sum += sign * intrinsic

        pnl = intrinsic_sum - self.price(self.params.S)
        return float(pnl)

    def payoff_curve(self, spot_range: np.ndarray) -> np.ndarray:
        spot_range = np.array(spot_range, dtype=float)
        return np.array([self.payoff_at_maturity(s) for s in spot_range], dtype=float)

    def get_greeks(self, spot: float) -> Dict[str, float]:
        """
        Greeks de la stratégie au spot donné (par action).
        Calcul via MultiLegGreeksCalculator (binomial + différences finies).
        """
        spot = float(spot)

        legs_cfg = [{"K": K, "type": opt, "sign": sign} for (opt, K, sign) in self.legs]
        calc = MultiLegGreeksCalculator(
            spot_range=np.array([spot], dtype=float),
            legs=legs_cfg,
            interest_rate=self.params.r,
            time_to_maturity=self.params.T,
            volatility=self.params.sigma,
            n_steps=self.params.N,
        )
        g = calc.calculate_strategy_greeks()
        return {
            "delta": float(g["delta"][0]),
            "gamma": float(g["gamma"][0]),
            "theta": float(g["theta"][0]),
            "vega": float(g["vega"][0]),
        }

    def validate_greeks_numerically(self, spot: float, h_ratio: float = 0.002) -> Dict:
        """
        Validation Delta/Gamma :
        - on dérive numériquement la VALEUR (prix aujourd'hui), pas le payoff à l'échéance.
        """
        spot = float(spot)
        h = max(0.01, h_ratio * spot)

        V0 = self.price(spot)
        Vup = self.price(spot + h)
        Vdn = self.price(max(1e-6, spot - h))

        delta_num = (Vup - Vdn) / (2.0 * h)
        gamma_num = (Vup - 2.0 * V0 + Vdn) / (h ** 2)

        greeks = self.get_greeks(spot)
        delta_ana = greeks["delta"]
        gamma_ana = greeks["gamma"]

        delta_error = abs(delta_ana - delta_num)
        gamma_error = abs(gamma_ana - gamma_num)

        return {
            "delta_analytical": delta_ana,
            "delta_numerical": float(delta_num),
            "delta_error": float(delta_error),
            "gamma_analytical": gamma_ana,
            "gamma_numerical": float(gamma_num),
            "gamma_error": float(gamma_error),
            "max_error": float(max(delta_error, gamma_error)),
            "validation_passed": bool(max(delta_error, gamma_error) < 1e-3),
        }

    def get_strategy_details(self) -> Dict:
        """
        Détails : coût (prix), max profit/loss à l'échéance, breakevens, legs.
        Toutes les valeurs sont par action (pas multipliées).
        """
        spot_min = self.params.K1 * 0.95
        spot_max = self.params.K4 * 1.05
        spot_range = np.linspace(spot_min, spot_max, 200)

        payoff = self.payoff_curve(spot_range)

        cost = self.price(self.params.S)
        max_profit = float(np.max(payoff))
        max_loss = float(np.min(payoff))

        # Breakevens : changements de signe du P&L
        breakevens = []
        for i in range(len(payoff) - 1):
            if payoff[i] == 0:
                breakevens.append(float(spot_range[i]))
            if payoff[i] * payoff[i + 1] < 0:
                breakevens.append(float(spot_range[i]))

        legs_out = []
        for opt_type, K, sign in self.legs:
            legs_out.append({
                "type": opt_type.upper(),
                "strike": float(K),
                "position": "LONG" if sign > 0 else "SHORT",
                "weight": int(sign),
            })

        return {
            "strategy_enum": self.params.strategy_type.value,
            "net_cost": float(cost),
            "max_profit": max_profit,
            "max_loss": max_loss,
            "breakeven_points": breakevens,
            "legs": legs_out,
        }


# Alias compatibilité
ShortCondor = Condor


class StrategyExecutor:
    def __init__(self, capital: float):
        self.capital = float(capital)

    def max_quantity(self, strategy: Condor) -> int:
        details = strategy.get_strategy_details()
        max_loss_per_share = -float(details["max_loss"])  # positive
        if max_loss_per_share <= 0:
            return 0

        mult = int(strategy.params.multiplier)
        max_contracts = int(self.capital / (max_loss_per_share * mult))
        return max(0, max_contracts)

    def get_execution_summary(self, strategy: Condor, quantity: int) -> Dict:
        details = strategy.get_strategy_details()
        max_loss_per_share = -float(details["max_loss"])
        mult = int(strategy.params.multiplier)

        total_max_loss = max_loss_per_share * quantity * mult
        util = (total_max_loss / self.capital * 100.0) if self.capital > 0 else 0.0
        remaining = self.capital - total_max_loss

        return {
            "total_max_loss": float(total_max_loss),
            "capital_utilization_pct": float(util),
            "capital_remaining": float(remaining),
            "quantity": int(quantity),
        }
