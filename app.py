from __future__ import annotations

import io
import json
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from binomial_engine import BinomialModel, MultiLegGreeksCalculator
from strategy_manager import StrategyParams, ShortIronCondor, StrategyExecutor
from market_data import MarketDataProvider, AVAILABLE_STOCKS


st.set_page_config(
    page_title="Short Iron Condor - Pricer Binomial (CRR)",
    layout="wide",
    initial_sidebar_state="expanded",
)


def triangular_dict_to_df(level_dict: dict, N: int) -> pd.DataFrame:
    """
    Convertit un arbre stocké en dictionnaire triangulaire {i:{j:val}}
    en tableau lisible (DataFrame).
    - i = niveau de temps (0..N)
    - j = nombre de mouvements "up" (0..i)
    """
    data = []
    for i in range(N + 1):
        row = []
        for j in range(N + 1):
            if i in level_dict and j in level_dict[i]:
                row.append(level_dict[i][j])
            else:
                row.append(np.nan)
        data.append(row)

    df = pd.DataFrame(data, columns=[f"j={j}" for j in range(N + 1)])
    df.insert(0, "niveau i", [f"i={i}" for i in range(N + 1)])
    return df


def generate_export_data(
    spot_price, K1, K2, K3, K4,
    rate_pct, expiration_years,
    volatility_pct, num_steps,
    quantity, multiplier,
    strategy: ShortIronCondor,
    current_greeks_ui,
    greeks_curve_ui,
    spot_range
):
    return {
        "timestamp": datetime.now().isoformat(),
        "strategy_type": "Short Iron Condor",
        "strategy_config": {
            "spot_price": float(spot_price),
            "K1": float(K1),
            "K2": float(K2),
            "K3": float(K3),
            "K4": float(K4),
            "interest_rate_pct": float(rate_pct),
            "time_to_expiration_years": float(expiration_years),
            "volatility_pct": float(volatility_pct),
            "binomial_steps": int(num_steps),
            "quantity_contracts": int(quantity),
            "multiplier": int(multiplier),
        },
        "current_greeks_ui": {
            "delta": float(current_greeks_ui["delta"]),
            "gamma": float(current_greeks_ui["gamma"]),
            "theta_per_day": float(current_greeks_ui["theta_per_day"]),
            "vega_per_1pct_vol": float(current_greeks_ui["vega_per_1pct_vol"]),
        },
        "greeks_curve_ui": {
            "spot_prices": [float(x) for x in spot_range.tolist()],
            "delta": [float(x) for x in greeks_curve_ui["delta"].tolist()],
            "gamma": [float(x) for x in greeks_curve_ui["gamma"].tolist()],
            "theta_per_day": [float(x) for x in greeks_curve_ui["theta_per_day"].tolist()],
            "vega_per_1pct_vol": [float(x) for x in greeks_curve_ui["vega_per_1pct_vol"].tolist()],
            "payoff_per_contract": [float(strategy.payoff_at_maturity(s) * multiplier) for s in spot_range],
        },
        "scenarios_total_pnl_eur": {
            "crash_20": float(strategy.payoff_at_maturity(spot_price * 0.8) * quantity * multiplier),
            "down_10": float(strategy.payoff_at_maturity(spot_price * 0.9) * quantity * multiplier),
            "current": float(strategy.payoff_at_maturity(spot_price) * quantity * multiplier),
            "up_10": float(strategy.payoff_at_maturity(spot_price * 1.1) * quantity * multiplier),
            "peak_20": float(strategy.payoff_at_maturity(spot_price * 1.2) * quantity * multiplier),
        },
    }


def export_to_json(export_data) -> str:
    return json.dumps(export_data, indent=2)


