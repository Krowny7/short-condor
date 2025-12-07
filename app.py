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
import json
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from binomial_engine import BinomialModel, MultiLegGreeksCalculator
from strategy_manager import ShortCondor, StrategyParams, StrategyExecutor
from market_data import MarketDataProvider, AVAILABLE_STOCKS


# Configuration de la page
st.set_page_config(
    page_title="Short Condor Strategy Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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


# ======================== EXPORT FUNCTIONS ========================
def generate_export_data(spot_price, K1, K2, K3, K4, rate, expiration_years, 
                         volatility, num_steps, quantity, strategy, current_greeks, 
                         greeks_range, spot_range):
    """
    Generate comprehensive export data from current analysis
    """
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "strategy_config": {
            "spot_price": float(spot_price),
            "strike_1_short_call": float(K1),
            "strike_2_long_call": float(K2),
            "strike_3_long_put": float(K3),
            "strike_4_short_put": float(K4),
            "interest_rate_pct": float(rate),
            "time_to_expiration_years": float(expiration_years),
            "volatility_pct": float(volatility),
            "binomial_steps": int(num_steps),
            "quantity_contracts": int(quantity),
        },
        "current_greeks": {
            "delta": float(current_greeks['delta']),
            "gamma": float(current_greeks['gamma']),
            "theta": float(current_greeks['theta']),
            "vega": float(current_greeks['vega']),
        },
        "greeks_evolution": {
            "spot_prices": [float(x) for x in spot_range.tolist()],
            "delta_values": [float(x) for x in greeks_range['delta'].tolist()],
            "gamma_values": [float(x) for x in greeks_range['gamma'].tolist()],
            "theta_values": [float(x) for x in greeks_range['theta'].tolist()],
            "vega_values": [float(x) for x in greeks_range['vega'].tolist()],
            "payoff_values": [float(strategy.payoff_at_maturity(s)) for s in spot_range],
        },
        "scenarios": {
            "crash_20": float(strategy.payoff_at_maturity(spot_price * 0.8) * quantity * 100),
            "down_10": float(strategy.payoff_at_maturity(spot_price * 0.9) * quantity * 100),
            "current": float(strategy.payoff_at_maturity(spot_price) * quantity * 100),
            "up_10": float(strategy.payoff_at_maturity(spot_price * 1.1) * quantity * 100),
            "peak_20": float(strategy.payoff_at_maturity(spot_price * 1.2) * quantity * 100),
            "at_k1": float(strategy.payoff_at_maturity(K1) * quantity * 100),
            "at_k2": float(strategy.payoff_at_maturity(K2) * quantity * 100),
            "at_k3": float(strategy.payoff_at_maturity(K3) * quantity * 100),
            "at_k4": float(strategy.payoff_at_maturity(K4) * quantity * 100),
        }
    }
    return export_data


def export_to_json(export_data):
    """Export data to JSON format"""
    return json.dumps(export_data, indent=2)


