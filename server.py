# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

from fastapi import FastAPI
import random
import time

app = FastAPI()

# ---------------------------------------------------------
# CORE STATE ENDPOINTS
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/state")
def state():
    return {
        "regime": "NORMAL",
        "risk": round(random.random(), 4),
        "impact": round(random.random(), 4),
        "slippage": round(random.random(), 4),
        "latency": round(random.uniform(1, 5), 4),
        "events": round(random.uniform(0, 2), 4),
        "fill_quality": 1
    }

@app.get("/decision")
def decision():
    mode = random.choice(["OK", "WARN", "SLIPPAGE_HIGH", "IMPACT_HIGH"])
    return {
        "autonomous": "ON",
        "main_mode": mode,
        "arbitrationId": "",
        "finalMode": mode,
        "reason": "Model-driven arbitration",
        "arbitrationNotes": {}
    }

# ---------------------------------------------------------
# FEDERATION SUMMARY (NOW DYNAMIC)
# ---------------------------------------------------------

@app.get("/federation")
def federation():
    return {
        "outputs": [
            random.choice(["riskSignal", "impactSignal", "latencySignal"]),
            random.choice(["riskModel", "impactModel", "slippageModel"])
        ],
        "federation": random.choice(["model1", "model2", "model3"])
    }

# ---------------------------------------------------------
# ARBITRATION
# ---------------------------------------------------------

@app.get("/arbitration")
def arbitration():
    mode = random.choice(["OK", "WARN", "CRITICAL"])
    return {
        "final_mode": mode,
        "reason": random.choice(["model1", "model2", "model3"]),
        "arbitrationNotes": {}
    }

# ---------------------------------------------------------
# VISUALIZER ENDPOINTS
# ---------------------------------------------------------

@app.get("/bubble_chart")
def bubble_chart():
    return [{
        "risk": round(random.random(), 3),
        "impact": round(random.random(), 3),
        "size": random.randint(10, 40)
    }]

@app.get("/heatmap")
def heatmap():
    matrix = [[round(random.random(), 3) for _ in range(3)] for _ in range(4)]
    return {"matrix": matrix}

@app.get("/timeline")
def timeline():
    modes = ["OK", "WARN", "CRITICAL"]
    return [{"mode": random.choice(modes)} for _ in range(12)]

@app.get("/safety_triggers")
def safety_triggers():
    return {
        "risk": {"triggered": random.random() > 0.85},
        "impact": {"triggered": random.random() > 0.85},
        "slippage": {"triggered": random.random() > 0.85},
        "latency": {"triggered": random.random() > 0.85}
    }

# ---------------------------------------------------------
# COCKPIT ENDPOINTS
# ---------------------------------------------------------

@app.get("/anomaly_detector")
def anomaly_detector():
    return {
        "risk_spike": random.random() > 0.8,
        "latency_spike": random.random() > 0.85,
        "impact_jump": random.random() > 0.9,
        "slippage_jump": random.random() > 0.9
    }

@app.get("/node_events")
def node_events():
    return {
        "events": [
            {"mode": "OK", "timestamp": time.time()},
            {"mode": "WARN", "timestamp": time.time() - 5},
            {"mode": "CRITICAL", "timestamp": time.time() - 10}
        ]
    }

@app.get("/quadrant")
def quadrant():
    return {
        "risk": round(random.random(), 3),
        "impact": round(random.random(), 3),
        "quadrant": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    }

@app.get("/heartbeat")
def heartbeat():
    return {
        "alive": True,
        "timestamp": time.time()
    }

@app.get("/sync_drift")
def sync_drift():
    return {
        "drift_ms": random.randint(0, 250),
        "status": "OK" if random.random() < 0.8 else "DRIFTING"
    }
