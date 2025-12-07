"""
Corrected Module for Iron Condor Strategy Management
With proper Greeks calculation and validation
"""

import numpy as np
from scipy.stats import norm
from binomial_engine import BinomialModel
from dataclasses import dataclass
from typing import Tuple, Dict, List
from enum import Enum


class StrategyType(Enum):
    """Strategy type enumeration"""
    SHORT_IRON_CONDOR_CREDIT = "short_iron_condor_credit"
    REVERSE_IRON_CONDOR_DEBIT = "reverse_iron_condor_debit"


@dataclass
class StrategyParams:
    """Parameters for Iron Condor strategy."""
    S: float  # Current spot price
    K1: float  # Lowest strike (long put)
    K2: float  # Second strike (short put)
    K3: float  # Third strike (short call)
    K4: float  # Highest strike (long call)
    r: float  # Risk-free rate
    T: float  # Time to maturity (in years)
    sigma: float  # Volatility
    N: int  # Number of binomial steps
    strategy_type: StrategyType = StrategyType.SHORT_IRON_CONDOR_CREDIT
    multiplier: int = 100  # Contract multiplier (typically 100)


class BlackScholesGreeks:
    """Black-Scholes Greeks calculator"""
    
    @staticmethod
    def d1(S, K, r, T, sigma):
        """Calculate d1 for Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def d2(S, K, r, T, sigma):
        """Calculate d2 for Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        return d1 - sigma * np.sqrt(T)
    
    @staticmethod
    def call_price(S, K, r, T, sigma):
        """European call price"""
        if T <= 0:
            return max(S - K, 0)
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        d2 = BlackScholesGreeks.d2(S, K, r, T, sigma)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    @staticmethod
    def put_price(S, K, r, T, sigma):
        """European put price"""
        if T <= 0:
            return max(K - S, 0)
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        d2 = BlackScholesGreeks.d2(S, K, r, T, sigma)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    @staticmethod
    def call_delta(S, K, r, T, sigma):
        """Call delta"""
        if T <= 0:
            return 1.0 if S > K else 0.0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        return norm.cdf(d1)
    
    @staticmethod
    def put_delta(S, K, r, T, sigma):
        """Put delta"""
        if T <= 0:
            return -1.0 if S < K else 0.0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        return norm.cdf(d1) - 1.0
    
    @staticmethod
    def gamma(S, K, r, T, sigma):
        """Gamma for both calls and puts"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    @staticmethod
    def vega(S, K, r, T, sigma):
        """Vega (for 1% change in volatility)"""
        if T <= 0 or sigma <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        return S * norm.pdf(d1) * np.sqrt(T) / 100.0
    
    @staticmethod
    def theta(S, K, r, T, sigma, option_type='call'):
        """Theta (daily decay)"""
        if T <= 0:
            return 0.0
        d1 = BlackScholesGreeks.d1(S, K, r, T, sigma)
        d2 = BlackScholesGreeks.d2(S, K, r, T, sigma)
        
        if option_type == 'call':
            theta_value = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                          - r * K * np.exp(-r * T) * norm.cdf(d2))
        else:  # put
            theta_value = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                          + r * K * np.exp(-r * T) * norm.cdf(-d2))
        
        # Convert to daily theta (divide by 365)
        return theta_value / 365.0


class IronCondor:
    """
    Iron Condor Strategy Implementation.
    
    SHORT IRON CONDOR (Credit Strategy):
    Structure:
    - Long Put at K1 (protection)
    - Short Put at K2 (income)
    - Short Call at K3 (income)
    - Long Call at K4 (protection)
    
    Condition: K1 < K2 < S0 < K3 < K4
    
    Payoff Shape:
    - Maximum profit when spot stays between K2 and K3
    - Limited losses on both sides (protected by long K1 put and long K4 call)
    - This is a CREDIT strategy (receive premium upfront)
    """
    
    def __init__(self, params: StrategyParams):
        """Initialize Iron Condor strategy with parameters."""
        # Validate strike order
        if not (params.K1 < params.K2 < params.S < params.K3 < params.K4):
            raise ValueError(
                f"For short iron condor: K1 < K2 < S < K3 < K4\n"
                f"Got: K1={params.K1}, K2={params.K2}, S={params.S}, K3={params.K3}, K4={params.K4}"
            )
        
        self.params = params
        self.strategy_type = params.strategy_type
        
        # Define legs: (option_type, strike, weight)
        # weight +1 = long, -1 = short
        if params.strategy_type == StrategyType.SHORT_IRON_CONDOR_CREDIT:
            self.legs = [
                ('put', params.K1, +1),   # Long put
                ('put', params.K2, -1),   # Short put
                ('call', params.K3, -1),  # Short call
                ('call', params.K4, +1),  # Long call
            ]
        else:  # REVERSE
            self.legs = [
                ('put', params.K1, -1),   # Short put
                ('put', params.K2, +1),   # Long put
                ('call', params.K3, +1),  # Long call
                ('call', params.K4, -1),  # Short call
            ]
    
    def _get_option_price(self, option_type: str, strike: float) -> float:
        """Get option price using Black-Scholes"""
        if option_type == 'call':
            return BlackScholesGreeks.call_price(
                self.params.S, strike, self.params.r, 
                self.params.T, self.params.sigma
            )
        else:  # put
            return BlackScholesGreeks.put_price(
                self.params.S, strike, self.params.r, 
                self.params.T, self.params.sigma
            )
    
    def strategy_cost(self) -> float:
        """
        Calculate net cost/credit of the strategy.
        
        For short iron condor:
        - We SELL (short) expensive options (K2 put, K3 call) -> receive credit
        - We BUY (long) cheaper options (K1 put, K4 call) -> pay debit
        - Net = Credit - Debit
        
        Returns:
        --------
        float : Negative = credit received, Positive = debit paid
        """
        net_cost = 0.0
        for option_type, strike, weight in self.legs:
            price = self._get_option_price(option_type, strike)
            # weight +1 (long) = we pay (cost increases)
            # weight -1 (short) = we receive (cost decreases)
            net_cost += weight * price
        
        return net_cost
    
    def payoff_at_maturity(self, spot_at_expiry: float) -> float:
        """
        Calculate payoff at maturity for a given spot price.
        
        Parameters:
        -----------
        spot_at_expiry : float - Stock price at maturity
        
        Returns:
        --------
        float : P&L per share (not including multiplier)
        """
        payoff = 0.0
        
        for option_type, strike, weight in self.legs:
            if option_type == 'call':
                intrinsic = max(spot_at_expiry - strike, 0)
            else:  # put
                intrinsic = max(strike - spot_at_expiry, 0)
            
            # weight: +1 = long (we profit), -1 = short (we lose)
            payoff += weight * intrinsic
        
        # Add initial net credit/debit
        net_credit = -self.strategy_cost()  # Negative cost = positive credit
        payoff += net_credit
        
        return payoff
    
    def payoff_curve(self, spot_range: np.ndarray) -> np.ndarray:
        """Calculate payoff for range of spot prices"""
        return np.array([self.payoff_at_maturity(S) for S in spot_range])
    
    def get_greeks(self, spot: float) -> Dict[str, float]:
        """
        Calculate strategy Greeks using weighted sum of leg Greeks.
        
        Returns:
        --------
        Dict with 'delta', 'gamma', 'vega', 'theta' (all per share)
        """
        greeks = {'delta': 0.0, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0}
        
        for option_type, strike, weight in self.legs:
            if option_type == 'call':
                delta = BlackScholesGreeks.call_delta(
                    spot, strike, self.params.r, self.params.T, self.params.sigma
                )
                theta = BlackScholesGreeks.theta(
                    spot, strike, self.params.r, self.params.T, self.params.sigma, 'call'
                )
            else:  # put
                delta = BlackScholesGreeks.put_delta(
                    spot, strike, self.params.r, self.params.T, self.params.sigma
                )
                theta = BlackScholesGreeks.theta(
                    spot, strike, self.params.r, self.params.T, self.params.sigma, 'put'
                )
            
            gamma = BlackScholesGreeks.gamma(
                spot, strike, self.params.r, self.params.T, self.params.sigma
            )
            vega = BlackScholesGreeks.vega(
                spot, strike, self.params.r, self.params.T, self.params.sigma
            )
            
            # Apply weight and accumulate
            greeks['delta'] += weight * delta
            greeks['gamma'] += weight * gamma
            greeks['vega'] += weight * vega
            greeks['theta'] += weight * theta
        
        return greeks
    
    def validate_greeks_numerically(self, spot: float, h_ratio: float = 0.002) -> Dict:
        """
        Validate analytical Greeks against numerical approximation.
        
        Parameters:
        -----------
        spot : float - Spot price to evaluate
        h_ratio : float - h = h_ratio * spot for finite difference
        
        Returns:
        --------
        Dict with validation results
        """
        h = h_ratio * spot if spot > 0 else 0.01
        
        # Current payoff
        V_current = self.payoff_at_maturity(spot)
        V_up = self.payoff_at_maturity(spot + h)
        V_down = self.payoff_at_maturity(spot - h)
        
        # Numerical Greeks
        delta_num = (V_up - V_down) / (2 * h)
        gamma_num = (V_up - 2 * V_current + V_down) / (h ** 2)
        
        # Analytical Greeks
        greeks = self.get_greeks(spot)
        delta_ana = greeks['delta']
        gamma_ana = greeks['gamma']
        
        # Calculate errors
        delta_error = abs(delta_ana - delta_num) if delta_num != 0 else abs(delta_ana)
        gamma_error = abs(gamma_ana - gamma_num) if gamma_num != 0 else abs(gamma_ana)
        
        return {
            'delta_analytical': delta_ana,
            'delta_numerical': delta_num,
            'delta_error': delta_error,
            'gamma_analytical': gamma_ana,
            'gamma_numerical': gamma_num,
            'gamma_error': gamma_error,
            'max_error': max(delta_error, gamma_error),
            'validation_passed': max(delta_error, gamma_error) < 1e-3
        }
    
    def get_strategy_details(self) -> Dict:
        """Return comprehensive strategy details"""
        spot_min = self.params.K1 * 0.95
        spot_max = self.params.K4 * 1.05
        spot_range = np.linspace(spot_min, spot_max, 100)
        payoff_range = self.payoff_curve(spot_range)
        
        cost = self.strategy_cost()
        max_profit = np.max(payoff_range)
        max_loss = np.min(payoff_range)
        
        greeks_at_spot = self.get_greeks(self.params.S)
        
        # Find breakevens
        breakevens = []
        for i in range(len(payoff_range) - 1):
            if payoff_range[i] * payoff_range[i + 1] < 0:  # Sign change
                breakevens.append(spot_range[i])
        
        return {
            'strategy_type': self.strategy_type.value,
            'net_cost': cost,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakeven_points': breakevens,
            'current_greeks': greeks_at_spot,
            'legs': [
                {
                    'type': leg[0],
                    'strike': leg[1],
                    'position': 'LONG' if leg[2] > 0 else 'SHORT',
                    'weight': leg[2]
                }
                for leg in self.legs
            ]
        }


# Backward compatibility wrapper
class ShortCondor(IronCondor):
    """Backward compatibility alias for IronCondor"""
    def __init__(self, params: StrategyParams):
        # Ensure backward compatibility
        if not hasattr(params, 'strategy_type'):
            params.strategy_type = StrategyType.SHORT_IRON_CONDOR_CREDIT
        super().__init__(params)


class StrategyExecutor:
    """Execute strategy with capital management"""
    
    def __init__(self, capital: float):
        self.capital = capital
    
    def max_quantity(self, strategy: IronCondor) -> int:
        """Calculate max contracts given capital and max loss"""
        max_loss = -strategy.get_strategy_details()['max_loss']
        if max_loss <= 0:
            return 0
        
        # Each contract controls 100 shares
        max_contracts = int(self.capital / (max_loss * strategy.params.multiplier))
        return max(0, max_contracts)
    
    def get_execution_summary(self, strategy: IronCondor, quantity: int) -> Dict:
        """Get execution summary"""
        details = strategy.get_strategy_details()
        max_loss = -details['max_loss']
        total_max_loss = max_loss * quantity * strategy.params.multiplier
        
        return {
            'total_max_loss': total_max_loss,
            'capital_utilization_pct': (total_max_loss / self.capital * 100) if self.capital > 0 else 0,
            'capital_remaining': self.capital - total_max_loss,
            'quantity': quantity
        }