def export_to_csv(export_data, strategy, spot_price, K1, K2, K3, K4, quantity):
    """Export data to CSV format"""
    csv_buffer = io.StringIO()
    
    # Strategy Configuration
    csv_buffer.write("STRATEGY CONFIGURATION\n")
    csv_buffer.write("Timestamp," + export_data["timestamp"] + "\n")
    csv_buffer.write("Spot Price,€" + str(export_data["strategy_config"]["spot_price"]) + "\n")
    csv_buffer.write("Strike 1 (Short Call),€" + str(export_data["strategy_config"]["strike_1_short_call"]) + "\n")
    csv_buffer.write("Strike 2 (Long Call),€" + str(export_data["strategy_config"]["strike_2_long_call"]) + "\n")
    csv_buffer.write("Strike 3 (Long Put),€" + str(export_data["strategy_config"]["strike_3_long_put"]) + "\n")
    csv_buffer.write("Strike 4 (Short Put),€" + str(export_data["strategy_config"]["strike_4_short_put"]) + "\n")
    csv_buffer.write("Interest Rate,%," + str(export_data["strategy_config"]["interest_rate_pct"]) + "\n")
    csv_buffer.write("Time to Expiration,years," + str(export_data["strategy_config"]["time_to_expiration_years"]) + "\n")
    csv_buffer.write("Volatility,%," + str(export_data["strategy_config"]["volatility_pct"]) + "\n")
    csv_buffer.write("Quantity,contracts," + str(export_data["strategy_config"]["quantity_contracts"]) + "\n")
    csv_buffer.write("\n")
    
    # Current Greeks
    csv_buffer.write("CURRENT GREEKS\n")
    csv_buffer.write("Delta," + str(export_data["current_greeks"]["delta"]) + "\n")
    csv_buffer.write("Gamma," + str(export_data["current_greeks"]["gamma"]) + "\n")
    csv_buffer.write("Theta," + str(export_data["current_greeks"]["theta"]) + "\n")
    csv_buffer.write("Vega," + str(export_data["current_greeks"]["vega"]) + "\n")
    csv_buffer.write("\n")
    
    # Scenarios
    csv_buffer.write("SCENARIO ANALYSIS\n")
    csv_buffer.write("Scenario,P&L (€)\n")
    csv_buffer.write("Crash (S -20%)," + str(export_data["scenarios"]["crash_20"]) + "\n")
    csv_buffer.write("Down (S -10%)," + str(export_data["scenarios"]["down_10"]) + "\n")
    csv_buffer.write("Current Price," + str(export_data["scenarios"]["current"]) + "\n")
    csv_buffer.write("Up (S +10%)," + str(export_data["scenarios"]["up_10"]) + "\n")
    csv_buffer.write("Peak (S +20%)," + str(export_data["scenarios"]["peak_20"]) + "\n")
    csv_buffer.write("\n")
    
    # Key Levels
    csv_buffer.write("KEY LEVELS\n")
    csv_buffer.write("Level,Price (€),P&L (€)\n")
    csv_buffer.write("K1 (Short Call)," + str(K1) + "," + str(export_data["scenarios"]["at_k1"]) + "\n")
    csv_buffer.write("K2 (Long Call)," + str(K2) + "," + str(export_data["scenarios"]["at_k2"]) + "\n")
    csv_buffer.write("K3 (Long Put)," + str(K3) + "," + str(export_data["scenarios"]["at_k3"]) + "\n")
    csv_buffer.write("K4 (Short Put)," + str(K4) + "," + str(export_data["scenarios"]["at_k4"]) + "\n")
    
    return csv_buffer.getvalue()


