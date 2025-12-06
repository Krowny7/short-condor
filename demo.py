"""
Demo script showing different Short Condor scenarios
Run this to understand the strategy without the UI
"""

import numpy as np
from binomial_engine import BinomialModel
from strategy_manager import ShortCondor, StrategyParams, StrategyExecutor


def demo_basic_pricing():
    """Demonstrate basic Short Condor pricing"""
    print("=" * 70)
    print("DEMO 1: Basic Short Condor Pricing")
    print("=" * 70)
    
    # Create strategy parameters
    params = StrategyParams(
        S=100,      # Spot: 100€
        K1=90,      # Sell Call at 90€
        K2=95,      # Buy Call at 95€
        K3=105,     # Buy Call at 105€
        K4=110,     # Sell Call at 110€
        r=0.025,    # 2.5% interest rate
        T=0.25,     # 3 months to expiration
        sigma=0.30, # 30% volatility
        N=50        # 50 binomial steps
    )
    
    # Create strategy
    strategy = ShortCondor(params)
    details = strategy.get_strategy_details()
    
    print(f"\nStrategy Parameters:")
    print(f"  Spot Price: ${params.S:.2f}")
    print(f"  Strikes: K1=${params.K1}, K2=${params.K2}, K3=${params.K3}, K4=${params.K4}")
    print(f"  Time to Expiry: {params.T:.2f} years ({params.T*365:.0f} days)")
    print(f"  Volatility: {params.sigma*100:.1f}%")
    print(f"  Risk-Free Rate: {params.r*100:.1f}%")
    
    print(f"\nIndividual Option Prices:")
    print(f"  Call @ K1 ($90): ${details['option_prices']['call_K1']:.4f} [SELL]")
    print(f"  Call @ K2 ($95): ${details['option_prices']['call_K2']:.4f} [BUY]")
    print(f"  Call @ K3 ($105): ${details['option_prices']['call_K3']:.4f} [BUY]")
    print(f"  Call @ K4 ($110): ${details['option_prices']['call_K4']:.4f} [SELL]")
    
    print(f"\nStrategy Metrics:")
    metrics = details["strategy_metrics"]
    print(f"  Net Cost: ${metrics['net_cost']:.4f}")
    if metrics['net_credit'] > 0:
        print(f"  → Credit Received: ${metrics['net_credit']:.4f} ✓")
    else:
        print(f"  → Debit Paid: ${-metrics['net_cost']:.4f}")
    
    print(f"\n  Max Profit: ${metrics['max_profit']:.4f}")
    print(f"  Max Loss: ${metrics['max_loss']:.4f}")
    print(f"  Lower Breakeven: ${metrics['lower_breakeven']:.2f}")
    print(f"  Upper Breakeven: ${metrics['upper_breakeven']:.2f}")
    print(f"  Profit Zone: ${metrics['profit_zone_lower']:.2f} - ${metrics['profit_zone_upper']:.2f}")
    
    return strategy, params


def demo_payoff_scenarios(strategy: ShortCondor, params: StrategyParams):
    """Demonstrate payoff at different spot prices"""
    print("\n" + "=" * 70)
    print("DEMO 2: Payoff at Different Spot Prices")
    print("=" * 70)
    
    scenarios = {
        "Crash (S -20%)": params.S * 0.8,
        "Down (S -10%)": params.S * 0.9,
        "Stable (S -5%)": params.S * 0.95,
        "Current": params.S,
        "Up (S +5%)": params.S * 1.05,
        "Spike (S +10%)": params.S * 1.1,
        "Moon (S +20%)": params.S * 1.2,
    }
    
    print(f"\n{'Scenario':<20} {'Spot Price':<15} {'P&L':<15} {'Status':<10}")
    print("-" * 60)
    
    for scenario_name, spot_at_exp in scenarios.items():
        pnl = strategy.payoff_at_maturity(spot_at_exp) * 100  # Per contract (100 shares)
        status = "✓ WIN" if pnl > 0 else ("✗ LOSS" if pnl < 0 else "NEUTRAL")
        print(f"{scenario_name:<20} ${spot_at_exp:<14.2f} ${pnl:<14.2f} {status:<10}")


