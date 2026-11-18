"""
Predictive Execution Cockpit & OpenBB Decision System - Streamlit Edition
Visualizes operational regime, risk/impact/slippage quadrants, OpenBB Unified Data Router
intelligence (Deep Equity Fundamentals, Global News Sentiment, FRED Macro), and live decision mandates.
"""

import random
import pandas as pd
import streamlit as st
from engine.predict import predict
from market_intel import MarketIntelSuite

st.set_page_config(
    page_title="Predictive Execution & OpenBB Decision Cockpit",
    page_icon="⚡",
    layout="wide",
)

intel = MarketIntelSuite()

st.title("⚡ Predictive Execution Cockpit & OpenBB Decision Engine")
st.caption(
    "Unified Data Router (obb) • Multi-Brain Arbitration • Deep Equity Fundamentals • Global News Sentiment • FRED Macro • SEC EDGAR"
)

# Sidebar
st.sidebar.header("🕹️ Execution & OpenBB Controls")
asset = st.sidebar.selectbox(
    "Active Ticker",
    ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "META", "AMD", "GOOGL", "PLTR", "SPY"],
    index=0,
)
auto_refresh = st.sidebar.checkbox("Live Telemetry Mode", value=True)

# Execute OpenBB-grounded prediction & intelligence bundle
pred_bundle = predict(asset)
obb_bundle = intel.get_openbb_intelligence(asset)
obb_dec = pred_bundle.get("openbb_decision", {})
qt = obb_bundle.get("quote_technicals", {})
fund = obb_bundle.get("fundamentals", {})
news = obb_bundle.get("news_sentiment", {})
macro = obb_bundle.get("macro", {})

risk = float(pred_bundle["risk"])
impact = float(pred_bundle["impact"])
slippage = float(pred_bundle["slippage"])
latency = float(pred_bundle["latency"])
regime_mode = str(pred_bundle["final_mode"])
signal_action = str(pred_bundle.get("signal_action", "HOLD"))
conviction = float(pred_bundle.get("conviction_score", 5.0))

# Top KPI row
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
c1.metric("OPENBB MANDATE", signal_action)
c2.metric("CONVICTION", f"{conviction:.1f} / 10")
c3.metric("REGIME MODE", regime_mode)
c4.metric("RISK SCORE", f"{risk:.3f}")
c5.metric("MARKET IMPACT", f"{impact:.3f}")
c6.metric("SLIPPAGE", f"{slippage:.3f}")
c7.metric("LATENCY", f"{latency:.1f}ms")

st.divider()

# Cockpit Tabs
t_cockpit, t_fund, t_news, t_sec, t_macro = st.tabs([
    "🎯 OpenBB Decision & Execution Cockpit",
    "📊 Deep Equity & Fundamentals",
    "📰 Global News & Sentiment",
    "🏛️ SEC EDGAR Filings & Ticks",
    "🌍 Global Macro, Forex & Crypto Pulse",
])

with t_cockpit:
    col_l, col_r = st.columns([1.4, 1.6])
    with col_l:
        st.subheader("Regime State & Microstructure Telemetry")
        st.progress(min(1.0, risk), text=f"Model Risk (Vol + Macro + News): {risk:.3f}")
        st.progress(min(1.0, impact), text=f"Market Impact (Order/Liquidity): {impact:.3f}")
        st.progress(min(1.0, slippage), text=f"Estimated Slippage (Spread {qt.get('estimated_spread_bps', 2.5)} bps): {slippage:.3f}")

        q = (
            "LOW" if risk < 0.33 and impact < 0.33
            else ("MEDIUM" if risk < 0.66 and impact < 0.66 else ("HIGH" if impact >= 0.66 else "CRITICAL"))
        )
        st.info(
            f"**Quadrant Classification:** {q} | **Provider:** `{qt.get('provider', 'openbb')}` | **Drift:** {random.randint(10, 45)}ms"
        )

        st.markdown("#### Factor Point Attribution")
        f_scores = obb_dec.get("factor_scores", {})
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Technicals", f"{f_scores.get('technicals', 0.0):+.2f}")
        fc2.metric("Fundamentals", f"{f_scores.get('fundamentals', 0.0):+.2f}")
        fc3.metric("News Catalyst", f"{f_scores.get('news_sentiment', 0.0):+.2f}")
        fc4.metric("Macro Filter", f"{f_scores.get('macro_regime', 0.0):+.2f}")

    with col_r:
        st.subheader(f"🎯 OpenBB Decision Mandate • {asset}")
        price = float(qt.get("price", 0.0))
        st.metric(
            f"{asset} Spot Price",
            f"${price:.2f}",
            f"{qt.get('change_pct', 0.0):+.2f}%",
        )
        m_a, m_b, m_c = st.columns(3)
        m_a.metric("Stop Loss (1.5 ATR)", f"${obb_dec.get('stop_loss', 0.0):.2f}")
        m_b.metric("Take Profit (2.5 ATR)", f"${obb_dec.get('take_profit', 0.0):.2f}")
        m_c.metric(
            "Analyst Target",
            f"${fund.get('target_mean'):.2f}" if fund.get("target_mean") else "N/A",
            f"{obb_dec.get('upside_pct', 0.0):+.1f}%",
        )

        st.markdown("#### Multi-Brain Decision Evidence")
        for drv in obb_dec.get("drivers", []):
            st.write(f"• {drv}")

