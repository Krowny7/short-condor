#!/usr/bin/env python
"""Quick test of Greeks calculation without scipy dependency"""

from binomial_engine import BinomialModel
import numpy as np

try:
    # Test basic Greeks calculation
    model = BinomialModel(100, 100, 0.05, 1, 0.2, 50)
    greeks = model.calculate_greeks(np.array([100, 105, 110]), 'call')
    
    print("✅ Greeks calculation works!")
    print(f"Delta: {greeks['delta']}")
    print(f"Gamma: {greeks['gamma']}")
    print(f"Theta: {greeks['theta']}")
    print(f"Vega: {greeks['vega']}")
    print("\n✅ No scipy import error - ready to deploy!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
