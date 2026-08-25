# paste federation logic here
# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

from engine.predict import predict
from engine.federation import federation_engine

app = FastAPI(title="Predictive Execution API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def generate_arbitration(federation):
    return {
        "final_mode": federation["mode"],
        "reason": "; ".join(federation["reasons"]),
        "arbitrationNotes": {
            "confidence": federation["confidence"],
            "votes": federation["votes"],
        },
    }


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


def generate_precedent(pred, federation):
    return {
        "timestamp": time.time(),
        "final_mode": federation["mode"],
        "risk": pred["risk"],
        "impact": pred["impact"],
        "latency": pred["latency"],
        "slippage": pred["slippage"],
    }


def run_tick():
    raw = predict() or {}

    pred = {
        "risk": raw.get("risk", 0.1),
        "impact": raw.get("impact", 0),
        "latency": raw.get("latency", 1),
        "slippage": raw.get("slippage", 0),
        "final_mode": raw.get("final_mode", "OK"),
    }

    state = generate_state(pred)
    federation = federation_engine["evaluate"](state)

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
