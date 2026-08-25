# =========================================================
# Simple Static Dashboard Server
# =========================================================
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time

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
# Make sure your dashboard files are in /static:
# static/index.html
# static/dashboard.js
# static/styles.css
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# -----------------------------
# MOCK DATA STORAGE
# (Replace with your real engine)
# -----------------------------
STATE = {"mode": "LIVE", "timestamp": time.time()}
DECISION = {"action": "BUY", "confidence": 0.82}
FEDERATION = {
    "federation": {"mode": "LIVE", "confidence": 0.88},
    "outputs": [
        {
            "name": "BrainA",
            "mode": "LIVE",
            "confidence": 80,
            "riskScore": 0.22,
            "impactBps": 0.4,
            "slippageBps": 0.1,
            "diagnostics": ["stable", "low-risk"]
        },
        {
            "name": "BrainB",
            "mode": "SHADOW",
            "confidence": 55,
            "riskScore": 0.31,
            "impactBps": 0.6,
            "slippageBps": 0.2,
            "diagnostics": ["medium-risk"]
        }
    ]
}

ARBITRATION = {"winner": "BrainA", "reason": "higher confidence"}

EPISODES = [{"id": 1, "brain": "BrainA", "reward": 0.12}]
PERFORMANCE = {"samples": [{"brain": "BrainA", "reward": 0.12}]}
PRECEDENTS = [{"case": "risk-high", "result": "HALT"}]

MODE_HISTORY = [
    {
        "timestamp": time.time() - 60,
        "mode": "LIVE",
        "reasons": ["stable"],
        "confidence": 0.88,
        "risk": 0.22,
        "impact": 0.4,
        "latency": 120,
        "slippage": 0.1
    },
    {
        "timestamp": time.time() - 30,
        "mode": "SHADOW",
        "reasons": ["risk rising"],
        "confidence": 0.55,
        "risk": 0.31,
        "impact": 0.6,
        "latency": 240,
        "slippage": 0.2
    }
]

# -----------------------------
# ENDPOINTS USED BY COCKPIT
# -----------------------------

@app.get("/state")
def get_state():
    return STATE

@app.get("/decision")
def get_decision():
    return DECISION

@app.get("/federation")
def get_federation():
    return FEDERATION

@app.get("/arbitration")
def get_arbitration():
    return ARBITRATION

@app.get("/episodes")
def get_episodes():
    return EPISODES

@app.get("/performance")
def get_performance():
    return PERFORMANCE

@app.get("/precedents")
def get_precedents():
    return PRECEDENTS

@app.get("/mode_history")
def get_mode_history():
    return MODE_HISTORY

@app.get("/predict")
def get_predict():
    # Simulated live tick
    return {
        "risk": 0.22,
        "impact": 0.4,
        "slippage": 0.1,
        "latency": 120
    }

# -----------------------------
# RUN LOCAL SERVER
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