def export_to_pdf(export_data, strategy, spot_price, K1, K2, K3, K4, quantity, capital, maturity):
    """Export data to PDF format with professional formatting"""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2ca02c'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    normal_style = styles['Normal']
    
    # Build PDF content
    elements = []
    
    # Title
    elements.append(Paragraph("Short Condor Strategy Analysis Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Report Info
    report_date = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    elements.append(Paragraph(f"<b>Generated:</b> {report_date}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Strategy Configuration Section
    elements.append(Paragraph("Strategy Configuration", heading_style))
    
    config_data = [
        ["Parameter", "Value"],
        ["Spot Price", f"€{spot_price:.2f}"],
        ["Strike 1 (Short Call)", f"€{K1:.2f}"],
        ["Strike 2 (Long Call)", f"€{K2:.2f}"],
        ["Strike 3 (Long Put)", f"€{K3:.2f}"],
        ["Strike 4 (Short Put)", f"€{K4:.2f}"],
        ["Interest Rate", f"{export_data['strategy_config']['interest_rate_pct']:.2f}%"],
        ["Time to Expiration", f"{export_data['strategy_config']['time_to_expiration_years']:.4f} years"],
        ["Volatility", f"{export_data['strategy_config']['volatility_pct']:.2f}%"],
        ["Binomial Steps", f"{export_data['strategy_config']['binomial_steps']}"],
        ["Quantity (Contracts)", f"{export_data['strategy_config']['quantity_contracts']}"],
        ["Capital Available", f"€{capital:.2f}"],
    ]
    
    config_table = Table(config_data, colWidths=[3*inch, 2*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(config_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Greeks Section
    elements.append(Paragraph("Greeks at Current Price", heading_style))
    
    greeks_data = [
        ["Greek", "Value", "Interpretation"],
        ["Delta", f"{export_data['current_greeks']['delta']:.6f}", "Spot sensitivity"],
        ["Gamma", f"{export_data['current_greeks']['gamma']:.6f}", "Delta change rate"],
        ["Theta", f"{export_data['current_greeks']['theta']:.6f}", "Time decay per day"],
        ["Vega", f"{export_data['current_greeks']['vega']:.6f}", "Volatility sensitivity"],
    ]
    
    greeks_table = Table(greeks_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    greeks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(greeks_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Scenario Analysis
    elements.append(Paragraph("Scenario Analysis", heading_style))
    
    scenarios_data = [
        ["Scenario", "Stock Price", "P&L (€)"],
        ["Crash (S -20%)", f"€{spot_price * 0.8:.2f}", f"{export_data['scenarios']['crash_20']:.2f}"],
        ["Down (S -10%)", f"€{spot_price * 0.9:.2f}", f"{export_data['scenarios']['down_10']:.2f}"],
        ["Current Price", f"€{spot_price:.2f}", f"{export_data['scenarios']['current']:.2f}"],
        ["Up (S +10%)", f"€{spot_price * 1.1:.2f}", f"{export_data['scenarios']['up_10']:.2f}"],
        ["Peak (S +20%)", f"€{spot_price * 1.2:.2f}", f"{export_data['scenarios']['peak_20']:.2f}"],
    ]
    
    scenarios_table = Table(scenarios_data, colWidths=[2*inch, 2*inch, 2*inch])
    scenarios_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(scenarios_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Levels
    elements.append(Paragraph("Key Levels Analysis", heading_style))
    
    levels_data = [
        ["Level", "Strike Price", "P&L (€)"],
        ["K1 (Short Call)", f"€{K1:.2f}", f"{export_data['scenarios']['at_k1']:.2f}"],
        ["K2 (Long Call)", f"€{K2:.2f}", f"{export_data['scenarios']['at_k2']:.2f}"],
        ["K3 (Long Put)", f"€{K3:.2f}", f"{export_data['scenarios']['at_k3']:.2f}"],
        ["K4 (Short Put)", f"€{K4:.2f}", f"{export_data['scenarios']['at_k4']:.2f}"],
    ]
    
    levels_table = Table(levels_data, colWidths=[2*inch, 2*inch, 2*inch])
    levels_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(levels_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(PageBreak())
    footer_text = """
    <b>Disclaimer:</b> This report is provided for educational and demonstration purposes only. 
    This is not financial advice. The Short Condor Strategy Analyzer is a tool for learning and 
    analysis. Always consult a qualified financial advisor before trading. Past performance does 
    not guarantee future results. Options trading involves substantial risk and is not suitable for all investors.
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def main():
    st.title("📈 Short Condor Strategy Analyzer")
    st.markdown("**Valuation Tool for Volatility-Based Options Strategies**")
    st.markdown("Binomial Model (Cox-Ross-Rubinstein) for European Options")
    
    # ======================== CHOIX DU MODE ========================
    mode = st.radio(
        "🎯 Usage Mode",
        ["Manual Mode", "Real Mode (Market Data)"],
        horizontal=True,
        help="Manual: Enter your own values | Real: Live data from Yahoo Finance"
    )
    
    # ======================== SIDEBAR: PARAMETERS ========================
    with st.sidebar:
        st.header("⚙️ Strategy Parameters")
        
        # ==================== REAL MODE ====================
        if mode == "Real Mode (Market Data)":
            st.subheader("📊 Real Market Data")
            
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
                st.metric("Realized Volatility", f"{summary['volatility_pct']:.1f}%")
            
            # Récupérer les valeurs de marché
            spot_price = summary['price']
            volatility = summary['volatility_pct']
            vol_decimal = summary['volatility'] / 100
            
            st.divider()
            st.subheader("🎛️ Adjustable Parameters")
            
            # Taux d'intérêt
            interest_rate = st.slider("Taux d'Intérêt (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5)
            rate_decimal = interest_rate / 100
            
            # Délai d'expiration
            maturity = st.slider("Délai d'Expiration (années)", min_value=0.01, max_value=2.0, value=0.25, step=0.01)
            
            st.divider()
            st.subheader("⚡ Short Condor Strikes (€)")
            st.info(
                f"📍 Current Price: €{spot_price:.2f}\n\n"
                f"**Structure:** K1 (Sell Call) < K2 (Buy Call) < K3 (Buy Call) < K4 (Sell Call)"
            )
            
            # Propose suggested strikes
            suggest_strikes = st.checkbox("💡 Get Suggested Strikes (±5% and ±10%)", value=True)
            
            if suggest_strikes:
                # Calculate suggested strikes for short condor (4 calls)
                suggested_k1 = spot_price * 0.90  # Sell call (10% OTM)
                suggested_k2 = spot_price * 0.95  # Buy call (5% OTM)
                suggested_k3 = spot_price * 1.05  # Buy call (5% OTM)
                suggested_k4 = spot_price * 1.10  # Sell call (10% OTM)
                
                col1, col2 = st.columns(2)
                with col1:
                    K1 = st.number_input(
                        "K1 - Sell Call (Lowest Strike)",
                        min_value=10.0,
                        value=suggested_k1,
                        step=1.0,
                        help=f"Income | Suggested: €{suggested_k1:.2f}"
                    )
                    K3 = st.number_input(
                        "K3 - Buy Call (High Strike)",
                        min_value=10.0,
                        value=suggested_k3,
                        step=1.0,
                        help=f"Protection | Suggested: €{suggested_k3:.2f}"
                    )
                with col2:
                    K2 = st.number_input(
                        "K2 - Buy Call (Low-Mid Strike)",
                        min_value=10.0,
                        value=suggested_k2,
                        step=1.0,
                        help=f"Protection | Suggested: €{suggested_k2:.2f}"
                    )
                    K4 = st.number_input(
                        "K4 - Sell Call (Highest Strike)",
                        min_value=10.0,
                        value=suggested_k4,
                        step=1.0,
                        help=f"Income | Suggested: €{suggested_k4:.2f}"
                    )
            else:
                col1, col2 = st.columns(2)
                with col1:
                    K1 = st.number_input("K1 - Sell Call (Lowest)", min_value=10.0, value=90.0, step=1.0)
                    K3 = st.number_input("K3 - Buy Call (High)", min_value=10.0, value=105.0, step=1.0)
                with col2:
                    K2 = st.number_input("K2 - Buy Call (Low-Mid)", min_value=10.0, value=95.0, step=1.0)
                    K4 = st.number_input("K4 - Sell Call (Highest)", min_value=10.0, value=110.0, step=1.0)
            
            st.divider()
            st.subheader("💰 Capital Management")
            capital = st.number_input("Available Capital (€)", min_value=1000, value=10000, step=500)
            
            st.divider()
            st.subheader("🎯 Model Precision")
            N_steps = st.slider("Binomial Steps (N)", min_value=10, max_value=200, value=50, step=10)
        
        # ==================== MANUAL MODE ====================
        else:
            st.subheader("Market Conditions")
            spot_price = st.slider("Spot Price (€)", min_value=50, max_value=500, value=100, step=1)
            volatility = st.slider("Volatility (%)", min_value=5, max_value=100, value=30, step=1)
            interest_rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.5)
            maturity = st.slider("Time to Expiration (years)", min_value=0.01, max_value=2.0, value=0.25, step=0.01)
            
            # Convert percentages to decimals
            vol_decimal = volatility / 100
            rate_decimal = interest_rate / 100
            
            # Strike Selection
            st.subheader("Strike Selection")
            st.info("K1 < K2 < K3 < K4 (Validation applied)")
            
            col1, col2 = st.columns(2)
            with col1:
                K1 = st.number_input("K1 - Short Call (Lowest)", min_value=10.0, value=90.0, step=1.0)
                K3 = st.number_input("K3 - Long Call", min_value=10.0, value=110.0, step=1.0)
            with col2:
                K2 = st.number_input("K2 - Long Call", min_value=10.0, value=95.0, step=1.0)
                K4 = st.number_input("K4 - Short Call (Highest)", min_value=10.0, value=115.0, step=1.0)
            
            # Capital Management
            st.subheader("Capital Management")
            capital = st.number_input("Available Capital (€)", min_value=1000, value=10000, step=500)
            
            # Binomial Precision
            st.subheader("Model Precision")
            N_steps = st.slider("Binomial Steps (N)", min_value=10, max_value=200, value=50, step=10)
        
        st.divider()
        
        # Validate strikes
        try:
            if not (K1 < K2 < K3 < K4):
                st.error("❌ Invalid strike order: K1 < K2 < K3 < K4")
                st.stop()
        except:
            st.error("Invalid strike prices")
            st.stop()
    
    # ======================== CREATE STRATEGY ========================
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
        
        # Validate Greeks numerically
        greeks_validation = strategy.validate_greeks_numerically(spot_price)
        
    except ValueError as e:
        st.error(f"❌ Strategy Configuration Error:\n{str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        st.write(traceback.format_exc())
        st.stop()
    
    # Display validation warning if needed
    if not greeks_validation['validation_passed']:
        st.warning(
            f"⚠️ Greeks Validation Warning:\n"
            f"Max numerical error: {greeks_validation['max_error']:.6f}\n"
            f"This may indicate numerical precision issues. Use higher N_steps for better accuracy."
        )
    
    # Display strategy legs clearly
    st.info("📊 **Short Condor Structure (4 Calls)**")
    legs_data = []
    for leg in details['legs']:
        legs_data.append({
            'Option': f"{leg['type'].upper()} {leg['strike']:.2f}",
            'Position': leg['position'],
            'Role': 'Protection' if (leg['type'] == 'put' and leg['position'] == 'LONG') or (leg['type'] == 'call' and leg['position'] == 'LONG') else 'Income'
        })
    legs_df = pd.DataFrame(legs_data)
    st.dataframe(legs_df, use_container_width=True, hide_index=True)
    
    # ======================== MAIN CONTENT: 3-COLUMN LAYOUT ========================
    
    # Column 1: Financial Results
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    with col1:
        st.subheader("💰 Strategy Valuation")
        
        net_cost = details["net_cost"]
        
        if net_cost < 0:  # Credit strategy
            st.metric(
                "Net Credit Received",
                f"€{-net_cost:.2f}",
                delta=f"Per 100 shares",
                delta_color="normal"
            )
            st.success(f"✓ Credit Strategy (Premium Received)")
        else:
            st.metric(
                "Net Debit Paid",
                f"€{net_cost:.2f}",
                delta=f"Per 100 shares",
                delta_color="off"
            )
            st.info(f"Debit Strategy (Premium Paid)")
        
        st.divider()
        st.subheader("📊 Extreme Scenarios")
        
        max_profit = details["max_profit"]
        max_loss = details["max_loss"]
        
        col_profit, col_loss = st.columns(2)
        with col_profit:
            st.metric(
                "Maximum Profit",
                f"€{max_profit:.2f}",
                delta="Per contract",
                delta_color="normal"
            )
        with col_loss:
            st.metric(
                "Maximum Loss",
                f"€{abs(max_loss):.2f}",
                delta="Per contract",
                delta_color="off"
            )
        
        st.divider()
        st.subheader("🎯 Breakeven Points")
        
        if len(details["breakeven_points"]) >= 2:
            lower_be = details["breakeven_points"][0]
            upper_be = details["breakeven_points"][-1]
            st.write(f"**Lower Breakeven:** €{lower_be:.2f}")
            st.write(f"**Upper Breakeven:** €{upper_be:.2f}")
            st.write(f"**Profit Zone:** €{K2:.2f} - €{K3:.2f}")
        else:
            st.write("Breakeven points cannot be calculated (check parameters)")
    
    with col2:
        st.subheader("📈 Capital Management")
        
        quantity = executor.max_quantity(strategy)
        execution = executor.get_execution_summary(strategy, quantity)
        
        st.metric(
            "Max Strategies",
            f"{quantity}x",
            delta=f"With €{capital:.0f} capital",
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
        st.subheader("🔧 Individual Option Prices")
        
        # Calculate individual option prices
        from strategy_manager import BlackScholesGreeks
        
        call_K1 = BlackScholesGreeks.call_price(spot_price, K1, rate_decimal, maturity, vol_decimal)
        call_K2 = BlackScholesGreeks.call_price(spot_price, K2, rate_decimal, maturity, vol_decimal)
        call_K3 = BlackScholesGreeks.call_price(spot_price, K3, rate_decimal, maturity, vol_decimal)
        call_K4 = BlackScholesGreeks.call_price(spot_price, K4, rate_decimal, maturity, vol_decimal)
        
        options_df = pd.DataFrame({
            "Leg": ["K1 (€" + f"{K1:.2f}" + ")", "K2 (€" + f"{K2:.2f}" + ")", 
                    "K3 (€" + f"{K3:.2f}" + ")", "K4 (€" + f"{K4:.2f}" + ")"],
            "Type": ["Call", "Call", "Call", "Call"],
            "Position": ["SHORT", "LONG", "LONG", "SHORT"],
            "Price (€)": [f"{call_K1:.2f}", f"{call_K2:.2f}", f"{call_K3:.2f}", f"{call_K4:.2f}"]
        })
        
        st.dataframe(options_df, use_container_width=True, hide_index=True)
    
    with col3:
        st.subheader("📋 Strategy Summary")
        
        summary_data = {
            "Parameter": [
                "Spot Price",
                "Volatility",
                "Interest Rate",
                "Time to Expiration",
                "Binomial Steps",
                "Capital",
                "Max Contracts"
            ],
            "Value": [
                f"€{spot_price:.2f}",
                f"{volatility}%",
                f"{interest_rate}%",
                f"{maturity:.4f} years",
                f"{N_steps}",
                f"€{capital:.2f}",
                f"{quantity}x"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.subheader("📌 Short Condor Logic (4 Calls)")
        
        st.markdown("""
        **Short Condor - Volatility Seller:**
        
        **Income Positions (Short Calls):**
        - **Sell Call @ K1** - Collect premium (lowest strike)
        - **Sell Call @ K4** - Collect premium (highest strike)
        
        **Protection Positions (Long Calls):**
        - **Buy Call @ K2** - Cap loss on lower side
        - **Buy Call @ K3** - Cap loss on upper side
        
        **Profit Zone:** When stock stays between K2 and K3 at expiration
        
        **Max Profit:** Net credit received (all options expire worthless between K2-K3)
        
        **Max Loss:** Limited on both sides by the long calls
        - Lower wing: max loss = (K2-K1)
        - Upper wing: max loss = (K4-K3)
        
        **Best For:** Low volatility markets, expects sideways movement
        
        **Greeks:** Short gamma (loses on big moves), short vega (loses if IV rises), positive theta (gains with time decay)
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
        
        # Plot payoff curve
        ax.plot(spot_range, payoff, linewidth=2.5, color="#3498db", label="Strategy P&L", zorder=3)
        
        # Fill profit and loss zones
        ax.fill_between(spot_range, 0, payoff, where=(payoff >= 0), alpha=0.3, color="#2ecc71", label="Profit Zone", zorder=1)
        ax.fill_between(spot_range, 0, payoff, where=(payoff < 0), alpha=0.3, color="#e74c3c", label="Loss Zone", zorder=1)
        
        # Add strike lines
        ax.axvline(K1, color="red", linestyle="--", linewidth=1, alpha=0.7, label=f"K1=€{K1:.2f} (Short)")
        ax.axvline(K2, color="orange", linestyle="--", linewidth=1, alpha=0.7, label=f"K2=€{K2:.2f} (Long)")
        ax.axvline(K3, color="orange", linestyle="--", linewidth=1, alpha=0.7, label=f"K3=€{K3:.2f} (Long)")
        ax.axvline(K4, color="red", linestyle="--", linewidth=1, alpha=0.7, label=f"K4=€{K4:.2f} (Short)")
        
        # Current spot price
        ax.axvline(spot_price, color="green", linestyle="-", linewidth=2, alpha=0.8, label=f"Current Price=€{spot_price:.2f}")
        
        ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("Stock Price at Expiration (€)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Profit/Loss (€)", fontsize=11, fontweight="bold")
        ax.set_title(f"Short Condor Payoff at Expiration (T={maturity} years)", fontsize=12, fontweight="bold")
        ax.legend(loc="upper left", fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # Chart 2: Volatility Sensitivity
    with viz_col2:
        st.subheader("Volatility Sensitivity")
        
        # Test volatility range
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
    st.header("📈 Greeks Evolution")
    st.markdown("*Understand how risks change with the stock price*")
    st.info("💡 **Professional Vectorized Calculation** - Like hedge fund pricers")
    
    try:
        # Create price range for Greeks
        spot_range_greeks = np.linspace(spot_price * 0.7, spot_price * 1.3, 50)
        
        # Define Short Condor legs: -K1 +K2 +K3 -K4
        legs_config = [
            {'K': K1, 'type': 'call', 'sign': -1},   # Short K1 Call
            {'K': K2, 'type': 'call', 'sign': +1},   # Long K2 Call
            {'K': K3, 'type': 'put', 'sign': +1},    # Long K3 Put
            {'K': K4, 'type': 'put', 'sign': -1}     # Short K4 Put
        ]
        
        # Create professional calculator
        greeks_calc = MultiLegGreeksCalculator(
            spot_range=spot_range_greeks,
            legs=legs_config,
            interest_rate=interest_rate,
            time_to_maturity=maturity,
            volatility=volatility,
            n_steps=N_steps
        )
        
        # Calculate strategy Greeks (vectorized)
        strategy_greeks = greeks_calc.calculate_strategy_greeks()
        delta_arr = strategy_greeks['delta']
        gamma_arr = strategy_greeks['gamma']
        theta_arr = strategy_greeks['theta']
        vega_arr = strategy_greeks['vega']
        
        # Helper function for smart axis scaling
        def get_axis_range(data):
            """
            Compute smart axis range for Greeks.
            Handles both tiny values (1e-5) and large values with proper scaling.
            """
            abs_max = np.max(np.abs(data))
            if abs_max == 0:
                return [-0.01, 0.01]
            
            # Add 20% margin
            margin = abs_max * 0.2
            return [np.min(data) - margin, np.max(data) + margin]
        
        # 4 separate charts - one for each Greek
        col1, col2 = st.columns(2)
        
        # DELTA
        with col1:
            st.subheader("Delta (Δ) - Spot Sensitivity")
            st.caption("Price change for €1 increase in spot | Short Condor: near 0 = delta-neutral ✓")
            fig_delta = go.Figure()
            fig_delta.add_trace(go.Scatter(
                x=spot_range_greeks, y=delta_arr,
                mode='lines', fill='tozeroy',
                name='Delta',
                line=dict(color='#007AFF', width=2),
                fillcolor='rgba(0, 122, 255, 0.2)',
                hovertemplate='<b>Price: €%{x:.1f}</b><br>Delta: %{y:.4e}<extra></extra>'
            ))
            fig_delta.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
            fig_delta.add_vline(x=spot_price, line_dash="dash", line_color="gray", opacity=0.7)
            fig_delta.update_layout(
                height=300, hovermode='x unified', margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Spot Price (€)", yaxis_title="Delta ([-1, +1])",
                template='plotly_dark',
                yaxis=dict(range=get_axis_range(delta_arr))
            )
            st.plotly_chart(fig_delta, use_container_width=True)
        
        # GAMMA
        with col2:
            st.subheader("Gamma (Γ) - Acceleration")
            st.caption("Delta change rate | Negative = loss if price moves")
            fig_gamma = go.Figure()
            fig_gamma.add_trace(go.Scatter(
                x=spot_range_greeks, y=gamma_arr,
                mode='lines', fill='tozeroy',
                name='Gamma',
                line=dict(color='#34C759', width=2),
                fillcolor='rgba(52, 199, 89, 0.2)',
                hovertemplate='<b>Price: €%{x:.1f}</b><br>Gamma: %{y:.4e}<extra></extra>'
            ))
            fig_gamma.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
            fig_gamma.add_vline(x=spot_price, line_dash="dash", line_color="gray", opacity=0.7)
            fig_gamma.update_layout(
                height=300, hovermode='x unified', margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Spot Price (€)", yaxis_title="Gamma",
                template='plotly_dark',
                yaxis=dict(range=get_axis_range(gamma_arr))
            )
            st.plotly_chart(fig_gamma, use_container_width=True)
        
        # THETA
        with col1:
            st.subheader("Theta (Θ) - Time Decay")
            st.caption("Daily gain/loss from time passage | Positive = profit each day")
            fig_theta = go.Figure()
            fig_theta.add_trace(go.Scatter(
                x=spot_range_greeks, y=theta_arr,
                mode='lines', fill='tozeroy',
                name='Theta',
                line=dict(color='#FF9500', width=2),
                fillcolor='rgba(255, 149, 0, 0.2)',
                hovertemplate='<b>Price: €%{x:.1f}</b><br>Theta: €%{y:.4e}/day<extra></extra>'
            ))
            fig_theta.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
            fig_theta.add_vline(x=spot_price, line_dash="dash", line_color="gray", opacity=0.7)
            fig_theta.update_layout(
                height=300, hovermode='x unified', margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Spot Price (€)", yaxis_title="Theta (€/day)",
                template='plotly_dark',
                yaxis=dict(range=get_axis_range(theta_arr))
            )
            st.plotly_chart(fig_theta, use_container_width=True)
        
        # VEGA
        with col2:
            st.subheader("Vega (ν) - Volatility Sensitivity")
            st.caption("Change for +1% volatility | Short Condor = short gamma = short vega")
            fig_vega = go.Figure()
            fig_vega.add_trace(go.Scatter(
                x=spot_range_greeks, y=vega_arr,
                mode='lines', fill='tozeroy',
                name='Vega',
                line=dict(color='#AF52DE', width=2),
                fillcolor='rgba(175, 82, 222, 0.2)',
                hovertemplate='<b>Price: €%{x:.1f}</b><br>Vega: %{y:.4e}<extra></extra>'
            ))
            fig_vega.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
            fig_vega.add_vline(x=spot_price, line_dash="dash", line_color="gray", opacity=0.7)
            fig_vega.update_layout(
                height=300, hovermode='x unified', margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Spot Price (€)", yaxis_title="Vega",
                template='plotly_dark',
                yaxis=dict(range=get_axis_range(vega_arr))
            )
            st.plotly_chart(fig_vega, use_container_width=True)
        
        # Display current Greeks at current spot price
        st.divider()
        st.subheader("📌 Greeks at Current Price")
        current_greeks = greeks_calc.get_greeks_at_spot(spot_price)
        
        col_vals1, col_vals2, col_vals3, col_vals4 = st.columns(4)
        with col_vals1:
            st.metric(
                "Delta", 
                f"{current_greeks['delta']:.6f}",
                help="Spot price sensitivity"
            )
        with col_vals2:
            st.metric(
                "Gamma", 
                f"{current_greeks['gamma']:.6f}",
                help="Convexity (movement risk)"
            )
        with col_vals3:
            st.metric(
                "Theta", 
                f"{current_greeks['theta']:.6f}",
                help="Daily profit if spot stable"
            )
        with col_vals4:
            st.metric(
                "Vega", 
                f"{current_greeks['vega']:.6f}",
                help="Implied volatility sensitivity"
            )
    
    except Exception as e:
        st.error(f"❌ Error in Greeks calculation: {str(e)}")
        import traceback
        st.write(traceback.format_exc())
    
    # ======================== P&L ANALYSIS TABLE ========================
    st.divider()
    st.header("📊 P&L Analysis")
    
    col_pnl1, col_pnl2 = st.columns([1, 1])
    
    with col_pnl1:
        st.subheader("Scenario Analysis")
        
        # Create scenarios
        scenarios = [
            ("Crash (S -20%)", spot_price * 0.8),
            ("Down (S -10%)", spot_price * 0.9),
            ("Current Price", spot_price),
            ("Up (S +10%)", spot_price * 1.1),
            ("Peak (S +20%)", spot_price * 1.2),
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
            "S = K3 (Profit End)": K3,
            "S = K4 (Breakeven High)": K4,
        }
        
        levels_data = []
        for level_name, level_price in key_levels.items():
            pnl = strategy.payoff_at_maturity(level_price) * quantity * 100
            status = "✓ PROFIT" if pnl > 0 else ("✗ LOSS" if pnl < 0 else "- NEUTRAL")
            levels_data.append({
                "Price Level": level_name,
                "Stock Price": f"€{level_price:.2f}",
                "P&L (€)": f"{pnl:,.2f}",
                "Status": status
            })
        
        levels_df = pd.DataFrame(levels_data)
        st.dataframe(levels_df, use_container_width=True, hide_index=True)
    
    # ======================== EXPORT & REPORTS ========================
    st.divider()
    st.header("📥 Export & Reports")
    
    col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
    
    # Generate export data
    try:
        # Prepare Greeks data for export
        greeks_range = {
            'delta': delta_arr,
            'gamma': gamma_arr,
            'theta': theta_arr,
            'vega': vega_arr
        }
        
        export_data = generate_export_data(
            spot_price, K1, K2, K3, K4, interest_rate, maturity, 
            volatility, N_steps, quantity, strategy, current_greeks, 
            greeks_range, spot_range_greeks
        )
        
        with col_export1:
            st.subheader("📄 Download JSON Report")
            json_data = export_to_json(export_data)
            filename_json = f"Short_Condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=filename_json,
                mime="application/json",
                use_container_width=True
            )
        
        with col_export2:
            st.subheader("📊 Download CSV Report")
            csv_data = export_to_csv(export_data, strategy, spot_price, K1, K2, K3, K4, quantity)
            filename_csv = f"Short_Condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=filename_csv,
                mime="text/csv",
                use_container_width=True
            )
        
        with col_export3:
            st.subheader("📋 Download PDF Report")
            pdf_data = export_to_pdf(export_data, strategy, spot_price, K1, K2, K3, K4, quantity, capital, maturity)
            filename_pdf = f"Short_Condor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_data,
                file_name=filename_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        
        st.info(
            "💡 **Export Information:**\n\n"
            "- **JSON**: Complete strategy data in machine-readable format (configuration, Greeks, scenarios)\n"
            "- **CSV**: Formatted tables for spreadsheet applications (Excel, Sheets, etc.)\n"
            "- **PDF**: Professional formatted report with all analysis data and tables\n\n"
            "All exports include: Strategy parameters, Current Greeks, Scenario analysis, Key levels P&L"
        )
    
    except Exception as e:
        st.error(f"❌ Error generating export data: {str(e)}")
    
    # ======================== FOOTER ========================
    st.divider()
    st.markdown("""
    ---
    **Short Condor Strategy Analyzer v1.0**
    
    *Built with Streamlit | Valuation Model: Binomial (Cox-Ross-Rubinstein)*
    
    ⚠️ **Disclaimer:** This tool is provided for educational and demonstration purposes only.
    This is not financial advice. Always consult a qualified financial advisor before trading.
    """)


if __name__ == "__main__":
    main()
