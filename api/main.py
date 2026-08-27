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

def r(): return round(random.uniform(0, 1), 4)

@app.get("/state")
def state():
    return {
        "regime": "NORMAL",
        "risk": r(),
        "slippage": r(),
        "impact": r() * 2,
        "latency": r() * 20,
        "sync": r() * 5,
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
        "risk": r(),
        "impact": r(),
        "size": random.randint(10, 40)
    }]

@app.get("/heatmap")
def heatmap():
    return {
        "matrix": [
            [r(), r(), r(), r()],
            [r(), r(), r(), r()],
            [r(), r(), r(), r()]
        ]
    }

@app.get("/timeline")
def timeline():
    return [{"mode": random.choice(["OK", "WARN", "FAIL"])} for _ in range(20)]

@app.get("/safety_triggers")
def safety():
    return {
        "risk": {"triggered": r() > 0.85},
        "impact": {"triggered": r() > 0.85},
        "slippage": {"triggered": r() > 0.85},
        "latency": {"triggered": r() > 0.85}
    }

# -----------------------------
# NEW FUNCTIONALITY
# -----------------------------

@app.get("/anomaly_detector")
def anomaly_detector():
    return {
        "risk_spike": r() > 0.92,
        "latency_spike": r() > 0.90,
        "impact_jump": r() > 0.88,
        "slippage_jump": r() > 0.87
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
    risk = r()
    impact = r()
    return {
        "risk": risk,
        "impact": impact,
        "quadrant": (
            "HIGH-HIGH" if risk > 0.5 and impact > 0.5 else
            "HIGH-LOW" if risk > 0.5 else
            "LOW-HIGH" if impact > 0.5 else
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
