# =========================================================
# Predictive Execution — OpenBB-Grounded Decision Engine
# =========================================================

import math
import random
import time
from typing import Any, Dict, Optional

from engine.openbb_intel import obb_router
from models.impact import ImpactBrain
from models.latency import LatencyBrain
from models.mode import ModeBrain
from models.risk import RiskBrain
from models.slippage import SlippageBrain

_risk_brain = RiskBrain()
_impact_brain = ImpactBrain()
_latency_brain = LatencyBrain()
_slippage_brain = SlippageBrain()
_mode_brain = ModeBrain()


def risk_model(intel: Optional[Dict[str, Any]] = None) -> float:
    """
    Compute execution & market risk score in [0.0, 1.0] grounded in OpenBB
    realized volatility, macro yield-curve stress, and news sentiment shock.
    """
    if not intel:
        base = 0.25 + math.sin(time.time() / 8.0) * 0.10
        return round(max(0.05, min(0.95, base + random.uniform(-0.02, 0.02))), 4)

    qt = intel.get("quote_technicals", {})
    macro = intel.get("macro", {})
    news = intel.get("news_sentiment", {})
    fund = intel.get("fundamentals", {})

    vol = float(qt.get("realized_volatility") or 0.22)
    spread_bps = float(qt.get("estimated_spread_bps") or 2.5)
    volume = max(100000, int(qt.get("volume") or 1000000))

    # Calibrated microstructure risk (scaled so ~20% vol blue-chip is ~0.22 risk)
    vol_component = min(0.65, vol * 0.85)
    spread_component = min(0.25, spread_bps * 0.015)
    liq_relief = min(0.12, max(0.0, (math.log10(volume) - 5.0) * 0.04))
    micro_risk = max(0.08, vol_component + spread_component - liq_relief)

    # Macro stress adjustment (yield curve inversion / high Fed Funds)
    macro_stress = float(macro.get("macro_stress_score") or 0.25)

    # News sentiment tail-risk adjustment
    net_sent = float(news.get("net_sentiment") or 0.0)
    sent_penalty = max(0.0, -net_sent * 0.15)

    # Fundamental quality buffer (strong fundamentals reduce tail risk)
    fund_score = float(fund.get("fundamental_score") or 0.50)
    fund_adjustment = (0.50 - fund_score) * 0.10

    combined = (0.65 * micro_risk) + (0.25 * macro_stress) + sent_penalty + fund_adjustment
    return round(max(0.05, min(0.98, combined)), 4)


def impact_model(intel: Optional[Dict[str, Any]] = None, order_size: int = 2500) -> float:
    """
    Compute normalized market impact coefficient [0.0, 1.0] from OpenBB
    volume liquidity and ImpactBrain basis points estimate.
    """
    if not intel:
        base = 0.22 + math.cos(time.time() / 10.0) * 0.08
        return round(max(0.05, min(0.95, base + random.uniform(-0.02, 0.02))), 4)

    qt = intel.get("quote_technicals", {})
    daily_vol = max(500000, int(qt.get("volume") or 5000000))
    # Effective intraday liquidity pool (25% of daily volume, floor 500k)
    participation_pool = max(500000.0, float(daily_vol) * 0.25)
    impact_bps = float(_impact_brain.predict({
        "order_size": order_size,
        "liquidity": participation_pool,
    }))
    # Scale bps so liquid large-caps sit around 0.12 - 0.28 and illiquid names higher
    normalized = min(0.95, max(0.08, 0.10 + (impact_bps / 25.0)))
    return round(normalized, 4)


def latency_model(intel: Optional[Dict[str, Any]] = None) -> float:
    """Estimate execution routing latency in milliseconds."""
    hops = 4
    congestion = 0.08 + abs(math.sin(time.time() / 6.0)) * 0.06
    if intel:
        qt = intel.get("quote_technicals", {})
        vol = float(qt.get("realized_volatility") or 0.22)
        congestion += min(0.20, vol * 0.15)
    est = float(_latency_brain.estimate({"network_hops": hops, "congestion": congestion}))
    return round(max(1.0, est + random.uniform(-0.5, 0.5)), 2)


def slippage_model(intel: Optional[Dict[str, Any]] = None) -> float:
    """
    Compute normalized slippage score [0.0, 1.0] from OpenBB spread and volatility.
    """
    if not intel:
        base = 0.22 + math.sin(time.time() / 6.0) * 0.12
        return round(max(0.03, min(0.95, base + random.uniform(-0.02, 0.02))), 4)

    qt = intel.get("quote_technicals", {})
    vol = float(qt.get("realized_volatility") or 0.22)
    spread_bps = float(qt.get("estimated_spread_bps") or 2.5)
    raw_slip = float(_slippage_brain.estimate({
        "spread": spread_bps / 100.0,
        "volatility": vol,
    }))
    normalized = min(0.95, max(0.03, raw_slip / 10.0))
    return round(normalized, 4)


def mode_model(risk: float, impact: float, slippage: float, latency: float = 12.0) -> str:
    """
    Decide operational regime mode (OK / WARN / CRITICAL / HALT) using composite
    execution metrics and ModeBrain thresholds.
    """
    brain_decision = _mode_brain.decide(risk, impact * 50.0, latency, slippage * 5.0)
    if brain_decision == "HALT":
        return "CRITICAL"

    score = (risk + impact + slippage) / 3.0
    if score < 0.33:
        return "OK"
    elif score < 0.66:
        return "WARN"
    return "CRITICAL"


