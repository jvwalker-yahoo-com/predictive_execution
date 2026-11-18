# =========================================================
# Predictive Execution — Multi-Brain Federation Engine
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import Any, Dict

from engine.predict import predict
from engine.mode_history import record_mode_switch

app = FastAPI(title="Predictive Execution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _evaluate_federation(state: Dict[str, Any], pred: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Evaluate multi-brain federation votes across Risk, Impact, Slippage,
    Latency, and OpenBB Intelligence brains.
    """
    risk = float(state.get("risk", 0.2))
    impact = float(state.get("impact", 0.2))
    slippage = float(state.get("slippage", 0.2))
    latency = float(state.get("latency", 10.0))

    votes = {
        "RiskBrain": "LIVE" if risk < 0.60 else ("SHADOW" if risk < 0.80 else "HALT"),
        "ImpactBrain": "LIVE" if impact < 0.60 else ("SHADOW" if impact < 0.80 else "HALT"),
        "SlippageBrain": "LIVE" if slippage < 0.60 else ("SHADOW" if slippage < 0.80 else "HALT"),
        "LatencyBrain": "LIVE" if latency < 25.0 else "SHADOW",
        "OpenBBBrain": "LIVE" if (pred or {}).get("final_mode", "OK") == "OK" else "SHADOW",
    }

    halt_count = sum(1 for v in votes.values() if v == "HALT")
    shadow_count = sum(1 for v in votes.values() if v == "SHADOW")
    live_count = sum(1 for v in votes.values() if v == "LIVE")

    if halt_count >= 1:
        mode = "HALT"
    elif shadow_count >= 2:
        mode = "SHADOW"
    else:
        mode = "LIVE"

    confidence = round(max(live_count, shadow_count, halt_count) / len(votes), 2)
    obb_dec = (pred or {}).get("openbb_decision", {})
    reasons = obb_dec.get("drivers") or [
        f"Risk={risk:.3f}, Impact={impact:.3f}, Slippage={slippage:.3f}, Latency={latency:.1f}ms"
    ]

    outputs = [
        {"name": f"risk:{risk:.4f}", "vote": votes["RiskBrain"]},
        {"name": f"impact:{impact:.4f}", "vote": votes["ImpactBrain"]},
        {"name": f"slippage:{slippage:.4f}", "vote": votes["SlippageBrain"]},
        {"name": f"openbb:{obb_dec.get('action', 'HOLD')}", "vote": votes["OpenBBBrain"]},
    ]

    return {
        "mode": mode,
        "confidence": confidence,
        "votes": votes,
        "reasons": reasons,
        "outputs": outputs,
    }


federation_engine = {
    "evaluate": _evaluate_federation,
}


def generate_state(pred: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "regime": "NORMAL" if pred.get("final_mode") == "OK" else pred.get("final_mode", "NORMAL"),
        "risk": pred["risk"],
        "slippage": pred["slippage"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "sync": 0,
        "fill_quality": 1,
        "signal_action": pred.get("signal_action", "HOLD"),
        "conviction_score": pred.get("conviction_score", 5.0),
    }


def generate_decision(pred: Dict[str, Any], federation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "autonomous": "ON",
        "final_mode": federation["mode"],
        "signal_action": pred.get("signal_action", "HOLD"),
        "conviction_score": pred.get("conviction_score", 5.0),
        "arbitration": [
            {
                "finalMode": federation["mode"],
                "reason": "; ".join(federation["reasons"]),
                "arbitrationNotes": {
                    "confidence": federation["confidence"],
                    "votes": federation["votes"],
                },
            }
        ],
    }


def generate_federation(federation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "outputs": [o["name"] for o in federation["outputs"]],
        "federation": {
            "mode": federation["mode"],
            "confidence": federation["confidence"],
            "votes": federation["votes"],
            "reasons": federation["reasons"],
        },
    }


def generate_arbitration(federation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "final_mode": federation["mode"],
        "reason": "; ".join(federation["reasons"]),
        "arbitrationNotes": {
            "confidence": federation["confidence"],
            "votes": federation["votes"],
        },
    }


def generate_episode(pred: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "symbol": pred.get("symbol", "AAPL"),
        "riskScore": pred["risk"],
        "timestamp": time.time(),
        "impactBps": pred["impact"],
        "syncDriftMs": 0,
        "autopilotMode": "ON",
        "twinStatus": "ALIGNED",
        "tags": [pred.get("signal_action", "HOLD")],
    }


def generate_performance(pred: Dict[str, Any], federation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": int(time.time()),
        "riskScore": pred["risk"],
        "impactBps": pred["impact"],
        "finalMode": federation["mode"],
        "timestamp": time.time(),
        "name": "Federation",
        "slippageBps": pred["slippage"],
        "safetyTriggered": federation["mode"] != "LIVE",
    }


def generate_precedent(pred: Dict[str, Any], federation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": time.time(),
        "final_mode": federation["mode"],
        "risk": pred["risk"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "slippage": pred["slippage"],
    }


def run_tick(symbol: str = "AAPL") -> Dict[str, Any]:
    raw = predict(symbol) or {}

    pred = {
        "symbol": raw.get("symbol", symbol),
        "risk": raw.get("risk", 0.1),
        "impact": raw.get("impact", 0),
        "latency": raw.get("latency", 1),
        "slippage": raw.get("slippage", 0),
        "final_mode": raw.get("final_mode", "OK"),
        "signal_action": raw.get("signal_action", "HOLD"),
        "conviction_score": raw.get("conviction_score", 5.0),
        "openbb_decision": raw.get("openbb_decision", {}),
    }

    state = generate_state(pred)
    federation = _evaluate_federation(state, pred)
    record_mode_switch(federation["mode"], federation, pred)

    return {
        "prediction": pred,
        "state": state,
        "decision": generate_decision(pred, federation),
        "federation": generate_federation(federation),
        "arbitration": generate_arbitration(federation),
        "episode": generate_episode(pred),
        "performance": generate_performance(pred, federation),
        "precedent": generate_precedent(pred, federation),
    }


@app.get("/state")
def get_state(symbol: str = "AAPL"):
    return run_tick(symbol)["state"]


@app.get("/decision")
def get_decision(symbol: str = "AAPL"):
    return run_tick(symbol)["decision"]


@app.get("/federation")
def get_federation(symbol: str = "AAPL"):
    return run_tick(symbol)["federation"]


@app.get("/arbitration")
def get_arbitration(symbol: str = "AAPL"):
    return run_tick(symbol)["arbitration"]


@app.get("/episodes")
def get_episodes(symbol: str = "AAPL"):
    return [run_tick(symbol)["episode"]]


@app.get("/performance")
def get_performance(symbol: str = "AAPL"):
    return [run_tick(symbol)["performance"]]


@app.get("/precedents")
def get_precedents(symbol: str = "AAPL"):
    return [run_tick(symbol)["precedent"]]


@app.get("/predict")
def get_predict(symbol: str = "AAPL"):
    return run_tick(symbol)["prediction"]
