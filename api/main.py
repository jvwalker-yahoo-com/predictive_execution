# paste FastAPI server here
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine.orchestrator import Orchestrator
from engine.database import engine, SessionLocal
from api.models import Base, TemporalEpisode, BrainPerformanceSample, ArbitrationPrecedent

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Predictive Execution Engine",
    description="Cloud-hosted execution engine with federation, arbitration, evolution, and temporal memory.",
    version="1.0"
)

# Allow dashboard access from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orch = Orchestrator()


# -----------------------------
# Core Engine Endpoints
# -----------------------------

@app.get("/state")
def get_state():
    """Return the engine's current state snapshot."""
    return orch.state.snapshot()


@app.get("/decision")
def get_decision():
    """Run one full engine step and persist the results."""
    return orch.step_with_persistence()


@app.post("/feed")
def post_feed(feed: dict):
    """Inject external data into the engine."""
    orch.update_state_from_feed(feed)
    return {"status": "ok"}


@app.get("/temporal")
def get_temporal():
    """Return temporal engine evaluation."""
    return orch.temporal.evaluate()


@app.get("/federation")
def get_federation():
    """Return federation vote results."""
    return orch.federation.evaluate(orch.state)


@app.get("/arbitration")
def get_arbitration():
    """Return arbitration ruling."""
    fed = orch.federation.evaluate(orch.state)
    return orch.arbitration.rule(orch.state, fed["outputs"], fed)


# -----------------------------
# Database Access Endpoints
# -----------------------------

@app.get("/episodes")
def get_episodes(limit: int = 50):
    """Return recent temporal episodes."""
    db = SessionLocal()
    eps = (
        db.query(TemporalEpisode)
        .order_by(TemporalEpisode.timestamp.desc())
        .limit(limit)
        .all()
    )
    return eps


@app.get("/performance")
def get_performance(limit: int = 50):
    """Return recent performance samples."""
    db = SessionLocal()
    samples = (
        db.query(BrainPerformanceSample)
        .order_by(BrainPerformanceSample.timestamp.desc())
        .limit(limit)
        .all()
    )
    return samples


@app.get("/precedents")
def get_precedents(limit: int = 50):
    """Return recent arbitration precedents."""
    db = SessionLocal()
    prec = (
        db.query(ArbitrationPrecedent)
        .order_by(ArbitrationPrecedent.timestamp.desc())
        .limit(limit)
        .all()
    )
    return prec