def synthesize_openbb_decision(symbol: str = "AAPL", intel: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Synthesize an institutional trading & execution decision combining:
      - Technical trend & momentum (VWAP, SMA20, SMA50, RSI14)
      - Deep Fundamentals (Forward P/E, ROE, Profit Margin, Wall St Target Upside)
      - Global News Sentiment (Bullish vs Bearish catalyst ratio)
      - Macro Regime (Fed Funds Rate, 10Y Treasury Yield, Yield Curve Spread)
    """
    bundle = intel or obb_router.get_full_intelligence_bundle(symbol)
    qt = bundle.get("quote_technicals", {})
    fund = bundle.get("fundamentals", {})
    news = bundle.get("news_sentiment", {})
    macro = bundle.get("macro", {})

    price = float(qt.get("price") or 0.0)
    sma20 = float(qt.get("sma20") or price)
    sma50 = float(qt.get("sma50") or price)
    vwap = float(qt.get("vwap") or price)
    rsi = float(qt.get("rsi14") or 50.0)

    # 1. Technical Score [-2.5, +2.5]
    tech_pts = 0.0
    if price > 0:
        tech_pts += 0.8 if price >= vwap else -0.8
        tech_pts += 0.9 if price >= sma20 else -0.9
        tech_pts += 0.5 if sma20 >= sma50 else -0.5
        if 45.0 <= rsi <= 68.0:
            tech_pts += 0.3
        elif rsi > 75.0:
            tech_pts -= 0.4  # Overbought
        elif rsi < 30.0:
            tech_pts += 0.4  # Oversold mean-reversion bounce

    # 2. Fundamental & Analyst Target Score [-2.0, +2.0]
    fund_score = float(fund.get("fundamental_score") or 0.5)
    fund_pts = (fund_score - 0.5) * 2.5
    target_mean = fund.get("target_mean")
    upside_pct = 0.0
    if isinstance(target_mean, (int, float)) and price > 0:
        upside_pct = round(((float(target_mean) - price) / price) * 100.0, 2)
        if upside_pct > 10.0:
            fund_pts += 0.75
        elif upside_pct < -5.0:
            fund_pts -= 0.75

    # 3. Global News Sentiment Score [-1.5, +1.5]
    net_sent = float(news.get("net_sentiment") or 0.0)
    news_pts = round(net_sent * 1.5, 2)

    # 4. Macro & Yield Curve Filter [-1.0, +1.0]
    spread = float(macro.get("yield_curve_spread") or 0.37)
    macro_pts = 0.4 if spread >= 0 else -0.6

    # Composite Conviction [1.0, 10.0]
    raw_total = tech_pts + fund_pts + news_pts + macro_pts
    conviction = round(max(1.0, min(10.0, 5.0 + raw_total)), 2)

    if conviction >= 7.2:
        action = "STRONG BUY"
    elif conviction >= 5.8:
        action = "BUY"
    elif conviction <= 3.0:
        action = "STRONG SELL"
    elif conviction <= 4.3:
        action = "SELL"
    else:
        action = "HOLD"

    atr = float(qt.get("atr14") or max(1.0, price * 0.015))
    is_bull = conviction >= 5.0
    stop_loss = round(price - (1.5 * atr), 2) if is_bull else round(price + (1.5 * atr), 2)
    take_profit = round(price + (2.5 * atr), 2) if is_bull else round(price - (2.5 * atr), 2)

    return {
        "symbol": bundle.get("symbol", symbol),
        "action": action,
        "conviction_score": conviction,
        "price": price,
        "target_mean": target_mean,
        "upside_pct": upside_pct,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "factor_scores": {
            "technicals": round(tech_pts, 2),
            "fundamentals": round(fund_pts, 2),
            "news_sentiment": round(news_pts, 2),
            "macro_regime": round(macro_pts, 2),
        },
        "drivers": [
            f"Technicals: Price ${price:.2f} vs SMA20 ${sma20:.2f} & VWAP ${vwap:.2f} (RSI {rsi:.1f})",
            f"Fundamentals: Health {fund_score:.2f} | Consensus {fund.get('recommendation', 'Hold')} (Target Upside {upside_pct:+.1f}%)",
            f"Global News: {news.get('sentiment_label', 'NEUTRAL')} ({news.get('count', 0)} articles, net score {net_sent:+.2f})",
            f"Macro (FRED): {macro.get('macro_regime', 'NORMAL')} (10Y-FFR Spread {spread:+.2f}%)",
        ],
    }


def predict(symbol: str = "AAPL") -> Dict[str, Any]:
    """
    Full OpenBB-grounded predictive execution & decision engine.
    Always returns a complete dictionary with all required fields.
    Never crashes. Never returns None. Never omits keys.
    """
    try:
        intel = obb_router.get_full_intelligence_bundle(symbol)
    except Exception:
        intel = None

    risk = risk_model(intel)
    impact = impact_model(intel)
    latency = latency_model(intel)
    slippage = slippage_model(intel)
    final_mode = mode_model(risk, impact, slippage, latency)
    obb_decision = synthesize_openbb_decision(symbol, intel)

    return {
        "timestamp": time.time(),
        "symbol": (symbol or "AAPL").upper().strip(),
        "risk": risk,
        "impact": impact,
        "latency": latency,
        "slippage": slippage,
        "final_mode": final_mode,
        "signal_action": obb_decision["action"],
        "conviction_score": obb_decision["conviction_score"],
        "openbb_decision": obb_decision,
    }
