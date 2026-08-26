// paste dashboard JS here
// Predictive Execution Dashboard — Updated Full File
// Works with Render backend and real-model API
// Predictive Execution Dashboard — Correct Version
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()

# ------------------------------
# CORE DATA GENERATORS
# ------------------------------

def get_state():
    return {
        "mode": random.choice(["IDLE", "ACTIVE", "LEARNING"]),
        "confidence": round(random.uniform(0.1, 0.99), 4),
        "latency": round(random.uniform(0.1, 5.0), 4)
    }

def get_decision():
    return {
        "action": random.choice(["BUY", "SELL", "HOLD"]),
        "strength": round(random.uniform(0.1, 1.0), 4)
    }

def get_episodes():
    return [{"episode": i, "reward": round(random.uniform(-1, 1), 4)} for i in range(10)]

def get_performance():
    return [{"step": i, "value": round(random.uniform(0, 1), 4)} for i in range(20)]

def get_federation():
    return {
        "nodes": 5,
        "active": random.randint(1, 5),
        "health": round(random.uniform(0.1, 1.0), 4)
    }

def get_arbitration():
    return {
        "conflicts": random.randint(0, 5),
        "resolved": random.randint(0, 5)
    }

def get_precedents():
    return [{"case": i, "result": random.choice(["PASS", "FAIL"])} for i in range(5)]

def get_timeline():
    return [{"t": i, "mode": random.choice(["IDLE", "ACTIVE", "LEARNING"])} for i in range(15)]

def get_visualizer():
    return {"graph": "federation_visualizer", "nodes": random.randint(3, 10)}

def get_diagnostics():
    return {"cpu": random.randint(1, 100), "ram": random.randint(1, 100)}

def get_heatmap():
    return {"heatmap": [[round(random.uniform(0, 1), 3) for _ in range(5)] for _ in range(5)]}

def get_bubble_chart():
    return [{"risk": round(random.uniform(0, 1), 3), "impact": round(random.uniform(0, 1), 3)} for _ in range(10)]

def get_safety_triggers():
    return {"triggers": random.randint(0, 3)}

def get_latency_spikes():
    return [{"t": i, "latency": round(random.uniform(0.1, 5.0), 3)} for i in range(20)]

def get_slippage_anomalies():
    return [{"t": i, "slippage": round(random.uniform(0, 1), 3)} for i in range(20)]

# ------------------------------
# API ENDPOINTS
# ------------------------------

@app.get("/state")
def api_state():
    return get_state()

@app.get("/decision")
def api_decision():
    return get_decision()

@app.get("/episodes")
def api_episodes():
    return get_episodes()

@app.get("/performance")
def api_performance():
    return get_performance()

@app.get("/federation")
def api_federation():
    return get_federation()

@app.get("/arbitration")
def api_arbitration():
    return get_arbitration()

@app.get("/precedents")
def api_precedents():
    return get_precedents()

@app.get("/timeline")
def api_timeline():
    return get_timeline()

# ------------------------------
# ALIAS ENDPOINTS (Dashboard compatibility)
# ------------------------------

@app.get("/mode_history")
def alias_mode_history():
    return get_timeline()

@app.get("/predict")
def alias_predict():
    return get_decision()

@app.get("/federation_visualizer")
def alias_federation_visualizer():
    return get_visualizer()

@app.get("/brain_diagnostics")
def alias_brain_diagnostics():
    return get_diagnostics()

@app.get("/confidence_heatmap")
def alias_confidence_heatmap():
    return get_heatmap()

@app.get("/risk_bubbles")
def alias_risk_bubbles():
    return get_bubble_chart()

@app.get("/safety")
def alias_safety():
    return get_safety_triggers()

@app.get("/latency_spikes")
def alias_latency_spikes():
    return get_latency_spikes()

@app.get("/slippage_anomalies")
def alias_slippage_anomalies():
    return get_slippage_anomalies()

# ------------------------------
# DASHBOARD STATIC FILES
# ------------------------------

app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
