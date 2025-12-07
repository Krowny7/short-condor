"""
Application Streamlit - Analyse de la Stratégie Short Condor
Interface Interactive pour l'évaluation et l'analyse des stratégies d'options basées sur la volatilité
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from binomial_engine import BinomialModel
from strategy_manager import ShortCondor, StrategyParams, StrategyExecutor
from market_data import MarketDataProvider, AVAILABLE_STOCKS


# Configuration de la page
st.set_page_config(
    page_title="Analyseur de Stratégie Short Condor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour meilleur style
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .profit-zone {
        color: #2ecc71;
        font-weight: bold;
    }
    .loss-zone {
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    st.title("📈 Analyseur de Stratégie Short Condor")
    st.markdown("**Outil d'Évaluation des Stratégies d'Options Basées sur la Volatilité**")
    st.markdown("Modèle Binomial (Cox-Ross-Rubinstein) pour Options Européennes")
    
    # ======================== CHOIX DU MODE ========================
    mode = st.radio(
        "🎯 Mode d'Utilisation",
        ["Mode Manuel", "Mode Réel (Données de Marché)"],
        horizontal=True,
        help="Manuel: Entrez vos propres valeurs | Réel: Données en direct depuis Yahoo Finance"
    )
    
    # ======================== BARRE LATÉRALE: PARAMÈTRES ========================
    with st.sidebar:
        st.header("⚙️ Paramètres de Stratégie")
        
        # ==================== MODE RÉEL ====================
        if mode == "Mode Réel (Données de Marché)":
            st.subheader("📊 Données de Marché Réelles")
            
            # Sélection de l'action
            selected_stock = st.selectbox(
                "Sélectionner une action",
                list(AVAILABLE_STOCKS.keys()),
                format_func=lambda x: f"{x} - {AVAILABLE_STOCKS[x]}"
            )
            
            # Récupérer les données
            with st.spinner(f"📡 Récupération des données pour {selected_stock}..."):
                market_data = MarketDataProvider(selected_stock, period="1y")
                
                if market_data.data is None or market_data.data.empty:
                    st.error(f"❌ Impossible de récupérer les données pour {selected_stock}")
                    st.stop()
                
                summary = market_data.get_summary()
            
            # Afficher les infos de l'action
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("Prix Actuel", f"€{summary['price']:.2f}")
            with col_info2:
                st.metric("Volatilité Réelle", f"{summary['volatility_pct']:.1f}%")
            
            # Récupérer les valeurs de marché
            spot_price = summary['price']
            volatility = summary['volatility_pct']
            vol_decimal = summary['volatility'] / 100
            
            st.divider()
            st.subheader("🎛️ Paramètres Ajustables")
            
            # Taux d'intérêt
            interest_rate = st.slider("Taux d'Intérêt (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5)
            rate_decimal = interest_rate / 100
            
            # Délai d'expiration
            maturity = st.slider("Délai d'Expiration (années)", min_value=0.01, max_value=2.0, value=0.25, step=0.01)
            
            st.divider()
            st.subheader("⚡ Strikes (€)")
            st.info(f"💡 Prix actuel: €{spot_price:.2f} | Volatilité: {volatility:.1f}%")
            
            # Proposer des strikes suggérés
            suggest_strikes = st.checkbox("💡 Obtenir des strikes suggérés", value=True)
            
            if suggest_strikes:
                # Calculer les strikes suggérés (±10% et ±15% du prix)
                suggested_k1 = spot_price * 0.85
                suggested_k2 = spot_price * 0.9
                suggested_k3 = spot_price * 1.1
                suggested_k4 = spot_price * 1.15
                
                col1, col2 = st.columns(2)
                with col1:
                    K1 = st.number_input(
                        "K1 - Vendre Call (Le plus bas)",
                        min_value=10.0,
                        value=suggested_k1,
                        step=1.0,
                        help=f"Suggéré: €{suggested_k1:.2f}"
                    )
                    K3 = st.number_input(
                        "K3 - Acheter Call",
                        min_value=10.0,
                        value=suggested_k3,
                        step=1.0,
                        help=f"Suggéré: €{suggested_k3:.2f}"
                    )
                with col2:
                    K2 = st.number_input(
                        "K2 - Acheter Call",
                        min_value=10.0,
                        value=suggested_k2,
                        step=1.0,
                        help=f"Suggéré: €{suggested_k2:.2f}"
                    )
                    K4 = st.number_input(
                        "K4 - Vendre Call (Le plus haut)",
                        min_value=10.0,
                        value=suggested_k4,
                        step=1.0,
                        help=f"Suggéré: €{suggested_k4:.2f}"
                    )
            else:
                col1, col2 = st.columns(2)
                with col1:
                    K1 = st.number_input("K1 - Vendre Call (Le plus bas)", min_value=10.0, value=90.0, step=1.0)
                    K3 = st.number_input("K3 - Acheter Call", min_value=10.0, value=110.0, step=1.0)
                with col2:
                    K2 = st.number_input("K2 - Acheter Call", min_value=10.0, value=95.0, step=1.0)
                    K4 = st.number_input("K4 - Vendre Call (Le plus haut)", min_value=10.0, value=115.0, step=1.0)
            
            st.divider()
            st.subheader("💰 Gestion du Capital")
            capital = st.number_input("Capital Disponible (€)", min_value=1000, value=10000, step=500)
            
            st.divider()
            st.subheader("🎯 Précision du Modèle")
            N_steps = st.slider("Étapes Binomiales (N)", min_value=10, max_value=200, value=50, step=10)
        
        # ==================== MODE MANUEL ====================
        else:
            st.subheader("Conditions de Marché")
            spot_price = st.slider("Prix Spot (€)", min_value=50, max_value=500, value=100, step=1)
            volatility = st.slider("Volatilité (%)", min_value=5, max_value=100, value=30, step=1)
            interest_rate = st.slider("Taux d'Intérêt (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5)
            maturity = st.slider("Délai d'Expiration (années)", min_value=0.01, max_value=2.0, value=0.25, step=0.01)
            
            # Conversion des pourcentages en décimales
            vol_decimal = volatility / 100
            rate_decimal = interest_rate / 100
            
            # Prix d'Exercice
            st.subheader("Sélection des Strikes")
            st.info("K1 < K2 < K3 < K4 (Validation appliquée)")
            
            col1, col2 = st.columns(2)
            with col1:
                K1 = st.number_input("K1 - Vendre Call (Le plus bas)", min_value=10.0, value=90.0, step=1.0)
                K3 = st.number_input("K3 - Acheter Call", min_value=10.0, value=110.0, step=1.0)
            with col2:
                K2 = st.number_input("K2 - Acheter Call", min_value=10.0, value=95.0, step=1.0)
                K4 = st.number_input("K4 - Vendre Call (Le plus haut)", min_value=10.0, value=115.0, step=1.0)
            
            # Gestion du Capital
            st.subheader("Gestion du Capital")
            capital = st.number_input("Capital Disponible (€)", min_value=1000, value=10000, step=500)
            
            # Précision Binomiale
            st.subheader("Précision du Modèle")
            N_steps = st.slider("Étapes Binomiales (N)", min_value=10, max_value=200, value=50, step=10)
        
        st.divider()
        
        # Valider les strikes
        try:
            if not (K1 < K2 < K3 < K4):
                st.error("❌ Ordre des strikes invalide: K1 < K2 < K3 < K4")
                st.stop()
        except:
            st.error("Prix d'exercice invalides")
            st.stop()
    
    # ======================== CRÉER STRATÉGIE ========================
    try:
        params = StrategyParams(
            S=spot_price,
            K1=K1,
            K2=K2,
            K3=K3,
            K4=K4,
            r=rate_decimal,
            T=maturity,
            sigma=vol_decimal,
            N=N_steps
        )
        
        strategy = ShortCondor(params)
        executor = StrategyExecutor(capital)
        details = strategy.get_strategy_details()
        
    except Exception as e:
        st.error(f"Erreur de création de stratégie: {str(e)}")
        st.stop()
    
    # ======================== CONTENU PRINCIPAL: DISPOSITION 3 COLONNES ========================
    
    # Colonne 1: Résultats Financiers
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    with col1:
        st.subheader("💰 Évaluation de la Stratégie")
        
        net_cost = details["strategy_metrics"]["net_cost"]
        credit = details["strategy_metrics"]["net_credit"]
        
        if credit > 0:
            st.metric(
                "Crédit Net Reçu",
                f"€{credit:.2f}",
                delta=f"Par 100 parts",
                delta_color="normal"
            )
            st.success(f"✓ Stratégie de Crédit (Risque Réduit)")
        else:
            st.metric(
                "Débit Net Payé",
                f"€{-net_cost:.2f}",
                delta=f"Par 100 parts",
                delta_color="off"
            )
        
        st.divider()
        st.subheader("📊 Scénarios Extrêmes")
        
        max_profit = details["strategy_metrics"]["max_profit"]
        max_loss = details["strategy_metrics"]["max_loss"]
        
        col_profit, col_loss = st.columns(2)
        with col_profit:
            st.metric(
                "Profit Maximum",
                f"€{max_profit:.2f}",
                delta="Par contrat",
                delta_color="normal"
            )
        with col_loss:
            st.metric(
                "Perte Maximum",
                f"€{max_loss:.2f}",
                delta="Par contrat",
                delta_color="off"
            )
        
        st.divider()
        st.subheader("🎯 Points d'Équilibre")
        
        lower_be, upper_be = details["strategy_metrics"]["lower_breakeven"], details["strategy_metrics"]["upper_breakeven"]
        
        st.write(f"**Équilibre Bas:** €{lower_be:.2f}")
        st.write(f"**Équilibre Haut:** €{upper_be:.2f}")
        
        profit_zone_lower = details["strategy_metrics"]["profit_zone_lower"]
        profit_zone_upper = details["strategy_metrics"]["profit_zone_upper"]
        
        st.write(f"\n**Zone de Profit:** €{profit_zone_lower:.2f} - €{profit_zone_upper:.2f}")
    
    with col2:
        st.subheader("📈 Gestion du Capital")
        
        quantity = executor.max_quantity(strategy)
        execution = executor.get_execution_summary(strategy, quantity)
        
        st.metric(
            "Stratégies Max",
            f"{quantity}x",
            delta=f"Avec €{capital:.0f} de capital",
            delta_color="normal"
        )
        
        total_max_loss = execution["total_max_loss"]
        utilization = execution["capital_utilization_pct"]
        remaining = execution["capital_remaining"]
        
        st.metric(
            "Risque Max Total",
            f"€{total_max_loss:.2f}",
            delta=f"{utilization:.1f}% du capital",
            delta_color="normal"
        )
        
        st.metric(
            "Capital Restant",
            f"€{remaining:.2f}",
            delta=f"{100-utilization:.1f}% libre",
            delta_color="normal"
        )
        
        st.divider()
        st.subheader("🔧 Prix des Options Individuelles")
        
        options_df = pd.DataFrame({
            "Strike": [f"K1 (€{K1:.2f})", f"K2 (€{K2:.2f})", f"K3 (€{K3:.2f})", f"K4 (€{K4:.2f})"],
            "Type": ["VENDRE", "ACHETER", "ACHETER", "VENDRE"],
            "Prix (€)": [
                f"{details['option_prices']['call_K1']:.2f}",
                f"{details['option_prices']['call_K2']:.2f}",
                f"{details['option_prices']['call_K3']:.2f}",
                f"{details['option_prices']['call_K4']:.2f}"
            ]
        })
        
        st.dataframe(options_df, use_container_width=True, hide_index=True)
    
    with col3:
        st.subheader("📋 Résumé de la Stratégie")
        
        summary_data = {
            "Paramètre": [
                "Prix Spot",
                "Volatilité",
                "Taux d'Intérêt",
                "Temps d'Expiration",
                "Étapes Binomiales",
                "Capital",
                "Stratégies à Exécuter"
            ],
            "Valeur": [
                f"€{spot_price:.2f}",
                f"{volatility}%",
                f"{interest_rate}%",
                f"{maturity:.2f} ans",
                f"{N_steps}",
                f"€{capital:.2f}",
                f"{quantity}x"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Afficher la source des données
        if mode == "Mode Réel (Données de Marché)":
            st.info(f"📊 **Source:** Yahoo Finance | Mis à jour: {summary['date']}")
        
        st.subheader("📌 Logique de la Stratégie")
        
        st.markdown("""
        **Configuration Short Condor:**
        - **VENDRE** Call @ K1 (Crédit)
        - **ACHETER** Call @ K2 (Débit)
        - **ACHETER** Call @ K3 (Débit)
        - **VENDRE** Call @ K4 (Crédit)
        
        **Profit quand:** L'action reste entre K2-K3
        
        **Perte quand:** L'action se déplace au-delà de K1 ou K4
        
        **Utilisation:** Quand une haute volatilité est attendue
        """)
    
    # ======================== SECTION GRAPHIQUES ========================
    st.divider()
    st.header("📊 Visualisations")
    
    viz_col1, viz_col2 = st.columns([1, 1])
    
    # Graphique 1: Diagramme de Payoff
    with viz_col1:
        st.subheader("Diagramme de Payoff à l'Expiration")
        
        # Créer une plage de prix au comptant (typiquement ±30% du prix actuel)
        min_spot = spot_price * 0.7
        max_spot = spot_price * 1.3
        spot_range = np.linspace(min_spot, max_spot, 200)
        
        payoff = strategy.payoff_curve(spot_range)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Tracer la courbe de payoff
        ax.plot(spot_range, payoff, linewidth=2.5, color="#3498db", label="P&L Stratégie", zorder=3)
        
        # Remplir les zones de profit et de perte
        ax.fill_between(spot_range, 0, payoff, where=(payoff >= 0), alpha=0.3, color="#2ecc71", label="Zone de Profit", zorder=1)
        ax.fill_between(spot_range, 0, payoff, where=(payoff < 0), alpha=0.3, color="#e74c3c", label="Zone de Perte", zorder=1)
        
        # Ajouter les lignes de strike
        ax.axvline(K1, color="red", linestyle="--", linewidth=1, alpha=0.7, label=f"K1=€{K1:.2f} (Vendre)")
        ax.axvline(K2, color="orange", linestyle="--", linewidth=1, alpha=0.7, label=f"K2=€{K2:.2f} (Acheter)")
        ax.axvline(K3, color="orange", linestyle="--", linewidth=1, alpha=0.7, label=f"K3=€{K3:.2f} (Acheter)")
        ax.axvline(K4, color="red", linestyle="--", linewidth=1, alpha=0.7, label=f"K4=€{K4:.2f} (Vendre)")
        
        # Prix spot actuel
        ax.axvline(spot_price, color="green", linestyle="-", linewidth=2, alpha=0.8, label=f"Prix Actuel=€{spot_price:.2f}")
        
        ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("Prix de l'Action à l'Expiration (€)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Profit/Perte (€)", fontsize=11, fontweight="bold")
        ax.set_title(f"Payoff Short Condor à l'Expiration (T={maturity} ans)", fontsize=12, fontweight="bold")
        ax.legend(loc="upper left", fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # Graphique 2: Sensibilité à la Volatilité
    with viz_col2:
        st.subheader("Sensibilité à la Volatilité")
        
        # Tester une plage de volatilité
        vol_range = np.linspace(0.05, 1.0, 50)
        strategy_prices = []
        
        for vol in vol_range:
            temp_params = StrategyParams(
                S=spot_price,
                K1=K1,
                K2=K2,
                K3=K3,
                K4=K4,
                r=rate_decimal,
                T=maturity,
                sigma=vol,
                N=N_steps
            )
            temp_strategy = ShortCondor(temp_params)
            strategy_prices.append(temp_strategy.strategy_cost())
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(vol_range * 100, strategy_prices, linewidth=2.5, color="#9b59b6", marker="o", markersize=4)
        
        # Mettre en surbrillance la volatilité actuelle
        current_vol_idx = np.argmin(np.abs(vol_range - vol_decimal))
        ax.scatter(volatility, strategy_prices[current_vol_idx], color="red", s=100, zorder=5, label=f"Vol Actuelle={volatility}%")
        
        ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("Volatilité (%)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Coût de la Stratégie (€)", fontsize=11, fontweight="bold")
        ax.set_title("Prix Short Condor vs Volatilité", fontsize=12, fontweight="bold")
        ax.legend(fontsize=9)
        
        # Ajouter l'ombrage pour profit/perte
        ax.fill_between(vol_range * 100, 0, strategy_prices, where=(np.array(strategy_prices) < 0), 
                         alpha=0.2, color="#2ecc71", label="Crédit Reçu")
        ax.fill_between(vol_range * 100, 0, strategy_prices, where=(np.array(strategy_prices) >= 0), 
                         alpha=0.2, color="#e74c3c", label="Débit Payé")
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # ======================== GREEKS EVOLUTION ========================
    st.divider()
    st.header("📈 Évolution des Greeks")
    st.markdown("*Comprendre comment les risques changent avec le prix de l'action*")
    
    try:
        # Créer une range de prix pour les Greeks
        spot_range_greeks = np.linspace(spot_price * 0.7, spot_price * 1.3, 50)
        
        # Calculer les Greeks pour la stratégie Short Condor
        # On va calculer les Greeks pour chaque leg et les combiner
        
        delta_condor = []
        gamma_condor = []
        theta_condor = []
        vega_condor = []
        
        for S in spot_range_greeks:
            # Créer un model temporaire pour ce spot
            model = BinomialModel(
                S=S, K=K1, T=maturity, r=interest_rate, 
                sigma=volatility, N=N_steps
            )
            
            # Calculer les Greeks pour chaque leg
            greeks_k1_call = model.calculate_greeks(np.array([S]), 'call')
            
            model_k2 = BinomialModel(S=S, K=K2, T=maturity, r=interest_rate, 
                                     sigma=volatility, N=N_steps)
            greeks_k2_call = model_k2.calculate_greeks(np.array([S]), 'call')
            
            model_k3 = BinomialModel(S=S, K=K3, T=maturity, r=interest_rate, 
                                     sigma=volatility, N=N_steps)
            greeks_k3_put = model_k3.calculate_greeks(np.array([S]), 'put')
            
            model_k4 = BinomialModel(S=S, K=K4, T=maturity, r=interest_rate, 
                                     sigma=volatility, N=N_steps)
            greeks_k4_put = model_k4.calculate_greeks(np.array([S]), 'put')
            
            # Short Condor: Vendre K1 Call, Acheter K2 Call, Acheter K3 Put, Vendre K4 Put
            delta = -greeks_k1_call['delta'][0] + greeks_k2_call['delta'][0] + greeks_k3_put['delta'][0] - greeks_k4_put['delta'][0]
            gamma = -greeks_k1_call['gamma'][0] + greeks_k2_call['gamma'][0] + greeks_k3_put['gamma'][0] - greeks_k4_put['gamma'][0]
            theta = -greeks_k1_call['theta'][0] + greeks_k2_call['theta'][0] + greeks_k3_put['theta'][0] - greeks_k4_put['theta'][0]
            vega = -greeks_k1_call['vega'][0] + greeks_k2_call['vega'][0] + greeks_k3_put['vega'][0] - greeks_k4_put['vega'][0]
            
            delta_condor.append(delta)
            gamma_condor.append(gamma)
            theta_condor.append(theta)
            vega_condor.append(vega)
        
        # Créer le graphique Plotly interactif
        fig_greeks = go.Figure()
        
        # Ajouter les courbes des Greeks
        fig_greeks.add_trace(go.Scatter(
            x=spot_range_greeks, y=delta_condor,
            mode='lines', name='Delta (Δ)',
            line=dict(color='#007AFF', width=3),
            hovertemplate='<b>Prix: €%{x:.2f}</b><br>Delta: %{y:.4f}<extra></extra>'
        ))
        
        fig_greeks.add_trace(go.Scatter(
            x=spot_range_greeks, y=gamma_condor,
            mode='lines', name='Gamma (Γ)',
            line=dict(color='#34C759', width=3),
            hovertemplate='<b>Prix: €%{x:.2f}</b><br>Gamma: %{y:.4f}<extra></extra>'
        ))
        
        fig_greeks.add_trace(go.Scatter(
            x=spot_range_greeks, y=theta_condor,
            mode='lines', name='Theta (Θ)',
            line=dict(color='#FF9500', width=3),
            hovertemplate='<b>Prix: €%{x:.2f}</b><br>Theta: %{y:.4f}<extra></extra>'
        ))
        
        fig_greeks.add_trace(go.Scatter(
            x=spot_range_greeks, y=vega_condor,
            mode='lines', name='Vega (ν)',
            line=dict(color='#FF3B30', width=3),
            hovertemplate='<b>Prix: €%{x:.2f}</b><br>Vega: %{y:.4f}<extra></extra>'
        ))
        
        # Ajouter une ligne pour le prix spot actuel
        fig_greeks.add_vline(x=spot_price, line_dash="dash", line_color="gray", 
                            annotation_text="Prix Actuel", annotation_position="top right")
        
        # Ajouter les zones de strike
        for strike, color, name in [(K1, "#FF3B30", "K1 (Vendre)"), 
                                     (K2, "#FF9500", "K2 (Acheter)"),
                                     (K3, "#FF9500", "K3 (Acheter)"),
                                     (K4, "#FF3B30", "K4 (Vendre)")]:
            fig_greeks.add_vline(x=strike, line_dash="dot", line_color=color, opacity=0.3,
                                annotation_text=name, annotation_position="bottom right")
        
        # Configurer le layout
        fig_greeks.update_layout(
            title="Évolution des Greeks Short Condor",
            xaxis_title="Prix de l'Action à l'Expiration (€)",
            yaxis_title="Valeur du Greek",
            hovermode='x unified',
            height=500,
            template='plotly_white',
            font=dict(size=12),
            plot_bgcolor='rgba(245, 245, 247, 0.5)',
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig_greeks, use_container_width=True)
        
        # Ajouter une explication des Greeks
        with st.expander("📚 Comprendre les Greeks"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**Delta (Δ)**")
                st.markdown("Combien l'option change vs l'action. Entre -1 et +1.")
                st.metric("Valeur actuelle", f"{delta_condor[np.argmin(np.abs(spot_range_greeks - spot_price))]:.4f}")
            
            with col2:
                st.markdown("**Gamma (Γ)**")
                st.markdown("Rapidité du changement du Delta. Plus élevé = plus risqué.")
                st.metric("Valeur actuelle", f"{gamma_condor[np.argmin(np.abs(spot_range_greeks - spot_price))]:.4f}")
            
            with col3:
                st.markdown("**Theta (Θ)**")
                st.markdown("Gain/Perte par jour (time decay). Positif = gagne avec le temps.")
                st.metric("€/jour", f"{theta_condor[np.argmin(np.abs(spot_range_greeks - spot_price))]:.4f}")
            
            with col4:
                st.markdown("**Vega (ν)**")
                st.markdown("Sensibilité à la volatilité. Positif = gagne si vol monte.")
                st.metric("Valeur actuelle", f"{vega_condor[np.argmin(np.abs(spot_range_greeks - spot_price))]:.4f}")
    
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du calcul des Greeks: {str(e)}")
    
    # ======================== TABLE D'ANALYSE P&L ========================
    st.divider()
    st.header("📊 Analyse P&L")
    
    col_pnl1, col_pnl2 = st.columns([1, 1])
    
    with col_pnl1:
        st.subheader("Analyse par Scénarios")
        
        # Créer des scénarios
        scenarios = [
            ("Crash (S -20%)", spot_price * 0.8),
            ("Baisse (S -10%)", spot_price * 0.9),
            ("Prix Actuel", spot_price),
            ("Hausse (S +10%)", spot_price * 1.1),
            ("Pic (S +20%)", spot_price * 1.2),
        ]
        
        pnl_data = []
        for scenario_name, spot_at_exp in scenarios:
            pnl = strategy.payoff_at_maturity(spot_at_exp) * quantity * 100
            pnl_data.append({
                "Scénario": scenario_name,
                "Prix de l'Action": f"€{spot_at_exp:.2f}",
                "P&L (€)": f"{pnl:,.2f}",
                "Rendement": f"{(pnl/capital)*100:.2f}%"
            })
        
        pnl_df = pd.DataFrame(pnl_data)
        st.dataframe(pnl_df, use_container_width=True, hide_index=True)
    
    with col_pnl2:
        st.subheader("Zones de Profit Historiques")
        
        # Définir les niveaux de prix clés
        key_levels = {
            "S = K1 (Équilibre Bas)": K1,
            "S = K2 (Début Profit)": K2,
            "S = Spot (Actuel)": spot_price,
            "S = K3 (Fin Profit)": K3,
            "S = K4 (Équilibre Haut)": K4,
        }
        
        levels_data = []
        for level_name, level_price in key_levels.items():
            pnl = strategy.payoff_at_maturity(level_price) * quantity * 100
            status = "✓ PROFIT" if pnl > 0 else ("✗ PERTE" if pnl < 0 else "- NEUTRE")
            levels_data.append({
                "Niveau de Prix": level_name,
                "Prix de l'Action": f"€{level_price:.2f}",
                "P&L (€)": f"{pnl:,.2f}",
                "Statut": status
            })
        
        levels_df = pd.DataFrame(levels_data)
        st.dataframe(levels_df, use_container_width=True, hide_index=True)
    
    # ======================== PIED DE PAGE ========================
    st.divider()
    st.markdown("""
    ---
    **Analyseur de Stratégie Short Condor v1.0**
    
    *Construit avec Streamlit | Modèle d'Évaluation: Binomial (Cox-Ross-Rubinstein)*
    
    ⚠️ **Avertissement:** Cet outil est fourni à des fins éducatives et de démonstration uniquement.
    Ce n'est pas un conseil financier. Consultez toujours un conseiller financier qualifié avant de négocier.
    """)


if __name__ == "__main__":
    main()
