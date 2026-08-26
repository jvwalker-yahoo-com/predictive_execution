# =========================================================
# Simple Static Dashboard Server
# =========================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import random
import time

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
# INTERNAL LIVE ENGINES
# -----------------------------

def risk_brain():
    score = round(random.uniform(0.1, 0.4), 4)
    return {
        "score": score,
        "confidence": round(random.uniform(0.7, 0.95), 4),
        "trend": [round(random.uniform(0.1, 0.4), 4) for _ in range(3)]
    }

def impact_brain():
    impact = round(random.uniform(0.1, 2.5), 4)
    return {
        "impact": impact,
        "confidence": round(random.uniform(0.6, 0.9), 4),
        "trend": [round(random.uniform(0.1, 2.5), 4) for _ in range(3)]
    }

def slippage_brain():
    slippage = round(random.uniform(0.1, 1.5), 4)
    return {
        "slippage": slippage,
        "confidence": round(random.uniform(0.5, 0.85), 4),
        "trend": [round(random.uniform(0.1, 1.5), 4) for _ in range(3)]
    }

def latency_brain():
    latency = round(random.uniform(1, 30), 4)
    return {
        "latency": latency,
        "confidence": round(random.uniform(0.8, 0.99), 4),
        "trend": [round(random.uniform(1, 30), 4) for _ in range(3)]
    }

def diagnostics_engine():
    return {
        "RiskBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": time.time()},
        "ImpactBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": time.time()},
        "SlippageBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": time.time()},
        "LatencyBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": time.time()}
    }

mode_history = []

def mode_switch_engine(mode):
    mode_history.append({"timestamp": time.time(), "mode": mode})
    if len(mode_history) > 20:
        mode_history.pop(0)

def safety_engine(risk, impact, slippage, latency):
    return {
        "risk": {"triggered": risk > 0.25, "value": risk},
        "impact": {"triggered": impact > 1.5, "value": impact},
        "slippage": {"triggered": slippage > 1.0, "value": slippage},
        "latency": {"triggered": latency > 15, "value": latency}
    }

def bubble_chart_engine(risk, impact, slippage, latency):
    return [
        {
            "risk": risk,
            "impact": impact,
            "slippage": slippage,
            "latency": latency,
            "size": round((risk + impact + slippage) * 4, 2),
            "color": "red" if slippage > 1.0 else "orange"
        }
    ]

def heatmap_engine():
    return {
        "matrix": [
            [round(random.uniform(0.7, 0.95), 4) for _ in range(4)]
            for _ in range(3)
        ],
        "labels": ["RiskBrain", "ImpactBrain", "SlippageBrain", "LatencyBrain"]
    }

# -----------------------------
# LIVE ENDPOINTS
# -----------------------------

@app.get("/state")
def get_state():
    risk = round(random.uniform(0.1, 0.4), 4)
    slippage = round(random.uniform(0.1, 1.5), 4)
    impact = round(random.uniform(0.1, 2.5), 4)
    latency = round(random.uniform(1, 30), 4)

    return {
        "regime": "NORMAL",
        "risk": risk,
        "slippage": slippage,
        "impact": impact,
        "latency": latency,
        "sync": 0,
        "fill_quality": 1
    }

@app.get("/decision")
def get_decision():
    modes = ["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]
    mode = random.choice(modes)
    mode_switch_engine(mode)

    return {
        "autonomous": "ON",
        "final_mode": mode,
        "arbitration": [
            {
                "finalMode": mode,
                "reason": "Model-driven arbitration",
                "arbitrationNotes": {}
            }
        ]
    }

@app.get("/federation")
def get_federation():
    return {
        "outputs": ["RiskBrain", "ImpactBrain"],
        "federation": "model1"
    }

@app.get("/arbitration")
def get_arbitration():
    modes = ["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]
    mode = random.choice(modes)
    return {
        "final_mode": mode,
        "reason": "model",
        "arbitrationNotes": {}
    }

@app.get("/visualizer")
def get_visualizer():
    return {
        "RiskBrain": risk_brain(),
        "ImpactBrain": impact_brain(),
        "SlippageBrain": slippage_brain(),
        "LatencyBrain": latency_brain()
    }

@app.get("/diagnostics")
def get_diagnostics():
    return diagnostics_engine()

@app.get("/timeline")
def get_timeline():
    return mode_history

@app.get("/safety_triggers")
def get_safety_triggers():
    risk = round(random.uniform(0.1, 0.4), 4)
    impact = round(random.uniform(0.1, 2.5), 4)
    slippage = round(random.uniform(0.1, 1.5), 4)
    latency = round(random.uniform(1, 30), 4)
    return safety_engine(risk, impact, slippage, latency)

@app.get("/bubble_chart")
def get_bubble_chart():
    risk = round(random.uniform(0.1, 0.4), 4)
    impact = round(random.uniform(0.1, 2.5), 4)
    slippage = round(random.uniform(0.1, 1.5), 4)
    latency = round(random.uniform(1, 30), 4)
    return bubble_chart_engine(risk, impact, slippage, latency)

@app.get("/heatmap")
def get_heatmap():
    return heatmap_engine()

@app.get("/episodes")
def get_episodes():
    return [
        {
            "id": "192a67d0-bf74-4752-8427-bf1a6",
            "symbol": "CLOUD",
            "riskScore": round(random.uniform(0.1, 0.3), 4),
            "timestamp": time.time(),
            "impactBps": round(random.uniform(0.5, 2.5), 4),
            "syncDriftMs": 0,
            "autopilotMode": "ON",
            "latStatus": "ALIGNED",
            "tags": []
        }
    ]

@app.get("/performance")
def get_performance():
    return [
        {
            "id": int(time.time()),
            "riskScore": round(random.uniform(0.1, 0.3), 4),
            "impactBps": round(random.uniform(0.1, 2.0), 4),
            "finalMode": random.choice(["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]),
            "timestamp": time.time(),
            "engine": "RiskBrain",
            "slippageBps": round(random.uniform(0.1, 1.5), 4),
            "safetyTriggered": random.choice([True, False])
        }
    ]

@app.get("/precedents")
def get_precedents():
    return [
        {
            "timestamp": time.time(),
            "final_mode": random.choice(["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]),
            "risk": round(random.uniform(0.1, 0.4), 4),
            "impact": round(random.uniform(0.1, 2.5), 4),
            "latency": round(random.uniform(1, 30), 4),
            "slippage": round(random.uniform(0.1, 1.5), 4)
        }
    ]

@app.get("/risk_matrix")
def get_risk_matrix():
    risk = round(random.uniform(0.1, 0.4), 4)
    impact = round(random.uniform(0.1, 2.5), 4)
    slippage = round(random.uniform(0.1, 1.5), 4)
    latency = round(random.uniform(1, 30), 4)

    return {
        "risk": risk,
        "impact": impact,
        "slippage": slippage,
        "latency": latency,
        "quadrants": {
            "risk_impact": "CRITICAL" if risk * impact > 0.3 else "SAFE",
            "risk_slippage": "CRITICAL" if risk * slippage > 0.3 else "SAFE",
            "risk_latency": "CRITICAL" if risk * latency > 5 else "SAFE"
        }
    }