def export_to_csv(export_data) -> str:
    csv_buffer = io.StringIO()
    cfg = export_data["strategy_config"]
    g = export_data["current_greeks_ui"]
    scen = export_data["scenarios_total_pnl_eur"]

    csv_buffer.write("CONFIGURATION\n")
    csv_buffer.write(f"Timestamp,{export_data['timestamp']}\n")
    csv_buffer.write(f"Strategy,{export_data['strategy_type']}\n")
    csv_buffer.write(f"Spot,€{cfg['spot_price']}\n")
    csv_buffer.write(f"K1,€{cfg['K1']}\n")
    csv_buffer.write(f"K2,€{cfg['K2']}\n")
    csv_buffer.write(f"K3,€{cfg['K3']}\n")
    csv_buffer.write(f"K4,€{cfg['K4']}\n")
    csv_buffer.write(f"Rate (%),{cfg['interest_rate_pct']}\n")
    csv_buffer.write(f"T (years),{cfg['time_to_expiration_years']}\n")
    csv_buffer.write(f"Vol (%),{cfg['volatility_pct']}\n")
    csv_buffer.write(f"N steps,{cfg['binomial_steps']}\n")
    csv_buffer.write(f"Quantity,{cfg['quantity_contracts']}\n")
    csv_buffer.write(f"Multiplier,{cfg['multiplier']}\n\n")

    csv_buffer.write("GREEKS (UI)\n")
    csv_buffer.write(f"Delta,{g['delta']}\n")
    csv_buffer.write(f"Gamma,{g['gamma']}\n")
    csv_buffer.write(f"Theta/day,{g['theta_per_day']}\n")
    csv_buffer.write(f"Vega(+1%),{g['vega_per_1pct_vol']}\n\n")

    csv_buffer.write("SCENARIOS (TOTAL P&L)\n")
    csv_buffer.write(f"Crash -20%,{scen['crash_20']}\n")
    csv_buffer.write(f"Down -10%,{scen['down_10']}\n")
    csv_buffer.write(f"Current,{scen['current']}\n")
    csv_buffer.write(f"Up +10%,{scen['up_10']}\n")
    csv_buffer.write(f"Peak +20%,{scen['peak_20']}\n")

    return csv_buffer.getvalue()


