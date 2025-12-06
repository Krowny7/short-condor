"""
Script de démonstration du mode réel
Montre comment récupérer les données de marché et analyser une stratégie Short Condor
"""

from market_data import MarketDataProvider, AVAILABLE_STOCKS
from strategy_manager import ShortCondor, StrategyParams, StrategyExecutor
import numpy as np

print("=" * 80)
print("DÉMONSTRATION: MODE RÉEL AVEC DONNÉES DE MARCHÉ")
print("=" * 80)

# Sélectionner une action
stocks_to_test = ["AAPL", "TSLA", "MSFT"]

for symbol in stocks_to_test:
    print(f"\n{'─' * 80}")
    print(f"ANALYSE: {AVAILABLE_STOCKS.get(symbol, symbol)}")
    print(f"{'─' * 80}\n")
    
    try:
        # Récupérer les données de marché
        provider = MarketDataProvider(symbol, period="1y")
        summary = provider.get_summary()
        
        if provider.data is None or provider.data.empty:
            print(f"❌ Impossible de récupérer les données pour {symbol}")
            continue
        
        # Afficher les données
        print(f"📊 DONNÉES DE MARCHÉ")
        print(f"   Symbol: {symbol}")
        print(f"   Prix actuel: €{summary['price']:.2f}")
        print(f"   Volatilité historique: {summary['volatility_pct']:.2f}%")
        print(f"   Source: Yahoo Finance")
        print(f"   Date: {summary['date']}\n")
        
        # Calculer les strikes suggérés
        spot = summary['price']
        suggested_k1 = spot * 0.85
        suggested_k2 = spot * 0.90
        suggested_k3 = spot * 1.10
        suggested_k4 = spot * 1.15
        
        print(f"💡 STRIKES SUGGÉRÉS (±10-15% du spot)")
        print(f"   K1 (Vendre): €{suggested_k1:.2f}")
        print(f"   K2 (Acheter): €{suggested_k2:.2f}")
        print(f"   K3 (Acheter): €{suggested_k3:.2f}")
        print(f"   K4 (Vendre): €{suggested_k4:.2f}\n")
        
        # Créer une stratégie
        params = StrategyParams(
            S=spot,
            K1=suggested_k1,
            K2=suggested_k2,
            K3=suggested_k3,
            K4=suggested_k4,
            r=0.025,  # 2.5%
            T=0.25,   # 3 mois
            sigma=summary['volatility'],
            N=50
        )
        
        strategy = ShortCondor(params)
        executor = StrategyExecutor(capital=10000)
        details = strategy.get_strategy_details()
        
        # Afficher les résultats
        print(f"📈 ANALYSE DE LA STRATÉGIE")
        metrics = details["strategy_metrics"]
        print(f"   Crédit Net: €{metrics['net_credit']:.2f}")
        print(f"   Profit Max: €{metrics['max_profit']:.2f}")
        print(f"   Perte Max: €{metrics['max_loss']:.2f}")
        print(f"   Point d'équilibre bas: €{metrics['lower_breakeven']:.2f}")
        print(f"   Point d'équilibre haut: €{metrics['upper_breakeven']:.2f}\n")
        
        # Gestion du capital
        quantity = executor.max_quantity(strategy)
        execution = executor.get_execution_summary(strategy, quantity)
        
        print(f"💰 GESTION DU CAPITAL (€10,000)")
        print(f"   Stratégies exécutables: {quantity}x")
        print(f"   Risque max total: €{execution['total_max_loss']:.2f}")
        print(f"   Utilisation du capital: {execution['capital_utilization_pct']:.1f}%")
        print(f"   Capital restant: €{execution['capital_remaining']:.2f}\n")
        
        # Scénarios
        print(f"📊 SCENARIOS À L'EXPIRATION")
        scenarios = [
            ("Crash -20%", spot * 0.8),
            ("Baisse -10%", spot * 0.9),
            ("Prix actuel", spot),
            ("Hausse +10%", spot * 1.1),
            ("Pic +20%", spot * 1.2),
        ]
        
        for scenario_name, spot_at_exp in scenarios:
            pnl = strategy.payoff_at_maturity(spot_at_exp) * quantity * 100
            status = "✓ PROFIT" if pnl > 0 else ("✗ PERTE" if pnl < 0 else "- NEUTRE")
            print(f"   {scenario_name:15} (€{spot_at_exp:7.2f}): {pnl:10.2f}€ {status}")
        
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {symbol}: {str(e)}\n")

print("=" * 80)
print("FIN DE LA DÉMONSTRATION")
print("=" * 80)
