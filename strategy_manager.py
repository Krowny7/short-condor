"""
Module for Short Condor Strategy Management
Volatility-based options strategy using binomial pricing
"""

import numpy as np
from binomial_engine import BinomialModel
from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass
class StrategyParams:
    """Parameters for Short Condor strategy."""
    S: float  # Current spot price
    K1: float  # Lowest strike (sold call)
    K2: float  # Second strike (bought call)
    K3: float  # Third strike (bought call)
    K4: float  # Highest strike (sold call)
    r: float  # Risk-free rate
    T: float  # Time to maturity
    sigma: float  # Volatility
    N: int  # Number of binomial steps


class ShortCondor:
    """
    Short Condor Strategy Implementation.
    
    Structure:
    - Sell Call at K1 (lowest strike)
    - Buy Call at K2
    - Buy Call at K3
    - Sell Call at K4 (highest strike)
    
    Condition: K1 < K2 < K3 < K4
    
    Payoff:
    - Maximum profit when spot stays between K2 and K3
    - Maximum loss when spot goes beyond K1 or above K4
    """
    
    def __init__(self, params: StrategyParams):
        """Initialize Short Condor strategy with parameters."""
        # Validate strike order
        if not (params.K1 < params.K2 < params.K3 < params.K4):
            raise ValueError(f"Strikes must satisfy K1 < K2 < K3 < K4. Got: {params.K1}, {params.K2}, {params.K3}, {params.K4}")
        
        self.params = params
        
        # Calculate individual call prices using binomial model
        self.call_K1 = BinomialModel(params.S, params.K1, params.r, params.T, params.sigma, params.N).price_call()
        self.call_K2 = BinomialModel(params.S, params.K2, params.r, params.T, params.sigma, params.N).price_call()
        self.call_K3 = BinomialModel(params.S, params.K3, params.r, params.T, params.sigma, params.N).price_call()
        self.call_K4 = BinomialModel(params.S, params.K4, params.r, params.T, params.sigma, params.N).price_call()
    
    def strategy_cost(self) -> float:
        """
        Calculate the net cost/credit of the Short Condor.
        
        Formula: -(Call_K1) - (-Call_K4) - Call_K2 - (-Call_K3)
        Which simplifies to: call_K1 - call_K2 - call_K3 + call_K4
        (Negative means credit, positive means debit)
        
        Returns:
        --------
        float : Net cost (negative = credit received, positive = debit paid)
        """
        # Sell K1 and K4, Buy K2 and K3
        net_cost = -self.call_K1 + self.call_K2 + self.call_K3 - self.call_K4
        return net_cost
    
    def payoff_at_maturity(self, spot_price: float) -> float:
        """
        Calculate the payoff of the Short Condor at maturity for a given spot price.
        
        Structure of Short Condor (with calls):
        +1 Call spread (K2-K3): Buy K2, Sell K3
        -1 Call spread (K1-K4): Sell K1, Buy K4
        
        This is equivalent to:
        +1 Short Put Spread @ (K1-K2) + +1 Short Call Spread @ (K3-K4)
        
        More direct calculation:
        Short Condor payoff = (Sell K1 - Buy K4) + (Buy K2 - Sell K3)
        
        Parameters:
        -----------
        spot_price : float - Stock price at maturity
        
        Returns:
        --------
        float : Total payoff (including premium paid/received)
        """
        # Calculate payoff of each individual position at maturity
        # All options are European calls, intrinsic value at expiration
        
        # Sold Call at K1 (we receive payoff when S < K1)
        payoff_sell_K1 = -max(spot_price - self.params.K1, 0)
        
        # Bought Call at K2 (we have payoff when S > K2)
        payoff_buy_K2 = max(spot_price - self.params.K2, 0)
        
        # Bought Call at K3 (we have payoff when S > K3)
        payoff_buy_K3 = max(spot_price - self.params.K3, 0)
        
        # Sold Call at K4 (we pay when S > K4)
        payoff_sell_K4 = -max(spot_price - self.params.K4, 0)
        
        # Total payoff from all positions
        payoff_at_expiry = payoff_sell_K1 + payoff_buy_K2 + payoff_buy_K3 + payoff_sell_K4
        
        # The net initial credit/debit
        # For a short condor, we SELL high value options (K1, K4) and BUY low value options (K2, K3)
        # So we typically receive a NET CREDIT = Price(K1) + Price(K4) - Price(K2) - Price(K3)
        net_credit = self.call_K1 + self.call_K4 - self.call_K2 - self.call_K3
        
        # Total P&L = payoff at expiry + net credit received
        total_pnl = payoff_at_expiry + net_credit
        
        return total_pnl
    
    def payoff_curve(self, spot_range: np.ndarray) -> np.ndarray:
        """
        Calculate payoff curve for a range of spot prices.
        
        Parameters:
        -----------
        spot_range : np.ndarray - Array of spot prices at maturity
        
        Returns:
        --------
        np.ndarray : Payoff values for each spot price
        """
        return np.array([self.payoff_at_maturity(S) for S in spot_range])
    
    def max_profit(self) -> float:
        """
        Calculate maximum profit of the Short Condor.
        
        Max profit occurs when spot stays between K2 and K3.
        
        Returns:
        --------
        float : Maximum profit
        """
        return -self.strategy_cost() if self.strategy_cost() < 0 else 0
    
    def max_loss(self) -> float:
        """
        Calculate maximum loss of the Short Condor.
        
        Max loss occurs at extremes (S <= K1 or S >= K4).
        
        Returns:
        --------
        float : Maximum loss (as absolute value)
        """
        # At S <= K1: payoff = 0 + credit = -strategy_cost
        # At S >= K4: payoff = (K4-K1) - (K4-K2) - (K4-K3) + credit
        #                     = K4 - K1 - K4 + K2 - K4 + K3 + credit
        #                     = K2 + K3 - K1 - K4 + credit
        
        width = self.params.K4 - self.params.K1
        max_intrinsic_loss = (self.params.K3 - self.params.K2) + (self.params.K4 - self.params.K3)
        
        # The max loss is the width of the outer strikes minus the credit
        max_loss_value = max_intrinsic_loss - (-self.strategy_cost() if self.strategy_cost() < 0 else -self.strategy_cost())
        
        return abs(max_loss_value)
    
    def breakeven_points(self) -> Tuple[float, float]:
        """
        Calculate breakeven points of the Short Condor.
        
        Returns:
        --------
        Tuple[float, float] : Lower and upper breakeven points
        """
        credit = -self.strategy_cost() if self.strategy_cost() < 0 else 0
        
        # Lower breakeven: K2 - credit
        lower_be = self.params.K2 - credit
        
        # Upper breakeven: K3 + credit
        upper_be = self.params.K3 + credit
        
        return (lower_be, upper_be)
    
    def get_strategy_details(self) -> Dict:
        """
        Return comprehensive strategy details.
        
        Returns:
        --------
        Dict : Strategy metrics and characteristics
        """
        cost = self.strategy_cost()
        lower_be, upper_be = self.breakeven_points()
        
        return {
            "strike_prices": {
                "K1_sold": self.params.K1,
                "K2_bought": self.params.K2,
                "K3_bought": self.params.K3,
                "K4_sold": self.params.K4
            },
            "option_prices": {
                "call_K1": self.call_K1,
                "call_K2": self.call_K2,
                "call_K3": self.call_K3,
                "call_K4": self.call_K4
            },
            "strategy_metrics": {
                "net_cost": cost,
                "net_credit": -cost if cost < 0 else 0,
                "net_debit": cost if cost > 0 else 0,
                "max_profit": self.max_profit(),
                "max_loss": abs(self.max_loss()),
                "lower_breakeven": lower_be,
                "upper_breakeven": upper_be,
                "profit_zone_lower": self.params.K2,
                "profit_zone_upper": self.params.K3
            }
        }


