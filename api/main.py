# =========================================================
# Predictive Execution API — Full System (Federation + Modes + History)
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

from engine.predict import predict
from engine.federation import federation_engine
from engine.mode_behaviour import apply_mode_behaviour
from engine.mode_history import record_mode_switch, get_mode_history

app = FastAPI(title="Predictive Execution API")

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# STATE GENERATOR
# ---------------------------------------------------------
def generate_state(pred):
    return {
        "regime": "NORMAL",
        "risk": pred["risk"],
        "slippage": pred["slippage"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "sync": 0,
        "fill_quality": 1,
    }

# ---------------------------------------------------------
# DECISION GENERATOR
# ---------------------------------------------------------
def generate_decision(pred, federation):
    return {
        "autonomous": "ON",
        "final_mode": federation["mode"],
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

# ---------------------------------------------------------
# FEDERATION PANEL
# ---------------------------------------------------------
def generate_federation(federation):
    return {
        "outputs": [o["name"] for o in federation["outputs"]],
        "federation": {
            "mode": federation["mode"],
            "confidence": federation["confidence"],
            "votes": federation["votes"],
            "reasons": federation["reasons"],
        },
    }

# ---------------------------------------------------------
# ARBITRATION PANEL
# ---------------------------------------------------------
def generate_arbitration(federation):
    return {
        "final_mode": federation["mode"],
        "reason": "; ".join(federation["reasons"]),
        "arbitrationNotes": {
            "confidence": federation["confidence"],
            "votes": federation["votes"],
        },
    }

# ---------------------------------------------------------
# EPISODE GENERATOR
# ---------------------------------------------------------
def generate_episode(pred):
    return {
        "id": str(uuid.uuid4()),
        "symbol": "CLOUD",
        "riskScore": pred["risk"],
        "timestamp": time.time(),
        "impactBps": pred["impact"],
        "syncDriftMs": 0,
        "autopilotMode": "ON",
        "twinStatus": "ALIGNED",
        "tags": [],
    }

# ---------------------------------------------------------
# PERFORMANCE PANEL
# ---------------------------------------------------------
def generate_performance(pred, federation):
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

# ---------------------------------------------------------
# PRECEDENT PANEL
# ---------------------------------------------------------
def generate_precedent(pred, federation):
    return {
        "timestamp": time.time(),
        "final_mode": federation["mode"],
        "risk": pred["risk"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "slippage": pred["slippage"],
    }

# ---------------------------------------------------------
# MAIN TICK — FULL PIPELINE
# ---------------------------------------------------------
def run_tick():
    raw = predict() or {}

    pred = {
        "risk": raw.get("risk", 0.1),
        "impact": raw.get("impact", 0),
        "latency": raw.get("latency", 1),
        "slippage": raw.get("slippage", 0),
        "final_mode": raw.get("final_mode", "OK"),
    }

    # Build state
    state = generate_state(pred)

    # Federation decides mode
    federation = federation_engine["evaluate"](state)
    mode = federation["mode"]

    # Apply mode behaviour
    adjusted_pred = apply_mode_behaviour(pred, mode)

    # Record mode switch
    record_mode_switch(mode, federation, adjusted_pred)

    return {
        "prediction": adjusted_pred,
        "state": state,
        "decision": generate_decision(adjusted_pred, federation),
        "federation": generate_federation(federation),
        "arbitration": generate_arbitration(federation),
        "episode": generate_episode(adjusted_pred),
        "performance": generate_performance(adjusted_pred, federation),
        "precedent": generate_precedent(adjusted_pred, federation),
        "mode_history": get_mode_history(),
    }

# ---------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------
@app.get("/state")
def get_state():
    return run_tick()["state"]

@app.get("/decision")
def get_decision():
    return run_tick()["decision"]

@app.get("/federation")
def get_federation():
    return run_tick()["federation"]

@app.get("/arbitration")
def get_arbitration():
    return run_tick()["arbitration"]

@app.get("/episodes")
def get_episodes():
    return [run_tick()["episode"]]

@app.get("/performance")
def get_performance():
    return [run_tick()["performance"]]

@app.get("/precedents")
def get_precedents():
    return [run_tick()["precedent"]]

@app.get("/predict")
def get_predict():
    return run_tick()["prediction"]

@app.get("/mode_history")
def get_mode_history_endpoint():
    return get_mode_history()
