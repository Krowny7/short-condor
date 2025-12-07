#!/usr/bin/env python
"""Full simulation of Greeks calculation in app.py"""

from binomial_engine import BinomialModel
import numpy as np

# Paramètres comme dans app.py (Mode Réel avec prix réel AAPL ~100)
S_spot = 100
K1, K2, K3, K4 = 95, 98, 102, 105
maturity = 0.25
interest_rate = 0.05
volatility = 0.2
N_steps = 50

# Range comme dans app.py
spot_range_greeks = np.linspace(S_spot * 0.7, S_spot * 1.3, 50)

delta_condor = np.array([])
gamma_condor = np.array([])
theta_condor = np.array([])
vega_condor = np.array([])

# Première itération seulement pour debug
for i, S in enumerate(spot_range_greeks[:5]):  # Juste 5 points
    model = BinomialModel(S=S, K=K1, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
    greeks_k1_call = model.calculate_greeks(np.array([S]), 'call')
    
    model_k2 = BinomialModel(S=S, K=K2, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
    greeks_k2_call = model_k2.calculate_greeks(np.array([S]), 'call')
    
    model_k3 = BinomialModel(S=S, K=K3, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
    greeks_k3_put = model_k3.calculate_greeks(np.array([S]), 'put')
    
    model_k4 = BinomialModel(S=S, K=K4, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
    greeks_k4_put = model_k4.calculate_greeks(np.array([S]), 'put')
    
    # Combine
    delta = -greeks_k1_call['delta'][0] + greeks_k2_call['delta'][0] + greeks_k3_put['delta'][0] - greeks_k4_put['delta'][0]
    gamma = -greeks_k1_call['gamma'][0] + greeks_k2_call['gamma'][0] + greeks_k3_put['gamma'][0] - greeks_k4_put['gamma'][0]
    theta = -greeks_k1_call['theta'][0] + greeks_k2_call['theta'][0] + greeks_k3_put['theta'][0] - greeks_k4_put['theta'][0]
    vega = -greeks_k1_call['vega'][0] + greeks_k2_call['vega'][0] + greeks_k3_put['vega'][0] - greeks_k4_put['vega'][0]
    
    delta_condor = np.append(delta_condor, delta)
    gamma_condor = np.append(gamma_condor, gamma)
    theta_condor = np.append(theta_condor, theta)
    vega_condor = np.append(vega_condor, vega)
    
    print(f"S={S:.1f}: Delta={delta:8.6f}, Gamma={gamma:8.6f}, Theta={theta:8.6f}, Vega={vega:8.6f}")

print("\nArrays finaux:")
print(f"delta_condor: {delta_condor}")
print(f"gamma_condor: {gamma_condor}")
print(f"theta_condor: {theta_condor}")
print(f"vega_condor: {vega_condor}")
print(f"\nRange: {spot_range_greeks[:5]}")