class StrategyExecutor:
    """Execute and manage Short Condor strategies with capital constraints."""
    
    def __init__(self, capital: float):
        """
        Initialize strategy executor with available capital.
        
        Parameters:
        -----------
        capital : float - Available capital in EUR
        """
        self.capital = capital
    
    def max_quantity(self, strategy: ShortCondor) -> int:
        """
        Calculate maximum number of complete strategies that can be executed.
        
        Each strategy has a notional value based on strike spacing.
        For a Short Condor, the notional is typically the width of strikes (K4-K1).
        
        Parameters:
        -----------
        strategy : ShortCondor - Strategy instance
        
        Returns:
        --------
        int : Maximum number of complete strategies
        """
        # Notional value per contract (usually 100 shares)
        multiplier = 100
        
        # Width of the condor
        width = strategy.params.K4 - strategy.params.K1
        notional_per_strategy = width * multiplier
        
        # For margin calculation, we use the max loss
        max_risk = strategy.max_loss() * multiplier
        
        # Number of strategies we can afford
        quantity = int(self.capital / max_risk) if max_risk > 0 else 0
        
        return max(0, quantity)
    
    def portfolio_pnl(self, strategy: ShortCondor, quantity: int, spot_at_maturity: float) -> float:
        """
        Calculate portfolio P&L at maturity.
        
        Parameters:
        -----------
        strategy : ShortCondor - Strategy instance
        quantity : int - Number of strategies
        spot_at_maturity : float - Stock price at maturity
        
        Returns:
        --------
        float : Total portfolio P&L
        """
        pnl_per_strategy = strategy.payoff_at_maturity(spot_at_maturity)
        multiplier = 100
        total_pnl = pnl_per_strategy * quantity * multiplier
        
        return total_pnl
    
    def get_execution_summary(self, strategy: ShortCondor, quantity: int) -> Dict:
        """
        Get execution summary for the strategy.
        
        Returns:
        --------
        Dict : Execution details
        """
        multiplier = 100
        total_risk = strategy.max_loss() * quantity * multiplier
        
        return {
            "capital_available": self.capital,
            "quantity": quantity,
            "max_loss_per_strategy": strategy.max_loss(),
            "total_max_loss": total_risk,
            "capital_utilization_pct": (total_risk / self.capital * 100) if self.capital > 0 else 0,
            "capital_remaining": max(0, self.capital - total_risk)
        }
