#!/usr/bin/env python
"""Debug what's being passed to Plotly"""

import numpy as np
import plotly.graph_objects as go

# Simulate what app.py does
delta_condor = np.array([])
gamma_condor = np.array([])
theta_condor = np.array([])
vega_condor = np.array([])

# Simulate adding values
for i in range(5):
    delta_condor = np.append(delta_condor, 0.1 * i)
    gamma_condor = np.append(gamma_condor, 0.2 * i)
    theta_condor = np.append(theta_condor, 0.3 * i)
    vega_condor = np.append(vega_condor, 0.4 * i)

spot_range = np.linspace(100, 110, 5)

print("Type of delta_condor:", type(delta_condor))
print("delta_condor:", delta_condor)
print("delta_condor[0]:", delta_condor[0], "type:", type(delta_condor[0]))
print()

# Create a trace like in app.py
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=spot_range, y=delta_condor,
    mode='lines', name='Delta (Δ)',
    line=dict(color='#007AFF', width=3),
    hovertemplate='<b>Prix: €%{x:.2f}</b><br>Delta: %{y:.4f}<extra></extra>'
))

print("Trace y data type:", type(fig.data[0]['y']))
print("Trace y data:", fig.data[0]['y'])
print()

# Try hovering - simulate what Plotly will show
test_val = fig.data[0]['y'][0]
print(f"First value formatted with .4f: {test_val:.4f}")
