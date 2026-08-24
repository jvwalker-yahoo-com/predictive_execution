# paste FastAPI server here
# engine/predict.py
# Full real-model predictive engine for your cloud backend
# api/main.py
# Full FastAPI backend wired to real models and dashboard endpoints
# api/main.py
# Complete FastAPI backend for Predictive Execution Dashboard

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

from engine.predict import predict  # real models

app = FastAPI(title="Predictive Execution API")

# Allow dashboard → backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# GLOBAL STATE / HISTORY
# ---------------------------------------------------------
STATE = {
    "regime": "NORMAL",
    "risk": 0.1,
    "slippage": 0,
    "impact": 0,
    "latency": 1,
    "sync": 0,
    "fill_quality": 1,
}

DECISION = {
    "autonomous": "ON",
    "final_mode": "OK",
    "arbitration": [
        {
            "finalMode": "OK",
            "reason": "Model arbitration",
            "arbitrationNotes": {},
        }
    ],
}

FEDERATION = {
    "outputs": ["RiskBrain", "ImpactBrain"],
    "federation": "model",
}

ARBITRATION = {
    "final_mode": "OK",
    "reason": "model",
    "arbitrationNotes": {},
}

EPISODES = []
PERFORMANCE = []
PRECEDENTS = []


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def record_episode(pred):
    episode = {
        "id": str(uuid.uuid4()),
        "symbol": "CLOUD",
        "riskScore": pred["risk"],
        "timestamp": time.time(),
        "impactBps": pred["impact"],
        "syncDriftMs": STATE["sync"],
        "autopilotMode": DECISION["autonomous"],
        "twinStatus": "ALIGNED",
        "tags": [],
    }
    EPISODES.append(episode)
    return episode


def record_performance(pred):
    sample = {
        "id": len(PERFORMANCE) + 1,
        "riskScore": pred["risk"],
        "impactBps": pred["impact"],
        "finalMode": pred["final_mode"],
        "timestamp": time.time(),
        "name": "RiskBrain",
        "slippageBps": pred["slippage"],
        "safetyTriggered": pred["final_mode"] != "OK",
    }
    PERFORMANCE.append(sample)
    return sample


def record_precedent(pred):
    precedent = {
        "timestamp": time.time(),
        "final_mode": pred["final_mode"],
        "risk": pred["risk"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "slippage": pred["slippage"],
    }
    PRECEDENTS.append(precedent)
    return precedent


# ---------------------------------------------------------
# MAIN TICK — RUN REAL MODELS + UPDATE EVERYTHING
# ---------------------------------------------------------
def run_tick():
    global STATE, DECISION, FEDERATION, ARBITRATION

    pred = predict()  # real model output

    # Update state
    STATE["risk"] = pred["risk"]
    STATE["impact"] = pred["impact"]
    STATE["latency"] = pred["latency"]
    STATE["slippage"] = pred["slippage"]

    # Update decision
    DECISION["final_mode"] = pred["final_mode"]
    DECISION["arbitration"] = [
        {
            "finalMode": pred["final_mode"],
            "reason": "Model-driven arbitration",
            "arbitrationNotes": {},
        }
    ]

    # Update federation
    FEDERATION["outputs"] = ["RiskBrain", "ImpactBrain"]
    FEDERATION["federation"] = "model"

    # Update arbitration
    ARBITRATION["final_mode"] = pred["final_mode"]
    ARBITRATION["reason"] = "model"
    ARBITRATION["arbitrationNotes"] = {}

    # Record history
    episode = record_episode(pred)
    perf = record_performance(pred)
    precedent = record_precedent(pred)

    return {
        "prediction": pred,
        "episode": episode,
        "performance": perf,
        "precedent": precedent,
    }


# ---------------------------------------------------------
# ENDPOINTS — EXACTLY WHAT YOUR DASHBOARD CALLS
# ---------------------------------------------------------
@app.get("/state")
def get_state():
    run_tick()
    return STATE


@app.get("/decision")
def get_decision():
    run_tick()
    return DECISION


@app.get("/federation")
def get_federation():
    run_tick()
    return FEDERATION


@app.get("/arbitration")
def get_arbitration():
    run_tick()
    return ARBITRATION


@app.get("/episodes")
def get_episodes():
    run_tick()
    return EPISODES[-10:]  # last 10 episodes


@app.get("/performance")
def get_performance():
    run_tick()
    return PERFORMANCE[-10:]  # last 10 samples


@app.get("/precedents")
def get_precedents():
    run_tick()
    return PRECEDENTS[-10:]  # last 10 precedents


@app.get("/predict")
def get_predict():
    return run_tick()["prediction"]
