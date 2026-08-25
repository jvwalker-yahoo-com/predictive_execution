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
# IMPORTANT: dashboard/index.html MUST exist
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

# -----------------------------
# CORE ENDPOINTS
# -----------------------------
@app.get("/state")
def get_state():
    return {
        "regime": "NORMAL",
        "risk": 0.1902,
        "slippage": 0.387,
        "impact": 2.495,
        "latency": 16,
        "sync": 0,
        "fill_quality": 1
    }

@app.get("/decision")
def get_decision():
    return {
        "autonomous": "ON",
        "final_mode": "RISK_HIGH",
        "arbitration": [
            {
                "finalMode": "RISK_HIGH",
                "reason": "Model-driven arbitration",
                "arbitrationNotes": {}
            }
        ]
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
        "final_mode": "SLIPPAGE_HIGH",
        "reason": "model",
        "arbitrationNotes": {}
    }

# -----------------------------
# MISSING ENDPOINTS (NOW ADDED)
# -----------------------------
@app.get("/episodes")
def get_episodes():
    return {
        "id": "1577b3d8-8f1f-4180-a441-768aa",
        "symbol": "CLOUD",
        "riskScore": 0.174,
        "timestamp": 1787681230.3143666,
        "impactPts": 1.804,
        "syncDriftPts": 0,
        "autopilotMode": "ON",
        "twinStatus": "ALIGNED",
        "tags": {}
    }

@app.get("/performance")
def get_performance():
    return {
        "id": 1787681230,
        "riskScore": 0.3135,
        "impactPts": 2.559,
        "final_mode": "RISK_HIGH",
        "timestamp": 1787681230.318327,
        "name": "RiskBrain",
        "slippageBPS": 0.527,
        "safetyTriggered": True
    }

@app.get("/precedents")
def get_precedents():
    return {
        "timestamp": 1787681230.3141093,
        "final_mode": "OK",
        "risk": 0.1273,
        "impact": 1.575,
        "latency": 2,
        "slippage": 0.062
    }

@app.get("/timeline")
def get_timeline():
    return {"error": "No timeline data yet"}

@app.get("/diagnostics")
def get_diagnostics():
    return {"status": "OK", "message": "Diagnostics placeholder"}

@app.get("/risk_matrix")
def get_risk_matrix():
    return {
        "risk": 0.075,
        "impact": 2.055,
        "slippage": 0.200,
        "latency": 0.000,
        "quadrants": {
            "risk_impact": "CRITICAL",
            "risk_slippage": "SAFE",
            "risk_latency": "CRITICAL"
        }
    }

@app.get("/heatmap")
def get_heatmap():
    return {"error": "No heatmap data yet"}

@app.get("/safety_triggers")
def get_safety_triggers():
    return {"error": "No safety triggers yet"}
