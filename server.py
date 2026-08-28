# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import time
import math

app = FastAPI()

# -----------------------------
# CORS (REQUIRED FOR DASHBOARD)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# INTERNAL MODEL SIMULATION
# -----------------------------

def model_risk():
    base = 0.35 + math.sin(time.time() / 8) * 0.25
    noise = random.uniform(-0.05, 0.05)
    return round(max(0, min(1, base + noise)), 4)

def model_impact():
    base = 0.40 + math.cos(time.time() / 10) * 0.20
    noise = random.uniform(-0.04, 0.04)
    return round(max(0, min(1, base + noise)), 4)

def model_slippage():
    base = 0.30 + math.sin(time.time() / 6) * 0.30
    noise = random.uniform(-0.03, 0.03)
    return round(max(0, min(1, base + noise)), 4)

def model_latency():
    base = 12 + math.sin(time.time() / 4) * 6
    noise = random.uniform(-1.5, 1.5)
    return round(max(1, base + noise), 3)

def model_mode(risk, impact, slippage):
    score = (risk + impact + slippage) / 3
    if score < 0.33:
        return "OK"
    elif score < 0.66:
        return "WARN"
    else:
        return "CRITICAL"

def model_federation():
    return {
        "outputs": [
            f"risk:{model_risk()}",
            f"impact:{model_impact()}",
            f"slippage:{model_slippage()}"
        ],
        "federation": random.choice(["model1", "model2", "model3"])
    }

# -----------------------------
# ENDPOINTS
# -----------------------------

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/state")
def state():
    return {
        "regime": "NORMAL",
        "risk": model_risk(),
        "impact": model_impact(),
        "slippage": model_slippage(),
        "latency": model_latency(),
        "events": round(random.uniform(0, 2), 4),
        "fill_quality": 1
    }

@app.get("/decision")
def decision():
    risk = model_risk()
    impact = model_impact()
    slippage = model_slippage()
    mode = model_mode(risk, impact, slippage)

    return {
        "autonomous": "ON",
        "main_mode": mode,
        "finalMode": mode,
        "reason": "Model arbitration",
        "arbitrationNotes": {}
    }

@app.get("/federation")
def federation():
    return model_federation()

@app.get("/arbitration")
def arbitration():
    risk = model_risk()
    impact = model_impact()
    slippage = model_slippage()
    mode = model_mode(risk, impact, slippage)

    return {
        "final_mode": mode,
        "reason": "model arbitration",
        "arbitrationNotes": {}
    }

@app.get("/anomaly_detector")
def anomaly_detector():
    return {
        "risk_spike": model_risk() > 0.85,
        "latency_spike": model_latency() > 20,
        "impact_jump": model_impact() > 0.85,
        "slippage_jump": model_slippage() > 0.85
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
    risk = model_risk()
    impact = model_impact()

    if risk < 0.33 and impact < 0.33:
        q = "LOW"
    elif risk < 0.66 and impact < 0.66:
        q = "MEDIUM"
    elif risk < 0.66 and impact >= 0.66:
        q = "HIGH"
    else:
        q = "CRITICAL"

    return {
        "risk": risk,
        "impact": impact,
        "quadrant": q
    }

@app.get("/heartbeat")
def heartbeat():
    return {"alive": True, "timestamp": time.time()}

@app.get("/sync_drift")
def sync_drift():
    drift = random.randint(0, 250)
    return {"drift_ms": drift, "status": "OK" if drift < 120 else "DRIFTING"}
