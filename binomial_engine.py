"""
Module for Binomial Option Pricing using Cox-Ross-Rubinstein (CRR) Model
"""

import numpy as np
from typing import Tuple, Dict, List


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
        """Initialize the binomial model parameters."""
        self.S = S
        self.K = K
        self.r = r
        self.T = T
        self.sigma = sigma
        self.N = N
        self.dt = T / N  # Length of each time step
        
        # Calculate CRR parameters
        self.u = np.exp(sigma * np.sqrt(self.dt))  # Up factor
        self.d = 1 / self.u  # Down factor
        self.q = (np.exp(r * self.dt) - self.d) / (self.u - self.d)  # Risk-neutral probability
        
    def price_call(self) -> float:
        """
        Calculate the price of a European call option using binomial tree.
        
        Returns:
        --------
        float : Option price
        """
        # Initialize option values at maturity (leaf nodes)
        option_values = np.zeros(self.N + 1)
        
        # Calculate intrinsic values at maturity
        for j in range(self.N + 1):
            S_T = self.S * (self.u ** (self.N - j)) * (self.d ** j)
            option_values[j] = max(S_T - self.K, 0)
        
        # Backward induction through the tree
        for i in range(self.N - 1, -1, -1):
            # Create temporary array for this level
            new_values = np.zeros(i + 1)
            for j in range(i + 1):
                new_values[j] = (
                    np.exp(-self.r * self.dt) * 
                    (self.q * option_values[j] + (1 - self.q) * option_values[j + 1])
                )
            option_values = new_values
        
        return float(option_values[0])
    
    def price_put(self) -> float:
        """
        Calculate the price of a European put option using binomial tree.
        
        Returns:
        --------
        float : Option price
        """
        # Initialize option values at maturity (leaf nodes)
        option_values = np.zeros(self.N + 1)
        
        # Calculate intrinsic values at maturity
        for j in range(self.N + 1):
            S_T = self.S * (self.u ** (self.N - j)) * (self.d ** j)
            option_values[j] = max(self.K - S_T, 0)
        
        # Backward induction through the tree
        for i in range(self.N - 1, -1, -1):
            # Create temporary array for this level
            new_values = np.zeros(i + 1)
            for j in range(i + 1):
                new_values[j] = (
                    np.exp(-self.r * self.dt) * 
                    (self.q * option_values[j] + (1 - self.q) * option_values[j + 1])
                )
            option_values = new_values
        
        return float(option_values[0])
    
    def _build_stock_tree(self) -> np.ndarray:
        """
        Build the stock price tree.
        
        Returns:
        --------
        np.ndarray : Stock prices at each node (last row contains final prices)
        """
        stock_tree = np.zeros(self.N + 1)
        
        # Generate all possible stock prices at maturity
        for j in range(self.N + 1):
            stock_tree[j] = self.S * (self.u ** (self.N - j)) * (self.d ** j)
        
        return stock_tree
    
    def get_tree_data(self) -> Dict:
        """
        Get tree structure for visualization (useful for small N).
        
        Returns:
        --------
        Dict : Tree data containing stock prices and option values
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
                "q": self.q
            }
        }
        
        # Build stock price tree level by level
        for i in range(self.N + 1):
            tree_data["stock_prices"][i] = {}
            for j in range(i + 1):
                tree_data["stock_prices"][i][j] = self.S * (self.u ** (i - j)) * (self.d ** j)
        
        # Calculate call prices using backward induction
        call_tree = {}
        for j in range(self.N + 1):
            call_tree[j] = max(tree_data["stock_prices"][self.N][j] - self.K, 0)
        
        tree_data["call_prices"][self.N] = call_tree
        
        for i in range(self.N - 1, -1, -1):
            tree_data["call_prices"][i] = {}
            for j in range(i + 1):
                call_value = (
                    np.exp(-self.r * self.dt) * 
                    (self.q * tree_data["call_prices"][i + 1][j] + 
                     (1 - self.q) * tree_data["call_prices"][i + 1][j + 1])
                )
                tree_data["call_prices"][i][j] = call_value
        
        # Calculate put prices using backward induction
        put_tree = {}
        for j in range(self.N + 1):
            put_tree[j] = max(self.K - tree_data["stock_prices"][self.N][j], 0)
        
        tree_data["put_prices"][self.N] = put_tree
        
        for i in range(self.N - 1, -1, -1):
            tree_data["put_prices"][i] = {}
            for j in range(i + 1):
                put_value = (
                    np.exp(-self.r * self.dt) * 
                    (self.q * tree_data["put_prices"][i + 1][j] + 
                     (1 - self.q) * tree_data["put_prices"][i + 1][j + 1])
                )
                tree_data["put_prices"][i][j] = put_value
        
        return tree_data
    
    @staticmethod
    def price_range_at_maturity(
        S: float, K: float, r: float, T: float, sigma: float, N: int,
        spot_range: np.ndarray, option_type: str = "call"
    ) -> np.ndarray:
        """
        Calculate option prices across a range of spot prices at maturity.
        Used for payoff diagrams.
        
        Parameters:
        -----------
        S, K, r, T, sigma, N : Model parameters (not all used for intrinsic value)
        spot_range : np.ndarray of spot prices to evaluate
        option_type : "call" or "put"
        
        Returns:
        --------
        np.ndarray : Option values at maturity for each spot price
        """
        if option_type.lower() == "call":
            return np.maximum(spot_range - K, 0)
        elif option_type.lower() == "put":
            return np.maximum(K - spot_range, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
    def calculate_greeks(self, spot_range, option_type="call"):
        """
        Calculer les Greeks (Delta, Gamma, Theta, Vega) sur une range de prix
        
        Parameters:
        -----------
        spot_range : np.ndarray - Range de prix spot
        option_type : str - "call" ou "put"
        
        Returns:
        --------
        dict with 'delta', 'gamma', 'theta', 'vega' as np.ndarray
        """
        from scipy.stats import norm
        
        greeks = {'delta': [], 'gamma': [], 'theta': [], 'vega': []}
        
        for S in spot_range:
            # Recalculer le prix avec la nouvelle taille de l'arbre
            tree = self.build_tree(S)
            option_price = self.backward_induction(tree, self.K, option_type)
            
            # Delta: dérivée par rapport au spot
            bump = S * 0.01 if S > 0 else 0.01
            tree_up = self.build_tree(S + bump)
            option_up = self.backward_induction(tree_up, self.K, option_type)
            tree_down = self.build_tree(S - bump)
            option_down = self.backward_induction(tree_down, self.K, option_type)
            delta = (option_up - option_down) / (2 * bump)
            
            # Gamma: dérivée seconde par rapport au spot
            gamma = (option_up - 2 * option_price + option_down) / (bump ** 2)
            
            # Theta: dérivée par rapport au temps (décroissance temporelle)
            # Approximation: 1 jour = 1/365 an
            t_bump = 1/365
            T_new = max(self.T - t_bump, 0.001)
            tree_t = self.build_tree(S)
            # Recalculer avec le nouveau T (simplifié)
            theta = (option_price - option_price) / t_bump if T_new < self.T else 0
            # Approximation plus simple pour Theta
            theta = -0.5 * gamma * (S ** 2) * (self.sigma ** 2)  # Theta approximation
            
            # Vega: dérivée par rapport à la volatilité
            vol_bump = self.sigma * 0.01 if self.sigma > 0 else 0.01
            old_sigma = self.sigma
            self.sigma = self.sigma + vol_bump
            tree_vol_up = self.build_tree(S)
            option_vol_up = self.backward_induction(tree_vol_up, self.K, option_type)
            self.sigma = old_sigma
            vega = (option_vol_up - option_price) / vol_bump
            
            greeks['delta'].append(delta)
            greeks['gamma'].append(gamma)
            greeks['theta'].append(theta)
            greeks['vega'].append(vega)
        
        return {k: np.array(v) for k, v in greeks.items()}