def export_to_pdf(export_data, capital: float) -> bytes:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2ca02c"),
        spaceAfter=6,
        spaceBefore=8,
        fontName="Helvetica-Bold",
    )
    normal_style = styles["Normal"]

    elements = []
    elements.append(Paragraph("Rapport - Short Iron Condor (Binomial CRR)", title_style))
    elements.append(Spacer(1, 0.15 * inch))

    cfg = export_data["strategy_config"]
    elements.append(Paragraph(f"<b>Généré :</b> {export_data['timestamp']}", normal_style))
    elements.append(Paragraph(f"<b>Stratégie :</b> {export_data['strategy_type']}", normal_style))
    elements.append(Spacer(1, 0.12 * inch))

    elements.append(Paragraph("Paramètres", heading_style))
    config_data = [
        ["Paramètre", "Valeur"],
        ["Spot", f"€{cfg['spot_price']:.2f}"],
        ["K1", f"€{cfg['K1']:.2f}"],
        ["K2", f"€{cfg['K2']:.2f}"],
        ["K3", f"€{cfg['K3']:.2f}"],
        ["K4", f"€{cfg['K4']:.2f}"],
        ["Taux", f"{cfg['interest_rate_pct']:.2f}%"],
        ["Maturité T", f"{cfg['time_to_expiration_years']:.4f} ans"],
        ["Volatilité", f"{cfg['volatility_pct']:.2f}%"],
        ["Pas binomial N", f"{cfg['binomial_steps']}"],
        ["Quantité", f"{cfg['quantity_contracts']}"],
        ["Multiplicateur", f"{cfg['multiplier']}"],
        ["Capital", f"€{capital:.2f}"],
    ]
    t = Table(config_data, colWidths=[2.8 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.15 * inch))

    elements.append(Paragraph("Greeks (unités affichées dans l'application)", heading_style))
    g = export_data["current_greeks_ui"]
    tg = Table(
        [
            ["Delta", f"{g['delta']:.6f}", "par €1 de spot"],
            ["Gamma", f"{g['gamma']:.6e}", "par €1²"],
            ["Theta/jour", f"{g['theta_per_day']:.6f}", "par jour"],
            ["Vega (+1%)", f"{g['vega_per_1pct_vol']:.6f}", "par +1% vol"],
        ],
        colWidths=[1.4 * inch, 2.0 * inch, 1.8 * inch],
    )
    tg.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightblue),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(tg)

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def main():
    st.title("Short Iron Condor - Pricer Binomial (CRR)")
    st.write("But : pricer la stratégie en binomial, afficher un arbre binomial, et analyser les Greeks.")

    mode = st.radio(
        "Mode d'utilisation",
        ["Mode manuel", "Mode marché (Yahoo Finance)"],
        horizontal=True,
    )

    with st.sidebar:
        st.header("Paramètres")
        st.subheader("Conditions de marché")

        if mode == "Mode marché (Yahoo Finance)":
            selected_stock = st.selectbox(
                "Action",
                list(AVAILABLE_STOCKS.keys()),
                format_func=lambda x: f"{x} - {AVAILABLE_STOCKS[x]}",
            )

            with st.spinner("Récupération des données de marché..."):
                market_data = MarketDataProvider(selected_stock, period="1y")
                if market_data.data is None or market_data.data.empty:
                    st.error("Impossible de récupérer les données (Yahoo Finance).")
                    st.stop()
                summary = market_data.get_summary()

            spot_price = float(summary["price"])
            vol_decimal = float(summary["volatility"])
            volatility_pct = float(summary["volatility_pct"])

            st.write(f"Spot : {spot_price:.2f}")
            st.write(f"Volatilité réalisée : {volatility_pct:.1f}%")

            interest_rate_pct = st.slider("Taux sans risque (%)", 0.0, 10.0, 2.5, 0.5)
            rate_decimal = float(interest_rate_pct) / 100.0
            maturity = st.slider("Maturité (années)", 0.01, 2.0, 0.25, 0.01)

            st.divider()
            st.subheader("Strikes (K1 < K2 < K3 < K4)")
            suggest = st.checkbox("Proposition automatique", value=True)
            if suggest:
                K1 = st.number_input("K1 (long put)", min_value=1.0, value=float(spot_price * 0.90), step=1.0)
                K2 = st.number_input("K2 (short put)", min_value=1.0, value=float(spot_price * 0.95), step=1.0)
                K3 = st.number_input("K3 (short call)", min_value=1.0, value=float(spot_price * 1.05), step=1.0)
                K4 = st.number_input("K4 (long call)", min_value=1.0, value=float(spot_price * 1.10), step=1.0)
            else:
                K1 = st.number_input("K1", min_value=1.0, value=90.0, step=1.0)
                K2 = st.number_input("K2", min_value=1.0, value=95.0, step=1.0)
                K3 = st.number_input("K3", min_value=1.0, value=105.0, step=1.0)
                K4 = st.number_input("K4", min_value=1.0, value=110.0, step=1.0)

        else:
            spot_price = float(st.slider("Spot (€)", 50, 500, 100, 1))
            volatility_pct = float(st.slider("Volatilité (%)", 5, 100, 30, 1))
            interest_rate_pct = st.slider("Taux sans risque (%)", 0.0, 10.0, 2.5, 0.5)
            maturity = st.slider("Maturité (années)", 0.01, 2.0, 0.25, 0.01)

            vol_decimal = float(volatility_pct) / 100.0
            rate_decimal = float(interest_rate_pct) / 100.0

            st.divider()
            st.subheader("Strikes (K1 < K2 < K3 < K4)")
            K1 = st.number_input("K1 (long put)", min_value=1.0, value=90.0, step=1.0)
            K2 = st.number_input("K2 (short put)", min_value=1.0, value=95.0, step=1.0)
            K3 = st.number_input("K3 (short call)", min_value=1.0, value=105.0, step=1.0)
            K4 = st.number_input("K4 (long call)", min_value=1.0, value=110.0, step=1.0)

        st.divider()
        capital = st.number_input("Capital (€)", min_value=1000, value=10000, step=500)
        N_steps = st.slider("Pas binomial N", 10, 300, 100, 10)

        if not (K1 < K2 < K3 < K4):
            st.error("Ordre des strikes invalide : il faut K1 < K2 < K3 < K4")
            st.stop()

    params = StrategyParams(
        S=float(spot_price),
        K1=float(K1), K2=float(K2), K3=float(K3), K4=float(K4),
        r=float(rate_decimal),
        T=float(maturity),
        sigma=float(vol_decimal),
        N=int(N_steps),
        multiplier=100,
    )

    strategy = ShortIronCondor(params)
    executor = StrategyExecutor(float(capital))
    details = strategy.get_strategy_details()

    st.subheader("Présentation de la stratégie")
    st.write(
        "Short Iron Condor : on vend un put (K2) et un call (K3), et on achète les ailes (K1 et K4) pour limiter le risque. "
        "On gagne surtout si le sous-jacent termine entre K2 et K3."
    )

    st.divider()
    st.subheader("Jambes de la stratégie")
    legs_df = pd.DataFrame(details["legs"])
    st.dataframe(legs_df, width="stretch", hide_index=True)

    multiplier = params.multiplier

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Prix (binomial CRR)")
        net_cost_per_share = float(details["net_cost"])
        net_cost_per_contract = net_cost_per_share * multiplier

        if net_cost_per_share < 0:
            st.metric("Crédit net (€/contrat)", f"{-net_cost_per_contract:.2f}")
        else:
            st.metric("Débit net (€/contrat)", f"{net_cost_per_contract:.2f}")

        st.divider()
        st.subheader("Profit / perte maximale à l'échéance")
        st.metric("Profit max (€/contrat)", f"{float(details['max_profit']) * multiplier:.2f}")
        st.metric("Perte max (€/contrat)", f"{abs(float(details['max_loss']) * multiplier):.2f}")

        st.divider()
        st.subheader("Points morts (breakevens)")
        be = details["breakeven_points"]
        if len(be) >= 2:
            st.write(f"BE bas : {be[0]:.2f}")
            st.write(f"BE haut : {be[-1]:.2f}")
            st.write(f"Zone centrale : {K2:.2f} → {K3:.2f}")
        else:
            st.write("Points morts non détectés (paramètres atypiques).")

    with c2:
        st.subheader("Gestion du capital")
        quantity = executor.max_quantity(strategy)
        exec_sum = executor.get_execution_summary(strategy, quantity)

        st.metric("Nombre maximum de contrats", f"{quantity}")
        st.metric("Perte max totale (€)", f"{exec_sum['total_max_loss']:.2f}")
        st.metric("Utilisation du capital (%)", f"{exec_sum['capital_utilization_pct']:.1f}%")
        st.metric("Capital restant (€)", f"{exec_sum['capital_remaining']:.2f}")

        st.divider()
        st.subheader("Prix des options (binomial CRR)")

        def price_leg(opt_type: str, strike: float) -> float:
            m = BinomialModel(
                S=float(spot_price),
                K=float(strike),
                r=float(rate_decimal),
                T=float(maturity),
                sigma=float(vol_decimal),
                N=int(N_steps),
            )
            return m.price_call() if opt_type == "call" else m.price_put()

        legs_desc = [("put", +1, K1), ("put", -1, K2), ("call", -1, K3), ("call", +1, K4)]

        rows = []
        for opt, sign, K in legs_desc:
            px = price_leg(opt, K)
            rows.append({
                "Option": f"{opt.upper()} @ {K:.2f}",
                "Position": "LONG" if sign > 0 else "SHORT",
                "Prix €/action": float(px),
                "Prix €/contrat": float(px * multiplier),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.divider()
    st.header("Payoff à l'échéance")

    min_spot = float(spot_price) * 0.7
    max_spot = float(spot_price) * 1.3
    spot_range = np.linspace(min_spot, max_spot, 250)

    payoff_contract = strategy.payoff_curve(spot_range) * multiplier
    payoff_profit = np.where(payoff_contract >= 0, payoff_contract, np.nan)
    payoff_loss = np.where(payoff_contract < 0, payoff_contract, np.nan)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot_range, y=payoff_profit,
        mode="lines", name="Gain",
        line=dict(color="green", width=3),
        fill="tozeroy", fillcolor="rgba(0, 128, 0, 0.18)",
        hovertemplate="Spot: €%{x:.2f}<br>P&L: €%{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=spot_range, y=payoff_loss,
        mode="lines", name="Perte",
        line=dict(color="red", width=3),
        fill="tozeroy", fillcolor="rgba(255, 0, 0, 0.18)",
        hovertemplate="Spot: €%{x:.2f}<br>P&L: €%{y:.2f}<extra></extra>",
    ))

    fig.add_hline(y=0, line_width=1, line_color="gray", opacity=0.6)
    for k in [K1, K2, K3, K4]:
        fig.add_vline(x=float(k), line_dash="dash", line_color="gray", opacity=0.6)
    fig.add_vline(x=float(spot_price), line_dash="dot", line_color="black", opacity=0.7)

    fig.update_layout(
        title="Payoff à l'échéance",
        xaxis_title="Spot à l'échéance",
        yaxis_title="P&L (€ / contrat)",
        hovermode="x unified",
        height=420,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.header("Arbres binomiaux (affichage)")

    with st.expander("Afficher un arbre binomial (N réduit pour l'affichage)"):
        tree_N = st.slider("Nombre de pas pour l'affichage (N ≤ 10)", 1, 10, 5, 1)
        tree_leg = st.selectbox("Jambe à afficher", options=["K1 (put)", "K2 (put)", "K3 (call)", "K4 (call)"], index=1)

        if "K1" in tree_leg:
            legK, legType = K1, "put"
        elif "K2" in tree_leg:
            legK, legType = K2, "put"
        elif "K3" in tree_leg:
            legK, legType = K3, "call"
        else:
            legK, legType = K4, "call"

        model_tree = BinomialModel(
            S=float(spot_price),
            K=float(legK),
            r=float(rate_decimal),
            T=float(maturity),
            sigma=float(vol_decimal),
            N=int(tree_N),
        )
        tree = model_tree.get_tree_data()
        if "error" in tree:
            st.error(tree["error"])
        else:
            st.caption(f"Option affichée : {legType.upper()} (K={legK:.2f}), N={tree_N}")

            stock_df = triangular_dict_to_df(tree["stock_prices"], tree_N)
            st.subheader("Arbre des prix du sous-jacent")
            st.dataframe(stock_df, width="stretch")

            opt_key = "call_prices" if legType == "call" else "put_prices"
            opt_df = triangular_dict_to_df(tree[opt_key], tree_N)
            st.subheader(f"Arbre des prix d'option ({legType.upper()})")
            st.dataframe(opt_df, width="stretch")

    st.divider()
    st.header("Greeks (binomial, différences finies)")

    spot_range_g = np.linspace(spot_price * 0.7, spot_price * 1.3, 60)

    legs_config = [
        {"K": K1, "type": "put", "sign": +1},
        {"K": K2, "type": "put", "sign": -1},
        {"K": K3, "type": "call", "sign": -1},
        {"K": K4, "type": "call", "sign": +1},
    ]

    greeks_calc = MultiLegGreeksCalculator(
        spot_range=spot_range_g,
        legs=legs_config,
        interest_rate=rate_decimal,
        time_to_maturity=maturity,
        volatility=vol_decimal,
        n_steps=N_steps,
    )
    g_curve = greeks_calc.calculate_strategy_greeks()

    delta = g_curve["delta"]
    gamma = g_curve["gamma"]
    theta_day = g_curve["theta"] / 365.0
    vega_1pct = g_curve["vega"] / 100.0

    def axis_range(arr):
        m = float(np.max(np.abs(arr)))
        if m == 0:
            return [-0.01, 0.01]
        return [float(np.min(arr) - 0.2 * m), float(np.max(arr) + 0.2 * m)]

    colA, colB = st.columns(2)
    with colA:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=spot_range_g, y=delta, mode="lines", fill="tozeroy", name="Delta"))
        fig1.add_hline(y=0, line_dash="dash", opacity=0.3)
        fig1.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        fig1.update_layout(height=300, xaxis_title="Spot", yaxis_title="Delta", yaxis=dict(range=axis_range(delta)))
        st.plotly_chart(fig1, width="stretch")

    with colB:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=spot_range_g, y=gamma, mode="lines", fill="tozeroy", name="Gamma"))
        fig2.add_hline(y=0, line_dash="dash", opacity=0.3)
        fig2.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        fig2.update_layout(height=300, xaxis_title="Spot", yaxis_title="Gamma", yaxis=dict(range=axis_range(gamma)))
        st.plotly_chart(fig2, width="stretch")

    colC, colD = st.columns(2)
    with colC:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=spot_range_g, y=theta_day, mode="lines", fill="tozeroy", name="Theta/jour"))
        fig3.add_hline(y=0, line_dash="dash", opacity=0.3)
        fig3.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        fig3.update_layout(height=300, xaxis_title="Spot", yaxis_title="Theta/jour", yaxis=dict(range=axis_range(theta_day)))
        st.plotly_chart(fig3, width="stretch")

    with colD:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=spot_range_g, y=vega_1pct, mode="lines", fill="tozeroy", name="Vega (+1%)"))
        fig4.add_hline(y=0, line_dash="dash", opacity=0.3)
        fig4.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        fig4.update_layout(height=300, xaxis_title="Spot", yaxis_title="Vega (+1%)", yaxis=dict(range=axis_range(vega_1pct)))
        st.plotly_chart(fig4, width="stretch")

    st.subheader("Greeks au spot actuel (unités affichées)")
    g0 = greeks_calc.get_greeks_at_spot(float(spot_price))
    current_greeks_ui = {
        "delta": g0["delta"],
        "gamma": g0["gamma"],
        "theta_per_day": g0["theta"] / 365.0,
        "vega_per_1pct_vol": g0["vega"] / 100.0,
    }

    a, b, c, d = st.columns(4)
    a.metric("Delta", f"{current_greeks_ui['delta']:.6f}")
    b.metric("Gamma", f"{current_greeks_ui['gamma']:.6e}")
    c.metric("Theta/jour", f"{current_greeks_ui['theta_per_day']:.6f}")
    d.metric("Vega (+1%)", f"{current_greeks_ui['vega_per_1pct_vol']:.6f}")

    st.divider()
    st.header("Export")

    greeks_curve_ui = {
        "delta": delta,
        "gamma": gamma,
        "theta_per_day": theta_day,
        "vega_per_1pct_vol": vega_1pct,
    }

    export_data = generate_export_data(
        spot_price=spot_price, K1=K1, K2=K2, K3=K3, K4=K4,
        rate_pct=interest_rate_pct,
        expiration_years=maturity,
        volatility_pct=volatility_pct,
        num_steps=N_steps,
        quantity=executor.max_quantity(strategy),
        multiplier=multiplier,
        strategy=strategy,
        current_greeks_ui=current_greeks_ui,
        greeks_curve_ui=greeks_curve_ui,
        spot_range=spot_range_g,
    )

    colx, coly, colz = st.columns(3)
    with colx:
        st.subheader("JSON")
        st.download_button(
            "Télécharger (JSON)",
            data=export_to_json(export_data),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            width="stretch",
        )

    with coly:
        st.subheader("CSV")
        st.download_button(
            "Télécharger (CSV)",
            data=export_to_csv(export_data),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width="stretch",
        )

    with colz:
        st.subheader("PDF")
        st.download_button(
            "Télécharger (PDF)",
            data=export_to_pdf(export_data, capital=float(capital)),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            width="stretch",
        )


if __name__ == "__main__":
    main()
