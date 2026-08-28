# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

# =========================================================
# Predictive Execution – Full FastAPI Server (Validated)
# =========================================================

# server.py
from fastapi import FastAPI
import random
import time
import math

app = FastAPI()

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
# CORE STATE ENDPOINTS
# -----------------------------

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/state")
def state():
    risk = model_risk()
    impact = model_impact()
    slippage = model_slippage()
    latency = model_latency()

    return {
        "regime": "NORMAL",
        "risk": risk,
        "impact": impact,
        "slippage": slippage,
        "latency": latency,
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
        "automation": "ON",
        "auto_mode": mode,
        "manual_mode": mode,
        "reason": "Mode-driven arbitration",
        "arbitrationNotes": []
    }

# -----------------------------
# FEDERATION / ARBITRATION
# -----------------------------

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
        "signal_mode": mode,
        "reason": "model3",
        "arbitrationNotes": []
    }

# -----------------------------
# VISUALIZER ENDPOINTS
# -----------------------------

@app.get("/bubble_chart")
def bubble_chart():
    return [{
        "risk": model_risk(),
        "impact": model_impact(),
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
        "risk": {"triggered": model_risk() > 0.75},
        "impact": {"triggered": model_impact() > 0.75},
        "slippage": {"triggered": model_slippage() > 0.75},
        "latency": {"triggered": model_latency() > 18}
    }

# -----------------------------
# COCKPIT ENDPOINTS
# -----------------------------

@app.get("/anomaly_detector")
def anomaly_detector():
    return {
        "risk_spike": model_risk() > 0.85,
        "impact_spike": model_impact() > 0.85,
        "latency_spike": model_latency() > 20,
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
    return {
        "alive": True,
        "timestamp": time.time()
    }

@app.get("/sync_drift")
def sync_drift():
    drift = random.randint(0, 250)
    return {
        "drift_ms": drift,
        "status": "OK" if drift < 120 else "DRIFTING"
    }