with t_fund:
    st.subheader(f"📊 Deep Equity & Fundamentals • {asset}")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Trailing P/E", f"{fund['pe_ratio']:.2f}" if isinstance(fund.get("pe_ratio"), (int, float)) else "N/A")
    f2.metric("Forward P/E", f"{fund['forward_pe']:.2f}" if isinstance(fund.get("forward_pe"), (int, float)) else "N/A")
    f3.metric(
        "Profit Margin",
        f"{fund['profit_margin'] * 100:.1f}%" if isinstance(fund.get("profit_margin"), (int, float)) else "N/A",
    )
    f4.metric(
        "Return on Equity (ROE)",
        f"{fund['return_on_equity'] * 100:.1f}%" if isinstance(fund.get("return_on_equity"), (int, float)) else "N/A",
    )

    f5, f6, f7, f8 = st.columns(4)
    f5.metric("Wall St Consensus", str(fund.get("recommendation", "Hold")))
    f6.metric("Fundamental Health", f"{fund.get('fundamental_score', 0.5):.2f} / 1.00")
    f7.metric("VWAP / SMA20", f"${qt.get('vwap', 0.0):.2f} / ${qt.get('sma20', 0.0):.2f}")
    f8.metric("RSI (14) / Ann. Vol", f"{qt.get('rsi14', 50.0):.1f} / {qt.get('realized_volatility', 0.22) * 100:.1f}%")

with t_news:
    st.subheader(f"📰 Global News & Sentiment • {asset}")
    n1, n2, n3 = st.columns(3)
    n1.metric("Sentiment Regime", str(news.get("sentiment_label", "NEUTRAL")))
    n2.metric("Net Sentiment Score", f"{news.get('net_sentiment', 0.0):+.2f}")
    n3.metric("Articles Analyzed", str(news.get("count", 0)))

    for art in news.get("articles", []):
        st.markdown(
            f"**[{art.get('sentiment', 'NEUTRAL')}] [{art.get('headline', '')}]({art.get('url', '#')})** — *{art.get('source', 'Wire')}*  \n"
            f"{art.get('summary', '')}"
        )

with t_sec:
    st.subheader(f"📄 Direct SEC EDGAR Corporate Filings • {asset}")
    filings = intel.get_sec_edgar_filings(asset, limit=10)
    if filings:
        st.dataframe(pd.DataFrame(filings), use_container_width=True, hide_index=True)
    else:
        st.info("No SEC filings found.")

with t_macro:
    st.subheader("Federal Reserve Macroeconomic Indicators (FRED)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fed Funds Rate", f"{macro.get('fed_funds_rate', {}).get('value', 3.75):.2f}%")
    m2.metric("10Y Treasury Yield", f"{macro.get('treasury_10y', {}).get('value', 4.12):.2f}%")
    m3.metric("Yield Curve Spread", f"{macro.get('yield_curve_spread', 0.37):+.2f}%")
    m4.metric("Macro Regime", str(macro.get("macro_regime", "NORMAL")))

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
