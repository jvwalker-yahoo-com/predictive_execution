# =========================================================
# Simple Static Dashboard Server
# =========================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# -----------------------------
# CORS (dashboard → API)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# STATIC DASHBOARD
# -----------------------------
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

# -----------------------------
# CORE ENDPOINTS
# -----------------------------
@app.get("/state")
def get_state():
    return {
        "regime": "NORMAL",
        "risk": 0.2002,
        "slippage": 1.885,
        "impact": 1.173,
        "latency": 14,
        "sync": 0,
        "fill_quality": 1
    }

@app.get("/decision")
def get_decision():
    return {
        "autonomous": "ON",
        "final_mode": "RISK_HIGH",
        "arbitration": {
            "finalMode": "RISK_HIGH",
            "reason": "Model-driven arbitration",
            "arbitrationNotes": {}
        }
    }

@app.get("/federation")
def get_federation():
    return {
        "outputs": ["RiskBrain", "ImpactBrain"],
        "federation": "model"
    }

@app.get("/arbitration")
def get_arbitration():
    return {
        "final_mode": "RISK_HIGH",
        "reason": "model",
        "arbitrationNotes": {}
    }

# -----------------------------
# MISSING ENDPOINTS (NOW ADDED)
# -----------------------------
@app.get("/episodes")
def get_episodes():
    return {
        "id": "87af4fcb-9f72-49de-b452-fc468",
        "symbol": "CLOUD",
        "riskScore": 0.1325,
        "impactDps": 2.715,
        "timestamp": 1787681855.3482394,
        "syncDriftPts": 0,
        "autopilotMode": "ON",
        "twinStatus": "ALIGNED",
        "tags": []
    }

@app.get("/performance")
def get_performance():
    return {
        "id": 1787681855,
        "riskScore": 0.2577,
        "impactDps": 2.92,
        "finalMode": "IMPACT_HIGH",
        "timestamp": 1787681855.353329,
        "name": "RiskBrain",
        "slippageDps": 0.387,
        "safetyTriggered": True
    }

@app.get("/precedents")
def get_precedents():
    return {
        "timestamp": 1787681855.3539312,
        "final_mode": "OK",
        "risk": 0.8043,
        "impact": 1.528,
        "latency": 12,
        "slippage": 0.524
    }

@app.get("/timeline")
def get_timeline():
    return {"error": "Connection failed"}

@app.get("/diagnostics")
def get_diagnostics():
    return {"error": "Connection failed"}

@app.get("/risk_matrix")
def get_risk_matrix():
    return {
        "risk": 0.138,
        "impact": 0.216,
        "slippage": 0.354,
        "latency": 16.000,
        "quadrants": {
            "risk_impact": "SAFE",
            "risk_slippage": "WATCH",
            "risk_latency": "CRITICAL"
        }
    }

@app.get("/heatmap")
def get_heatmap():
    return {"error": "Connection failed"}

@app.get("/safety_triggers")
def get_safety_triggers():
    return {"error": "Connection failed"}
