#!/usr/bin/env python
"""Debug Greeks calculation"""

from binomial_engine import BinomialModel
import numpy as np

# Test avec des paramètres réalistes
S = 100
K1 = 95
maturity = 0.25
interest_rate = 0.05
volatility = 0.2
N_steps = 50

# Test 1: Créer un modèle et calculer les Greeks
model = BinomialModel(S=S, K=K1, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
greeks = model.calculate_greeks(np.array([S]), 'call')

print("Test 1: Greeks pour un CALL avec S=100, K=95")
print(f"  Delta: {greeks['delta'][0]}")
print(f"  Gamma: {greeks['gamma'][0]}")
print(f"  Theta: {greeks['theta'][0]}")
print(f"  Vega: {greeks['vega'][0]}")
print()

# Test 2: Vérifier les prix pour debugging
price_call = model.price_call()
print(f"Test 2: Prix CALL direct avec S=100, K=95: {price_call}")
print()

# Test 3: Vérifier avec une petite boucle comme dans app.py
spot_range = np.array([95, 100, 105])
delta_list = []
for spot in spot_range:
    m = BinomialModel(S=spot, K=K1, T=maturity, r=interest_rate, sigma=volatility, N=N_steps)
    g = m.calculate_greeks(np.array([spot]), 'call')
    delta_list.append(g['delta'][0])
    print(f"Spot={spot}: Delta={g['delta'][0]:.6f}, Gamma={g['gamma'][0]:.6f}, Theta={g['theta'][0]:.6f}")
