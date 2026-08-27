# =========================================================
# Predictive Execution – Full FastAPI Server
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import random
import time
import os

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
# Serve dashboard folder
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

# Redirect root → dashboard
@app.get("/")
def root():
    return RedirectResponse("/dashboard")

# -----------------------------
# DEBUG ENDPOINT (to verify Render file layout)
# -----------------------------
@app.get("/debug_files")
def debug_files():
    try:
        return {
            "cwd": os.getcwd(),
            "files": os.listdir("."),
            "dashboard_exists": os.path.isdir("dashboard"),
            "dashboard_files": os.listdir("dashboard") if os.path.isdir("dashboard") else "MISSING"
        }
    except Exception as e:
        return {"error": str(e)}

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
                "type": random.choice(["SPIKE", "DROP