def demo_capital_management(strategy: ShortCondor):
    """Demonstrate capital management"""
    print("\n" + "=" * 70)
    print("DEMO 3: Capital Management")
    print("=" * 70)
    
    capital_amounts = [5000, 10000, 50000, 100000]
    
    print(f"\n{'Capital':<15} {'Max Strategies':<20} {'Max Risk':<15} {'Utilization':<15}")
    print("-" * 65)
    
    for capital in capital_amounts:
        executor = StrategyExecutor(capital)
        quantity = executor.max_quantity(strategy)
        execution = executor.get_execution_summary(strategy, quantity)
        
        max_risk = execution['total_max_loss']
        utilization = execution['capital_utilization_pct']
        
        print(f"€{capital:<14,.0f} {quantity:<20}x €{max_risk:<14,.2f} {utilization:<14.1f}%")


def demo_volatility_sensitivity(params: StrategyParams):
    """Demonstrate how strategy price changes with volatility"""
    print("\n" + "=" * 70)
    print("DEMO 4: Volatility Sensitivity Analysis")
    print("=" * 70)
    
    vol_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]
    
    print(f"\n{'Volatility':<15} {'Strategy Cost':<20} {'Status':<15}")
    print("-" * 50)
    
    for vol in vol_levels:
        temp_params = StrategyParams(
            S=params.S,
            K1=params.K1,
            K2=params.K2,
            K3=params.K3,
            K4=params.K4,
            r=params.r,
            T=params.T,
            sigma=vol,
            N=params.N
        )
        temp_strategy = ShortCondor(temp_params)
        cost = temp_strategy.strategy_cost()
        
        if cost < 0:
            status = f"Credit: €{-cost:.4f} ✓"
        else:
            status = f"Debit: €{cost:.4f}"
        
        print(f"{vol*100:<14.0f}% {cost:<20.4f} {status:<15}")


def demo_greeks_equivalent(strategy: ShortCondor, params: StrategyParams):
    """Estimate Greeks for the strategy"""
    print("\n" + "=" * 70)
    print("DEMO 5: Sensitivity Analysis (Greeks-like)")
    print("=" * 70)
    
    # Calculate strategy price at spot ±1%
    current_pnl = strategy.payoff_at_maturity(params.S)
    pnl_up = strategy.payoff_at_maturity(params.S * 1.01)
    pnl_down = strategy.payoff_at_maturity(params.S * 0.99)
    
    # Approximate delta
    delta_approx = (pnl_up - pnl_down) / (2 * params.S * 0.01)
    
    print(f"\nCurrent Strategy P&L (at spot ${params.S}): ${current_pnl:.4f}")
    print(f"P&L if Spot +1%: ${pnl_up:.4f}")
    print(f"P&L if Spot -1%: ${pnl_down:.4f}")
    print(f"\nApproximate Delta: {delta_approx:.2f}")
    print(f"  → Strategy is {'long' if delta_approx > 0 else 'short'} the underlying")
    print(f"  → For every 1% move in spot, P&L changes by ~${abs(delta_approx):.2f} per contract")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("SHORT CONDOR STRATEGY - DEMONSTRATION")
    print("=" * 70 + "\n")
    
    # Run demos
    strategy, params = demo_basic_pricing()
    demo_payoff_scenarios(strategy, params)
    demo_capital_management(strategy)
    demo_volatility_sensitivity(params)
    demo_greeks_equivalent(strategy, params)
    demo_real_market_data()
    
    print("\n" + "=" * 70)
    print("Pour l'analyse interactive, lancez: streamlit run app.py")
    print("=" * 70 + "\n")


