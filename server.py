# =========================================================
# Predictive Execution – Full FastAPI Server (OpenBB Enriched)
# =========================================================

import asyncio
import math
import random
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine.mode_history import get_mode_history
from engine.openbb_intel import obb_router
from engine.predict import (
    impact_model,
    latency_model,
    mode_model,
    predict,
    risk_model,
    slippage_model,
    synthesize_openbb_decision,
)
from market_intel import MarketIntelSuite

app = FastAPI(
    title="Predictive Execution & OpenBB Decision Engine",
    version="2.0.0",
)

# -----------------------------
# CORS (REQUIRED FOR DASHBOARD)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

intel_engine = MarketIntelSuite()


# -----------------------------
# INTERNAL MODEL WRAPPERS
# -----------------------------
def model_risk(symbol: str = "AAPL") -> float:
    intel = obb_router.get_full_intelligence_bundle(symbol)
    return risk_model(intel)


def model_impact(symbol: str = "AAPL") -> float:
    intel = obb_router.get_full_intelligence_bundle(symbol)
    return impact_model(intel)


def model_slippage(symbol: str = "AAPL") -> float:
    intel = obb_router.get_full_intelligence_bundle(symbol)
    return slippage_model(intel)


def model_latency(symbol: str = "AAPL") -> float:
    intel = obb_router.get_full_intelligence_bundle(symbol)
    return latency_model(intel)


def model_mode(risk: float, impact: float, slippage: float) -> str:
    return mode_model(risk, impact, slippage)


def model_federation(symbol: str = "AAPL"):
    bundle = predict(symbol)
    obb_dec = bundle.get("openbb_decision", {})
    return {
        "outputs": [
            f"risk:{bundle['risk']}",
            f"impact:{bundle['impact']}",
            f"slippage:{bundle['slippage']}",
            f"openbb_action:{bundle.get('signal_action', 'HOLD')}",
            f"conviction:{bundle.get('conviction_score', 5.0)}",
        ],
        "federation": "OpenBBMultiBrain",
        "signal_action": bundle.get("signal_action", "HOLD"),
        "conviction_score": bundle.get("conviction_score", 5.0),
        "factors": obb_dec.get("factor_scores", {}),
    }


# -----------------------------
# CORE COCKPIT ENDPOINTS
# -----------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "OpenBB Predictive Execution v2.0",
        "openbb_router": "active",
    }


@app.get("/state")
def state(symbol: str = "AAPL"):
    bundle = predict(symbol)
    return {
        "symbol": bundle["symbol"],
        "regime": "NORMAL" if bundle["final_mode"] == "OK" else bundle["final_mode"],
        "risk": bundle["risk"],
        "impact": bundle["impact"],
        "slippage": bundle["slippage"],
        "latency": bundle["latency"],
        "events": round(random.uniform(0.1, 1.5), 4),
        "fill_quality": round(max(0.80, 1.0 - (bundle["slippage"] * 0.15)), 4),
        "signal_action": bundle["signal_action"],
        "conviction_score": bundle["conviction_score"],
    }


@app.get("/decision")
def decision(symbol: str = "AAPL"):
    bundle = predict(symbol)
    mode = bundle["final_mode"]
    obb_dec = bundle["openbb_decision"]

    return {
        "autonomous": "ON",
        "symbol": bundle["symbol"],
        "main_mode": mode,
        "finalMode": mode,
        "signal_action": obb_dec["action"],
        "conviction_score": obb_dec["conviction_score"],
        "price": obb_dec["price"],
        "stop_loss": obb_dec["stop_loss"],
        "take_profit": obb_dec["take_profit"],
        "reason": " | ".join(obb_dec.get("drivers", ["OpenBB multi-factor arbitration"])),
        "arbitrationNotes": obb_dec.get("factor_scores", {}),
    }


@app.get("/federation")
def federation(symbol: str = "AAPL"):
    return model_federation(symbol)


