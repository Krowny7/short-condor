# app.py
"""
Application Streamlit - Short Iron Condor (Binomial CRR)

Objectifs projet (consigne) :
- Pricer la stratégie en binomial (CRR).
- Afficher des arbres binomiaux (sur une version réduite N<=10).
- Ajouter les Greeks (différences finies via binomial).
- Démonstration orale : expliquer quand la stratégie est profitable, risques, limites.
"""

import json
import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from binomial_engine import BinomialModel, MultiLegGreeksCalculator
from strategy_manager import StrategyParams, ShortIronCondor, StrategyExecutor

from market_data import MarketDataProvider, AVAILABLE_STOCKS


# ---------- Compat Streamlit (évite warnings / casse selon versions) ----------
def st_df(df: pd.DataFrame, **kwargs):
    try:
        return st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        return st.dataframe(df, use_container_width=True, **kwargs)


def st_plot(fig, **kwargs):
    try:
        return st.plotly_chart(fig, width="stretch", **kwargs)
    except TypeError:
        return st.plotly_chart(fig, use_container_width=True, **kwargs)


def st_download(*, label: str, data, file_name: str, mime: str):
    try:
        return st.download_button(label=label, data=data, file_name=file_name, mime=mime, width="stretch")
    except TypeError:
        return st.download_button(label=label, data=data, file_name=file_name, mime=mime, use_container_width=True)


# ---------- Export helpers ----------
def generate_export_data(
    spot_price, K1, K2, K3, K4,
    rate_pct, T_years, vol_pct, N_steps,
    quantity, multiplier,
    current_greeks_ui,
    greeks_curve_ui,
    spot_range
):
    return {
        "timestamp": datetime.now().isoformat(),
        "strategy": "SHORT_IRON_CONDOR",
        "config": {
            "spot_price": float(spot_price),
            "K1_long_put": float(K1),
            "K2_short_put": float(K2),
            "K3_short_call": float(K3),
            "K4_long_call": float(K4),
            "interest_rate_pct": float(rate_pct),
            "time_to_expiration_years": float(T_years),
            "volatility_pct": float(vol_pct),
            "binomial_steps": int(N_steps),
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
        },
    }


def export_to_json(export_data) -> str:
    return json.dumps(export_data, indent=2)


def export_to_csv(export_data) -> str:
    cfg = export_data["config"]
    g = export_data["current_greeks_ui"]

    buf = io.StringIO()
    buf.write("CONFIGURATION\n")
    for k, v in cfg.items():
        buf.write(f"{k},{v}\n")
    buf.write("\nGREEKS (UI)\n")
    for k, v in g.items():
        buf.write(f"{k},{v}\n")
    return buf.getvalue()


