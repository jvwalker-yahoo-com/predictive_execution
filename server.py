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
    return {
        "score": round(random.uniform(0.05, 0.9), 4),
        "confidence": round(random.uniform(0.7, 0.95), 4),
        "trend": [round(random.uniform(0.05, 0.9), 4) for _ in range(3)]
    }

def impact_brain():
    return {
        "impact": round(random.uniform(0.1, 3.0), 4),
        "confidence": round(random.uniform(0.6, 0.9), 4),
        "trend": [round(random.uniform(0.1, 3.0), 4) for _ in range(3)]
    }

def slippage_brain():
    return {
        "slippage": round(random.uniform(0.05, 2.0), 4),
        "confidence": round(random.uniform(0.5, 0.85), 4),
        "trend": [round(random.uniform(0.05, 2.0), 4) for _ in range(3)]
    }

def latency_brain():
    return {
        "latency": round(random.uniform(0.1, 30), 4),
        "confidence": round(random.uniform(0.8, 0.99), 4),
        "trend": [round(random.uniform(0.1, 30), 4) for _ in range(3)]
    }

def diagnostics_engine():
    now = time.time()
    return {
        "RiskBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": now},
        "ImpactBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": now},
        "SlippageBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": now},
        "LatencyBrain": {"status": "OK", "drift": round(random.uniform(0.0, 0.05), 4), "lastUpdate": now}
    }

mode_history = []

def mode_switch_engine(mode: str):
    mode_history.append({"timestamp": time.time(), "mode": mode})
    if len(mode_history) > 50:
        mode_history.pop(0)

def safety_engine(risk, impact, slippage, latency):
    return {
        "risk": {"triggered": random.choice([True, False]), "value": risk},
        "impact": {"triggered": random.choice([True, False]), "value": impact},
        "slippage": {"triggered": random.choice([True, False]), "value": slippage},
        "latency": {"triggered": random.choice([True, False]), "value": latency}
    }

def bubble_chart_engine(risk, impact, slippage, latency):
    return [
        {
            "risk": risk,
            "impact": impact,
            "slippage": slippage,
            "latency": latency,
            "size": round((risk + impact + slippage) * 4, 2),
            "color": random.choice(["red", "orange", "yellow"])
        }
    ]

def heatmap_engine():
    return {
        "matrix": [
            [round(random.uniform(0.5, 0.99), 4) for _ in range(4)]
            for _ in range(3)
        ],
        "labels": ["RiskBrain", "ImpactBrain", "SlippageBrain", "LatencyBrain"]
    }

def latency_spike_engine():
    return {
        "spikes": [
            {
                "timestamp": time.time(),
                "latency": round(random.uniform(10, 40), 4),
                "severity": random.choice(["LOW", "MEDIUM", "HIGH"])
            }
        ]
    }

def slippage_anomaly_engine():
    return {
        "anomalies": [
            {
                "timestamp": time.time(),
                "slippage": round(random.uniform(1.0, 3.0), 4),
                "type": random.choice(["SPIKE", "DROP", "VOLATILITY_SURGE"])
            }
        ]
    }

# -----------------------------
# LIVE ENDPOINTS
# -----------------------------

@app.get("/state")
def get_state():
    return {
        "regime": "NORMAL",
        "risk": round(random.uniform(0.05, 0.9), 4),
        "slippage": round(random.uniform(0.05, 2.0), 4),
        "impact": round(random.uniform(0.1, 3.0), 4),
        "latency": round(random.uniform(0.1, 30), 4),
        "sync": round(random.uniform(0, 10), 4),
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
        "arbitration": {
            "finalMode": mode,
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
    mode = random.choice(["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"])
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
    return safety_engine(
        round(random.uniform(0.05, 0.9), 4),
        round(random.uniform(0.1, 3.0), 4),
        round(random.uniform(0.05, 2.0), 4),
        round(random.uniform(0.1, 30), 4)
    )

@app.get("/bubble_chart")
def get_bubble_chart():
    return bubble_chart_engine(
        round(random.uniform(0.05, 0.9), 4),
        round(random.uniform(0.1, 3.0), 4),
        round(random.uniform(0.05, 2.0), 4),
        round(random.uniform(0.1, 30), 4)
    )

@app.get("/heatmap")
def get_heatmap():
    return heatmap_engine()

@app.get("/latency_spikes")
def get_latency_spikes():
    return latency_spike_engine()

@app.get("/slippage_anomalies")
def get_slippage_anomalies():
    return slippage_anomaly_engine()

@app.get("/episodes")
def get_episodes():
    return [
        {
            "id": str(random.randint(10000, 99999)),
            "symbol": "CLOUD",
            "riskScore": round(random.uniform(0.05, 0.9), 4),
            "timestamp": time.time(),
            "impactBps": round(random.uniform(0.1, 3.0), 4),
            "syncDriftPs": round(random.uniform(0, 10), 4),
            "autoPilotMode": "ON",
            "twinStatus": "ALIGNED",
            "tags": []
        }
    ]

@app.get("/performance")
def get_performance():
    return [
        {
            "id": int(time.time()),
            "riskScore": round(random.uniform(0.05, 0.9), 4),
            "impactBps": round(random.uniform(0.1, 3.0), 4),
            "finalMode": random.choice(["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]),
            "timestamp": time.time(),
            "name": "RiskBrain",
            "slippageBps": round(random.uniform(0.05, 2.0), 4),
            "safetyTriggered": random.choice([True, False])
        }
    ]

@app.get("/precedents")
def get_precedents():
    return [
        {
            "timestamp": time.time(),
            "final_mode": random.choice(["OK", "RISK_HIGH", "IMPACT_HIGH", "SLIPPAGE_HIGH"]),
            "risk": round(random.uniform(0.05, 0.9), 4),
            "impact": round(random.uniform(0.1, 3.0), 4),
            "latency": round(random.uniform(0.1, 30), 4),
            "slippage": round(random.uniform(0.05, 2.0), 4)
        }
    ]

@app.get("/risk_matrix")
def get_risk_matrix():
    risk = round(random.uniform(0.05, 0.9), 4)
    impact = round(random.uniform(0.1, 3.0), 4)
    slippage = round(random.uniform(0.05, 2.0), 4)
    latency = round(random.uniform(0.1, 30), 4)

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

# -----------------------------
# ALIAS ENDPOINTS (Dashboard compatibility)
# -----------------------------

@app.get("/federation_visualizer")
def alias_federation_visualizer():
    return get_visualizer()

@app.get("/brain_diagnostics")
def alias_brain_diagnostics():
    return get_diagnostics()

@app.get("/mode_timeline")
def alias_mode_timeline():
    return get_timeline()

@app.get("/safety")
def alias_safety():
    return get_safety_triggers()

@app.get("/risk_bubbles")
def alias_risk_bubbles():
    return get_bubble_chart()

@app.get("/confidence_heatmap")
def alias_confidence_heatmap():
    return get_heatmap()

@app.get("/latency")
def alias_latency():
    return get_latency_spikes()

@app.get("/slippage")
def alias_slippage():
    return get_slippage_anomalies()
