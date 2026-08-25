# =========================================================
# Simple Static Dashboard Server
# =========================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# -----------------------------
# CORS
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
        "risk": 0.1184,
        "slippage": 0.267,
        "impact": 2.338,
        "latency": 3,
        "sync": 0,
        "fill_quality": 1
    }

@app.get("/decision")
def get_decision():
    return {
        "autonomous": "ON",
        "final_mode": "IMPACT_HIGH",
        "arbitration": {
            "FinalMode": "IMPACT_HIGH",
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
        "final_mode": "OK",
        "reason": "model",
        "arbitrationNotes": {}
    }

# -----------------------------
# LIST-BASED PANELS (FIXED)
# -----------------------------
@app.get("/episodes")
def get_episodes():
    return [
        {
            "id": "39bb1478-494b-4c23-b058-a962b",
            "symbol": "CLOUD",
            "riskScore": 0.192,
            "timestamp": 1787682135.3995852,
            "impactBps": 2.209,
            "syncDriftPs": 0,
            "agencyMode": "ON",
            "twinStatus": "ALIGNED",
            "tags": []
        }
    ]

@app.get("/performance")
def get_performance():
    return [
        {
            "id": 1787682135,
            "riskScore": 0.2547,
            "impactBps": 1.0399,
            "finalMode": "OK",
            "timestamp": 1787682135.3981843,
            "name": "RiskBrain",
            "slippageBps": 1.2,
            "safetyTriggered": False
        }
    ]

@app.get("/precedents")
def get_precedents():
    return [
        {
            "timestamp": 1787682135.398245,
            "final_mode": "OK",
            "risk": 0.1098,
            "impact": 0.123,
            "latency": 22,
            "slippage": 0.756
        }
    ]

# -----------------------------
# REMAINING PANELS
# -----------------------------
@app.get("/timeline")
def get_timeline():
    return {"error": "Connection failed"}

@app.get("/diagnostics")
def get_diagnostics():
    return {"error": "Connection failed"}

@app.get("/safety_triggers")
def get_safety_triggers():
    return {"error": "Connection failed"}

@app.get("/heatmap")
def get_heatmap():
    return {"error": "Connection failed"}

@app.get("/bubble_chart")
def get_bubble_chart():
    return {"error": "Connection failed"}

@app.get("/visualizer")
def get_visualizer():
    return {"error": "Connection failed"}

@app.get("/risk_matrix")
def get_risk_matrix():
    return {
        "risk": 0.091,
        "impact": 0.176,
        "slippage": 0.983,
        "latency": 7.0,
        "quadrants": {
            "risk_impact": "CRITICAL",
            "risk_slippage": "CRITICAL",
            "risk_latency": "CRITICAL"
        }
    }