def export_to_pdf(export_data, capital: float) -> bytes:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1f77b4"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    heading_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#2ca02c"),
        spaceAfter=6,
        spaceBefore=8,
        fontName="Helvetica-Bold",
    )
    normal = styles["Normal"]

    elements = []
    elements.append(Paragraph("Short Iron Condor Report (Binomial CRR)", title_style))
    elements.append(Spacer(1, 0.12 * inch))

    cfg = export_data["config"]
    elements.append(Paragraph(f"<b>Date:</b> {export_data['timestamp']}", normal))
    elements.append(Paragraph(f"<b>Stratégie:</b> {export_data['strategy']}", normal))
    elements.append(Spacer(1, 0.12 * inch))

    elements.append(Paragraph("Configuration", heading_style))
    rows = [["Paramètre", "Valeur"]] + [[k, str(v)] for k, v in cfg.items()] + [["capital_eur", f"{capital:.2f}"]]
    t = Table(rows, colWidths=[2.7 * inch, 2.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)

    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph("Greeks (unités interface)", heading_style))

    g = export_data["current_greeks_ui"]
    tg = Table(
        [
            ["Delta", f"{g['delta']:.6f}", "variation du prix pour +1€ de spot"],
            ["Gamma", f"{g['gamma']:.6e}", "variation de delta"],
            ["Theta/day", f"{g['theta_per_day']:.6f}", "érosion temps par jour"],
            ["Vega(+1%)", f"{g['vega_per_1pct_vol']:.6f}", "variation pour +1% de vol"],
        ],
        colWidths=[1.2 * inch, 1.6 * inch, 2.7 * inch],
    )
    tg.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightblue),
    ]))
    elements.append(tg)

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# ---------- UI helpers ----------
def triangular_dict_to_df(level_dict: dict, N: int) -> pd.DataFrame:
    """
    Transforme un arbre {i:{j:val}} en tableau (DataFrame) lisible :
    - ligne = niveau i (temps)
    - colonne = nœud j
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
    df.insert(0, "niveau", [f"i={i}" for i in range(N + 1)])
    return df


# ---------- App ----------
def main():
    st.set_page_config(
        page_title="Short Iron Condor (Binomial CRR)",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Short Iron Condor - Pricer Binomial (CRR)")
    st.write("But : pricer la stratégie en binomial, afficher arbres binomiaux, et analyser les Greeks.")

    # Mode
    mode = st.radio(
        "Mode d’utilisation",
        ["Mode manuel", "Mode marché (Yahoo Finance)"],
        horizontal=True,
    )

    with st.sidebar:
        st.header("Paramètres")

        if mode == "Mode marché (Yahoo Finance)":
            st.subheader("Données de marché")
            selected_stock = st.selectbox(
                "Choisir une action",
                list(AVAILABLE_STOCKS.keys()),
                format_func=lambda x: f"{x} - {AVAILABLE_STOCKS[x]}",
            )

            with st.spinner("Récupération des données..."):
                md = MarketDataProvider(selected_stock, period="1y")
                if md.data is None or md.data.empty:
                    st.error("Impossible de récupérer les données marché.")
                    st.stop()
                summary = md.get_summary()

            spot_price = float(summary["price"])
            vol_pct = float(summary["volatility_pct"])
            vol_decimal = float(summary["volatility"])  # déjà en décimal

            st.write(f"Spot actuel : {spot_price:.2f} €")
            st.write(f"Volatilité réalisée : {vol_pct:.1f} %")

            rate_pct = st.slider("Taux sans risque (%)", 0.0, 10.0, 2.5, 0.5)
            r = rate_pct / 100.0

            T = st.slider("Maturité (années)", 0.01, 2.0, 0.25, 0.01)

            st.divider()
            st.subheader("Strikes (K1 < K2 < K3 < K4)")
            suggest = st.checkbox("Proposer des strikes (±5% / ±10%)", value=True)
            if suggest:
                K1 = st.number_input("K1 (long put)",  min_value=1.0, value=float(spot_price * 0.90), step=1.0)
                K2 = st.number_input("K2 (short put)", min_value=1.0, value=float(spot_price * 0.95), step=1.0)
                K3 = st.number_input("K3 (short call)", min_value=1.0, value=float(spot_price * 1.05), step=1.0)
                K4 = st.number_input("K4 (long call)",  min_value=1.0, value=float(spot_price * 1.10), step=1.0)
            else:
                K1 = st.number_input("K1 (long put)",  min_value=1.0, value=90.0, step=1.0)
                K2 = st.number_input("K2 (short put)", min_value=1.0, value=95.0, step=1.0)
                K3 = st.number_input("K3 (short call)", min_value=1.0, value=105.0, step=1.0)
                K4 = st.number_input("K4 (long call)",  min_value=1.0, value=110.0, step=1.0)

            st.divider()
            capital = st.number_input("Capital disponible (€)", min_value=1000, value=10000, step=500)
            N_steps = st.slider("Nombre de pas binomial N", 10, 300, 100, 10)

        else:
            st.subheader("Conditions de marché")
            spot_price = float(st.slider("Spot (€)", 50, 500, 100, 1))
            vol_pct = float(st.slider("Volatilité (%)", 5, 100, 30, 1))
            rate_pct = float(st.slider("Taux sans risque (%)", 0.0, 10.0, 2.5, 0.5))
            T = float(st.slider("Maturité (années)", 0.01, 2.0, 0.25, 0.01))

            vol_decimal = vol_pct / 100.0
            r = rate_pct / 100.0

            st.divider()
            st.subheader("Strikes (K1 < K2 < K3 < K4)")
            K1 = float(st.number_input("K1 (long put)",  min_value=1.0, value=90.0, step=1.0))
            K2 = float(st.number_input("K2 (short put)", min_value=1.0, value=95.0, step=1.0))
            K3 = float(st.number_input("K3 (short call)", min_value=1.0, value=105.0, step=1.0))
            K4 = float(st.number_input("K4 (long call)",  min_value=1.0, value=110.0, step=1.0))

            st.divider()
            capital = float(st.number_input("Capital disponible (€)", min_value=1000, value=10000, step=500))
            N_steps = int(st.slider("Nombre de pas binomial N", 10, 300, 100, 10))

        if not (K1 < K2 < K3 < K4):
            st.error("Ordre invalide : il faut K1 < K2 < K3 < K4.")
            st.stop()

    # --- Construire stratégie ---
    params = StrategyParams(
        S=float(spot_price),
        K1=float(K1), K2=float(K2), K3=float(K3), K4=float(K4),
        r=float(r), T=float(T), sigma=float(vol_decimal), N=int(N_steps),
        multiplier=100,
    )
    strat = ShortIronCondor(params)
    executor = StrategyExecutor(capital)

    details = strat.get_strategy_details()
    qty = executor.max_quantity(strat)
    exec_sum = executor.get_execution_summary(strat, qty)

    multiplier = params.multiplier

    # --- Résumé stratégie ---
    st.subheader("Résumé de la stratégie")
    st.write(
        "Short Iron Condor : on encaisse un crédit au départ. "
        "La stratégie est gagnante si le sous-jacent termine entre K2 et K3. "
        "En dehors, la perte est limitée par les ailes (K1 et K4)."
    )

    legs_df = pd.DataFrame(details["legs"])
    st_df(legs_df, hide_index=True)

    # --- Chiffres clés ---
    c1, c2, c3 = st.columns([1, 1, 1.2])

    with c1:
        st.subheader("Pricing (binomial)")
        cost_per_contract = details["net_cost_per_share"] * multiplier
        if cost_per_contract < 0:
            st.metric("Crédit net (€/contrat)", f"{abs(cost_per_contract):.2f}")
        else:
            st.metric("Débit net (€/contrat)", f"{cost_per_contract:.2f}")

        st.divider()
        st.subheader("Max profit / Max perte (échéance)")
        st.metric("Max profit (€/contrat)", f"{details['max_profit_per_share'] * multiplier:.2f}")
        st.metric("Max perte (€/contrat)", f"{abs(details['max_loss_per_share'] * multiplier):.2f}")

        st.divider()
        st.subheader("Breakevens")
        be = details["breakeven_points"]
        if len(be) >= 2:
            st.write(f"Breakeven bas : {be[0]:.2f} €")
            st.write(f"Breakeven haut : {be[-1]:.2f} €")
        else:
            st.write("Breakevens non détectés (paramètres atypiques).")

    with c2:
        st.subheader("Gestion du capital")
        st.metric("Contrats max", f"{qty}")
        st.metric("Perte max totale (€)", f"{exec_sum['total_max_loss']:.2f}")
        st.metric("Utilisation du capital (%)", f"{exec_sum['capital_utilization_pct']:.1f}")
        st.metric("Capital restant (€)", f"{exec_sum['capital_remaining']:.2f}")

        st.divider()
        st.subheader("Prix des jambes (binomial)")
        def price_leg(opt_type: str, K: float) -> float:
            m = BinomialModel(S=float(spot_price), K=float(K), r=float(r), T=float(T), sigma=float(vol_decimal), N=int(N_steps))
            return float(m.price_put()) if opt_type == "put" else float(m.price_call())

        legs_prices = [
            {"Leg": f"PUT  K1 {K1:.2f}", "Position": "LONG",  "Prix €/share": f"{price_leg('put', K1):.4f}",  "Prix €/contrat": f"{price_leg('put', K1)*multiplier:.2f}"},
            {"Leg": f"PUT  K2 {K2:.2f}", "Position": "SHORT", "Prix €/share": f"{price_leg('put', K2):.4f}",  "Prix €/contrat": f"{price_leg('put', K2)*multiplier:.2f}"},
            {"Leg": f"CALL K3 {K3:.2f}", "Position": "SHORT", "Prix €/share": f"{price_leg('call', K3):.4f}", "Prix €/contrat": f"{price_leg('call', K3)*multiplier:.2f}"},
            {"Leg": f"CALL K4 {K4:.2f}", "Position": "LONG",  "Prix €/share": f"{price_leg('call', K4):.4f}", "Prix €/contrat": f"{price_leg('call', K4)*multiplier:.2f}"},
        ]
        st_df(pd.DataFrame(legs_prices), hide_index=True)

    with c3:
        st.subheader("Comment l’expliquer à l’oral")
        st.write(
            "- On vend de la volatilité : on préfère un marché stable.\n"
            "- Gain si le prix reste entre K2 et K3.\n"
            "- Risque : gros mouvement (baisse ou hausse), mais perte plafonnée grâce aux ailes.\n"
            "- Greeks typiques : theta positif (le temps aide), vega négatif (hausse de vol pénalise)."
        )

    # --- Payoff interactif (vert / rouge) ---
    st.divider()
    st.subheader("Payoff à l’échéance")

    x = np.linspace(spot_price * 0.7, spot_price * 1.3, 350)
    y = strat.payoff_curve_per_share(x) * multiplier

    y_profit = np.where(y >= 0, y, np.nan)
    y_loss = np.where(y < 0, y, np.nan)

    fig_payoff = go.Figure()
    fig_payoff.add_trace(go.Scatter(x=x, y=y_profit, mode="lines", name="Zone de gain", line=dict(color="green", width=3)))
    fig_payoff.add_trace(go.Scatter(x=x, y=y_loss, mode="lines", name="Zone de perte", line=dict(color="red", width=3)))

    fig_payoff.add_hline(y=0, line_width=1, line_color="gray")
    for k, name in [(K1, "K1"), (K2, "K2"), (K3, "K3"), (K4, "K4")]:
        fig_payoff.add_vline(x=k, line_width=1, line_dash="dash", line_color="gray")
    fig_payoff.add_vline(x=spot_price, line_width=2, line_dash="dot", line_color="black")

    fig_payoff.update_layout(
        height=420,
        xaxis_title="Spot à l’échéance",
        yaxis_title="P&L (€/contrat)",
        legend=dict(orientation="h"),
        margin=dict(l=40, r=20, t=30, b=40),
    )
    st_plot(fig_payoff)

    # --- Arbres binomiaux ---
    st.divider()
    st.subheader("Arbres binomiaux (version réduite)")

    with st.expander("Afficher un arbre binomial (N <= 10)"):
        tree_N = st.slider("N pour affichage (petit arbre)", 1, 10, 5, 1)
        leg_choice = st.selectbox("Jambe à afficher", ["K1 (put)", "K2 (put)", "K3 (call)", "K4 (call)"], index=1)

        if "K1" in leg_choice:
            legK, legType = K1, "put"
        elif "K2" in leg_choice:
            legK, legType = K2, "put"
        elif "K3" in leg_choice:
            legK, legType = K3, "call"
        else:
            legK, legType = K4, "call"

        model_tree = BinomialModel(S=float(spot_price), K=float(legK), r=float(r), T=float(T), sigma=float(vol_decimal), N=int(tree_N))
        tree = model_tree.get_tree_data()

        if "error" in tree:
            st.error(tree["error"])
        else:
            st.caption(f"Arbre affiché : {legType.upper()} strike={legK:.2f} avec N={tree_N}")

            st.write("Arbre des prix du sous-jacent")
            st_df(triangular_dict_to_df(tree["stock_prices"], tree_N))

            opt_key = "put_prices" if legType == "put" else "call_prices"
            st.write("Arbre des prix de l’option")
            st_df(triangular_dict_to_df(tree[opt_key], tree_N))

    # --- Greeks (binomial, différences finies) ---
    st.divider()
    st.subheader("Greeks (binomial, différences finies)")

    spot_range_g = np.linspace(spot_price * 0.7, spot_price * 1.3, 60)

    legs_config = [
        {"K": K1, "type": "put",  "sign": +1},
        {"K": K2, "type": "put",  "sign": -1},
        {"K": K3, "type": "call", "sign": -1},
        {"K": K4, "type": "call", "sign": +1},
    ]

    greeks_calc = MultiLegGreeksCalculator(
        spot_range=spot_range_g,
        legs=legs_config,
        interest_rate=float(r),
        time_to_maturity=float(T),
        volatility=float(vol_decimal),
        n_steps=int(N_steps),
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
        f = go.Figure()
        f.add_trace(go.Scatter(x=spot_range_g, y=delta, mode="lines", name="Delta"))
        f.add_hline(y=0, line_dash="dash", opacity=0.3)
        f.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        f.update_layout(height=320, xaxis_title="Spot", yaxis_title="Delta", yaxis=dict(range=axis_range(delta)))
        st_plot(f)

    with colB:
        f = go.Figure()
        f.add_trace(go.Scatter(x=spot_range_g, y=gamma, mode="lines", name="Gamma"))
        f.add_hline(y=0, line_dash="dash", opacity=0.3)
        f.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        f.update_layout(height=320, xaxis_title="Spot", yaxis_title="Gamma", yaxis=dict(range=axis_range(gamma)))
        st_plot(f)

    colC, colD = st.columns(2)
    with colC:
        f = go.Figure()
        f.add_trace(go.Scatter(x=spot_range_g, y=theta_day, mode="lines", name="Theta/jour"))
        f.add_hline(y=0, line_dash="dash", opacity=0.3)
        f.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        f.update_layout(height=320, xaxis_title="Spot", yaxis_title="Theta/jour", yaxis=dict(range=axis_range(theta_day)))
        st_plot(f)

    with colD:
        f = go.Figure()
        f.add_trace(go.Scatter(x=spot_range_g, y=vega_1pct, mode="lines", name="Vega (+1%)"))
        f.add_hline(y=0, line_dash="dash", opacity=0.3)
        f.add_vline(x=spot_price, line_dash="dash", opacity=0.6)
        f.update_layout(height=320, xaxis_title="Spot", yaxis_title="Vega (+1%)", yaxis=dict(range=axis_range(vega_1pct)))
        st_plot(f)

    st.subheader("Greeks au spot actuel (unités interface)")
    g0 = greeks_calc.get_greeks_at_spot(float(spot_price))
    current_greeks_ui = {
        "delta": float(g0["delta"]),
        "gamma": float(g0["gamma"]),
        "theta_per_day": float(g0["theta"]) / 365.0,
        "vega_per_1pct_vol": float(g0["vega"]) / 100.0,
    }

    a, b, c, d = st.columns(4)
    a.metric("Delta", f"{current_greeks_ui['delta']:.6f}")
    b.metric("Gamma", f"{current_greeks_ui['gamma']:.6e}")
    c.metric("Theta/jour", f"{current_greeks_ui['theta_per_day']:.6f}")
    d.metric("Vega (+1%)", f"{current_greeks_ui['vega_per_1pct_vol']:.6f}")

    # --- Export ---
    st.divider()
    st.subheader("Export")

    greeks_curve_ui = {
        "delta": delta,
        "gamma": gamma,
        "theta_per_day": theta_day,
        "vega_per_1pct_vol": vega_1pct,
    }

    export_data = generate_export_data(
        spot_price=spot_price, K1=K1, K2=K2, K3=K3, K4=K4,
        rate_pct=rate_pct, T_years=T, vol_pct=vol_pct, N_steps=N_steps,
        quantity=qty, multiplier=multiplier,
        current_greeks_ui=current_greeks_ui,
        greeks_curve_ui=greeks_curve_ui,
        spot_range=spot_range_g,
    )

    cX, cY, cZ = st.columns(3)
    with cX:
        st_download(
            label="Télécharger JSON",
            data=export_to_json(export_data),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
    with cY:
        st_download(
            label="Télécharger CSV",
            data=export_to_csv(export_data),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    with cZ:
        st_download(
            label="Télécharger PDF",
            data=export_to_pdf(export_data, capital=capital),
            file_name=f"iron_condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()
