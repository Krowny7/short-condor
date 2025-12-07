#!/usr/bin/env python
"""Debug Short Condor Greeks combination"""

from binomial_engine import BinomialModel
import numpy as np

# Paramètres réalistes
S = 100  # Spot price
K1, K2, K3, K4 = 95, 98, 102, 105  # Short Condor strikes
maturity = 0.25
interest_rate = 0.05
volatility = 0.2
N_steps = 50

# Une seule itération pour tester
S_test = 100

# Modèles pour chaque leg
model_k1 = BinomialModel(S=S_test, K=K1, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
greeks_k1_call = model_k1.calculate_greeks(np.array([S_test]), 'call')

model_k2 = BinomialModel(S=S_test, K=K2, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
greeks_k2_call = model_k2.calculate_greeks(np.array([S_test]), 'call')

model_k3 = BinomialModel(S=S_test, K=K3, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
greeks_k3_put = model_k3.calculate_greeks(np.array([S_test]), 'put')

model_k4 = BinomialModel(S=S_test, K=K4, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
greeks_k4_put = model_k4.calculate_greeks(np.array([S_test]), 'put')

print("Greeks individuels pour chaque leg à S=100:")
print(f"K1 Call: Delta={greeks_k1_call['delta'][0]:.6f}")
print(f"K2 Call: Delta={greeks_k2_call['delta'][0]:.6f}")
print(f"K3 Put:  Delta={greeks_k3_put['delta'][0]:.6f}")
print(f"K4 Put:  Delta={greeks_k4_put['delta'][0]:.6f}")
print()

# Short Condor: Vendre K1 Call, Acheter K2 Call, Acheter K3 Put, Vendre K4 Put
delta = -greeks_k1_call['delta'][0] + greeks_k2_call['delta'][0] + greeks_k3_put['delta'][0] - greeks_k4_put['delta'][0]
gamma = -greeks_k1_call['gamma'][0] + greeks_k2_call['gamma'][0] + greeks_k3_put['gamma'][0] - greeks_k4_put['gamma'][0]
theta = -greeks_k1_call['theta'][0] + greeks_k2_call['theta'][0] + greeks_k3_put['theta'][0] - greeks_k4_put['theta'][0]
vega = -greeks_k1_call['vega'][0] + greeks_k2_call['vega'][0] + greeks_k3_put['vega'][0] - greeks_k4_put['vega'][0]

print("Short Condor Greeks combinés:")
print(f"Delta: {delta:.6f}")
print(f"Gamma: {gamma:.6f}")
print(f"Theta: {theta:.6f}")
print(f"Vega:  {vega:.6f}")
