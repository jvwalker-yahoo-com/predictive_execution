"""
Predictive Execution Cockpit - Streamlit Edition
Visualizes operational regime, risk/impact/slippage quadrants, and live market intelligence
(Frankfurter, CoinGecko, FRED, SEC EDGAR, Polygon/Finnhub).
"""

import time
import math
import random
import pandas as pd
import streamlit as st
from market_intel import MarketIntelSuite

st.set_page_config(page_title="Predictive Execution Cockpit", page_icon="⚡", layout="wide")

intel = MarketIntelSuite()

st.title("⚡ Predictive Execution Cockpit & Market Confluence")
st.caption("Real-Time Operational Cockpit • Regime State • Global Macro • SEC EDGAR • Polygon Ticks")

# Sidebar
st.sidebar.header("🕹️ Execution Controls")
asset = st.sidebar.selectbox("Active Ticker", ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "AMD"], index=0)
auto_refresh = st.sidebar.checkbox("Auto Refresh Simulation", value=True)

# Metrics Simulation (from 1. System Purpose.txt)
t = time.time()
risk = round(max(0.0, min(1.0, 0.35 + math.sin(t / 8) * 0.25 + random.uniform(-0.03, 0.03))), 3)
impact = round(max(0.0, min(1.0, 0.40 + math.cos(t / 10) * 0.20 + random.uniform(-0.03, 0.03))), 3)
slippage = round(max(0.0, min(1.0, 0.30 + math.sin(t / 6) * 0.30 + random.uniform(-0.03, 0.03))), 3)
latency = round(max(1.0, 12.0 + math.sin(t / 4) * 6.0 + random.uniform(-1.0, 1.0)), 1)
score = (risk + impact + slippage) / 3.0
regime_mode = "OK" if score < 0.33 else ("WARN" if score < 0.66 else "CRITICAL")
mode_color = "#00e676" if regime_mode == "OK" else ("#f59e0b" if regime_mode == "WARN" else "#ff5252")

# Top KPI row
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("REGIME MODE", regime_mode)
c2.metric("RISK COEFFICIENT", f"{risk:.3f}")
c3.metric("MARKET IMPACT", f"{impact:.3f}")
c4.metric("SLIPPAGE", f"{slippage:.3f}")
c5.metric("LATENCY", f"{latency:.1f}ms")

st.divider()

# Cockpit Tabs
t_cockpit, t_sec, t_macro = st.tabs([
    "📊 Predictive Execution Cockpit",
    "🏛️ SEC EDGAR Filings & Polygon Ticks",
    "🌍 Global Macro, Forex & Crypto Pulse"
])

with t_cockpit:
    col_l, col_r = st.columns([1.5, 1.5])
    with col_l:
        st.subheader("Regime State & Anomaly Radar")
        st.progress(min(1.0, risk), text=f"Model Risk: {risk:.3f}")
        st.progress(min(1.0, impact), text=f"Market Impact: {impact:.3f}")
        st.progress(min(1.0, slippage), text=f"Estimated Slippage: {slippage:.3f}")
        
        q = "LOW" if risk < 0.33 and impact < 0.33 else ("MEDIUM" if risk < 0.66 and impact < 0.66 else ("HIGH" if impact >= 0.66 else "CRITICAL"))
        st.info(f"**Quadrant Classification:** {q} | **Drift:** {random.randint(10, 85)}ms (Nominal)")

    with col_r:
        st.subheader(f"⚡ Intraday Ticks: {asset}")
        quote = intel.get_stock_ticks_and_quote(asset)
        if quote.get("price", 0) > 0:
            st.metric(f"{asset} Price", f"${quote['price']:.2f}", f"{quote.get('change_pct', 0):+.2f}%")
            st.write(f"• **Day Range:** ${quote.get('low', 0):.2f} - ${quote.get('high', 0):.2f}")
            st.write(f"• **Open / Prev Close:** ${quote.get('open', 0):.2f} / ${quote.get('prev_close', 0):.2f}")
            st.caption(f"Source: {quote.get('source', 'Finnhub').upper()}")
        else:
            st.info("Market data syncing...")

with t_sec:
    st.subheader(f"📄 Direct SEC EDGAR Corporate Filings • {asset}")
    filings = intel.get_sec_edgar_filings(asset, limit=10)
    if filings:
        st.dataframe(pd.DataFrame(filings), use_container_width=True, hide_index=True)
    else:
        st.info("No SEC filings found.")

with t_macro:
    st.subheader("Federal Reserve Macroeconomic Indicators (FRED)")
    fred = intel.get_fred_macro_indicators()
    m1, m2, m3 = st.columns(3)
    m1.metric("Fed Funds Rate", f"{fred.get('fed_funds_rate', {}).get('value', 3.75):.2f}%")
    m2.metric("10Y Treasury Yield", f"{fred.get('treasury_10y', {}).get('value', 4.12):.2f}%")
    m3.metric("Yield Curve Spread", f"{fred.get('yield_curve_spread', 0.37):+.2f}%")

    st.markdown("---")
    st.subheader("💱 Real-Time Foreign Exchange (Frankfurter - Zero Auth)")
    fx = intel.get_forex_rates("USD", ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF"])
    fx_cols = st.columns(6)
    for i, (k, v) in enumerate(fx.get("rates", {}).items()):
        fx_cols[i % 6].metric(f"USD/{k}", f"{v:.4f}")

    st.markdown("---")
    st.subheader("🪙 Cryptocurrency Market Pulse (CoinGecko - Zero Auth)")
    cg = intel.get_crypto_prices(["bitcoin", "ethereum", "solana", "ripple"])
    cg_cols = st.columns(4)
    for i, (cid, cdata) in enumerate(cg.get("data", {}).items()):
        cg_cols[i % 4].metric(cdata["symbol"], f"${cdata['price_usd']:,.2f}", f"{cdata['change_24h_pct']:+.2f}%")