def demo_real_market_data():
    """DEMO 6: Utilisation de données de marché réelles"""
    from market_data import MarketDataProvider, AVAILABLE_STOCKS
    
    print("\n" + "=" * 70)
    print("DEMO 6: Analyse avec Données de Marche Reelles")
    print("=" * 70 + "\n")
    
    # Tester avec Apple
    symbol = "AAPL"
    print(f"Récupération des données pour {AVAILABLE_STOCKS[symbol]}...\n")
    
    provider = MarketDataProvider(symbol, period="1y")
    summary = provider.get_summary()
    
    print(f"Données de marché (Yahoo Finance):")
    print(f"  Action: {summary['name']} ({summary['symbol']})")
    print(f"  Prix actuel: EUR {summary['price']:.2f}")
    print(f"  Volatilité historique (1 an): {summary['volatility_pct']:.2f}%")
    print(f"  Date: {summary['date']}\n")
    
    # Strikes suggérés
    spot = summary['price']
    k1 = spot * 0.85
    k2 = spot * 0.90
    k3 = spot * 1.10
    k4 = spot * 1.15
    
    print(f"Strikes suggérés automatiquement (±10-15% du prix):")
    print(f"  K1 (Vendre): EUR {k1:.2f}")
    print(f"  K2 (Acheter): EUR {k2:.2f}")
    print(f"  K3 (Acheter): EUR {k3:.2f}")
    print(f"  K4 (Vendre): EUR {k4:.2f}\n")
    
    # Créer stratégie
    params = StrategyParams(
        S=spot,
        K1=k1,
        K2=k2,
        K3=k3,
        K4=k4,
        r=0.025,  # 2.5% taux d'intérêt
        T=0.25,   # 3 mois
        sigma=summary['volatility'],
        N=50
    )
    
    strategy = ShortCondor(params)
    executor = StrategyExecutor(capital=10000)
    details = strategy.get_strategy_details()
    metrics = details["strategy_metrics"]
    
    print(f"Métriques de la stratégie:")
    print(f"  Crédit net reçu: EUR {metrics['net_credit']:.2f}")
    print(f"  Profit maximum: EUR {metrics['max_profit']:.2f}")
    print(f"  Perte maximum: EUR {metrics['max_loss']:.2f}")
    print(f"  Point d'équilibre bas: EUR {metrics['lower_breakeven']:.2f}")
    print(f"  Point d'équilibre haut: EUR {metrics['upper_breakeven']:.2f}\n")
    
    # Gestion du capital
    quantity = executor.max_quantity(strategy)
    execution = executor.get_execution_summary(strategy, quantity)
    
    print(f"Gestion du capital (EUR 10,000):")
    print(f"  Stratégies exécutables: {quantity}x")
    print(f"  Risque max total: EUR {execution['total_max_loss']:.2f}")
    print(f"  Utilisation du capital: {execution['capital_utilization_pct']:.1f}%")
    print(f"  Capital restant: EUR {execution['capital_remaining']:.2f}\n")
    
    print(f"Analyse de scénarios à l'expiration (dans 3 mois):")
    scenarios = [
        ("Crash -20%", spot * 0.8),
        ("Baisse -10%", spot * 0.9),
        ("Stable (Prix actuel)", spot),
        ("Hausse +10%", spot * 1.1),
        ("Spike +20%", spot * 1.2),
    ]
    
    for scenario_name, spot_at_exp in scenarios:
        pnl = strategy.payoff_at_maturity(spot_at_exp) * quantity * 100
        status = "PROFIT" if pnl > 0 else ("PERTE" if pnl < 0 else "NEUTRE")
        print(f"  {scenario_name:25} (EUR {spot_at_exp:7.2f}): EUR {pnl:8.2f} [{status}]")
    
    print(f"\nInterprétation:")
    print(f"  La stratégie est rentable si le prix s'éloigne de son niveau actuel")
    print(f"  Elle perd si le prix reste stable (peu de volatilité réalisée)")
    print(f"  Avec une volatilité actuelle de {summary['volatility_pct']:.1f}%, la stratégie est bien positionnée\n")


if __name__ == "__main__":
    main()
