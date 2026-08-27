# =========================================================
# Predictive Execution API — Full System (Federation + Modes + History)
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def rand():
    return round(random.uniform(0.0, 1.0), 4)

@app.get("/state")
def state():
    return {
        "regime": "NORMAL",
        "risk": rand(),
        "slippage": rand(),
        "impact": rand() * 2,
        "latency": rand() * 20,
        "sync": rand() * 5,
        "fill_quality": 1
    }

@app.get("/decision")
def decision():
    return {
        "autonomous": "ON",
        "final_mode": random.choice(["IMPACT_HIGH", "RISK_HIGH", "NORMAL"]),
        "arbitration": {
            "finalMode": random.choice(["IMPACT_HIGH", "RISK_HIGH", "NORMAL"]),
            "reason": "Model-driven arbitration",
            "arbitrationNotes": {}
        }
    }

@app.get("/federation")
def federation():
    return {
        "outputs": ["RiskBrain", "ImpactBrain"],
        "federation": "model"
    }

@app.get("/arbitration")
def arbitration():
    return {
        "final_mode": random.choice(["RISK_HIGH", "IMPACT_HIGH", "NORMAL"]),
        "reason": "model",
        "arbitrationNotes": {}
    }

@app.get("/bubble_chart")
def bubble():
    return [{
        "risk": rand(),
        "impact": rand(),
        "size": random.randint(10, 40)
    }]

@app.get("/heatmap")
def heatmap():
    return {
        "matrix": [
            [rand(), rand(), rand(), rand()],
            [rand(), rand(), rand(), rand()],
            [rand(), rand(), rand(), rand()]
        ]
    }

@app.get("/timeline")
def timeline():
    return [{"mode": random.choice(["OK", "WARN", "FAIL"])} for _ in range(20)]

@app.get("/safety_triggers")
def safety():
    return {
        "risk": {"triggered": rand() > 0.85},
        "impact": {"triggered": rand() > 0.85},
        "slippage": {"triggered": rand() > 0.85},
        "latency": {"triggered": rand() > 0.85}
    }

# -----------------------------
# NEW FUNCTIONALITY
# -----------------------------

@app.get("/anomaly_detector")
def anomaly_detector():
    return {
        "risk_spike": rand() > 0.92,
        "latency_spike": rand() > 0.90,
        "impact_jump": rand() > 0.88,
        "slippage_jump": rand() > 0.87
    }

@app.get("/mode_events")
def mode_events():
    return [
        {"event": random.choice(["MODE_SWITCH", "FAILSAFE", "REVERT", "NORMALIZE"]),
         "value": random.choice(["RISK_HIGH", "IMPACT_HIGH", "NORMAL"])}
        for _ in range(10)
    ]

@app.get("/quadrant")
def quadrant():
    r = rand()
    i = rand()
    return {
        "risk": r,
        "impact": i,
        "quadrant": (
            "HIGH-HIGH" if r > 0.5 and i > 0.5 else
            "HIGH-LOW" if r > 0.5 else
            "LOW-HIGH" if i > 0.5 else
            "LOW-LOW"
        )
    }

@app.get("/heartbeat")
def heartbeat():
    return {"alive": random.choice([True, True, True, False])}

@app.get("/sync_drift")
def sync_drift():
    return {"drift": round(random.uniform(-2.0, 2.0), 3)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