@app.get("/arbitration")
def arbitration(symbol: str = "AAPL"):
    bundle = predict(symbol)
    mode = bundle["final_mode"]
    obb_dec = bundle["openbb_decision"]

    return {
        "symbol": bundle["symbol"],
        "final_mode": mode,
        "signal_action": obb_dec["action"],
        "conviction_score": obb_dec["conviction_score"],
        "reason": " | ".join(obb_dec.get("drivers", ["OpenBB model arbitration"])),
        "arbitrationNotes": obb_dec.get("factor_scores", {}),
    }


@app.get("/anomaly_detector")
def anomaly_detector(symbol: str = "AAPL"):
    bundle = predict(symbol)
    return {
        "risk_spike": bundle["risk"] > 0.85,
        "latency_spike": bundle["latency"] > 20.0,
        "impact_jump": bundle["impact"] > 0.85,
        "slippage_jump": bundle["slippage"] > 0.85,
    }


@app.get("/node_events")
def node_events():
    history = get_mode_history()
    if history:
        return {"events": history[-10:]}
    now = time.time()
    return {
        "events": [
            {"mode": "OK", "timestamp": now},
            {"mode": "WARN", "timestamp": now - 5},
            {"mode": "OK", "timestamp": now - 10},
        ]
    }


@app.get("/quadrant")
def quadrant(symbol: str = "AAPL"):
    bundle = predict(symbol)
    risk = bundle["risk"]
    impact = bundle["impact"]

    if risk < 0.33 and impact < 0.33:
        q = "LOW"
    elif risk < 0.66 and impact < 0.66:
        q = "MEDIUM"
    elif risk < 0.66 and impact >= 0.66:
        q = "HIGH"
    else:
        q = "CRITICAL"

    return {
        "symbol": bundle["symbol"],
        "risk": risk,
        "impact": impact,
        "quadrant": q,
    }


@app.get("/heartbeat")
def heartbeat():
    return {"alive": True, "timestamp": time.time()}


@app.get("/sync_drift")
def sync_drift():
    drift = random.randint(8, 65)
    return {"drift_ms": drift, "status": "OK" if drift < 120 else "DRIFTING"}


# =========================================================================
# GLOBAL MARKET & OPENBB INTELLIGENCE ENDPOINTS
# =========================================================================
@app.get("/api/macro/forex", tags=["Market Intelligence"])
async def get_macro_forex(base: str = "USD"):
    return await asyncio.to_thread(intel_engine.get_forex_rates, base)


@app.get("/api/macro/crypto", tags=["Market Intelligence"])
async def get_macro_crypto():
    return await asyncio.to_thread(intel_engine.get_crypto_prices)


@app.get("/api/macro/fred", tags=["Market Intelligence"])
async def get_macro_fred():
    return await asyncio.to_thread(intel_engine.get_fred_macro_indicators)


@app.get("/api/sec/filings/{symbol}", tags=["Market Intelligence"])
async def get_sec_filings(symbol: str, limit: int = 10):
    return await asyncio.to_thread(intel_engine.get_sec_edgar_filings, symbol, limit)


@app.get("/api/market/ticks/{symbol}", tags=["Market Intelligence"])
async def get_market_ticks(symbol: str):
    return await asyncio.to_thread(intel_engine.get_stock_ticks_and_quote, symbol)


@app.get("/api/openbb/intelligence/{symbol}", tags=["OpenBB Intelligence"])
async def get_openbb_intelligence(symbol: str):
    return await asyncio.to_thread(obb_router.get_full_intelligence_bundle, symbol)


@app.get("/api/openbb/decision/{symbol}", tags=["OpenBB Intelligence"])
async def get_openbb_decision(symbol: str):
    return await asyncio.to_thread(synthesize_openbb_decision, symbol)


@app.get("/api/openbb/fundamentals/{symbol}", tags=["OpenBB Intelligence"])
async def get_openbb_fundamentals(symbol: str):
    return await asyncio.to_thread(obb_router.get_equity_fundamentals, symbol)


@app.get("/api/openbb/news/{symbol}", tags=["OpenBB Intelligence"])
async def get_openbb_news(symbol: str, limit: int = 8):
    return await asyncio.to_thread(obb_router.get_global_news_sentiment, symbol, limit)
