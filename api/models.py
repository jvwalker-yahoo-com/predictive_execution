# paste SQLAlchemy models here

from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ---------------------------------------------------------
# Temporal Memory Episodes
# ---------------------------------------------------------

class TemporalEpisode(Base):
    __tablename__ = "temporal_episodes"

    id = Column(String, primary_key=True)
    timestamp = Column(Float)
    symbol = Column(String)
    regime = Column(String)
    riskScore = Column(Float)
    slippageBps = Column(Float)
    impactBps = Column(Float)
    latencyMs = Column(Float)
    syncDriftMs = Column(Float)
    fillQuality = Column(Float)
    autopilotMode = Column(String)
    safetyState = Column(String)
    twinStatus = Column(String)
    narrativeSummary = Column(String)
    tags = Column(JSON)


# ---------------------------------------------------------
# Evolution Engine: Genomes
# ---------------------------------------------------------

class BrainGenome(Base):
    __tablename__ = "brain_genomes"

    name = Column(String, primary_key=True)
    aggression = Column(Float)
    riskAversion = Column(Float)
    latencySensitivity = Column(Float)
    routingBoldness = Column(Float)


# ---------------------------------------------------------
# Evolution Engine: Performance Samples
# ---------------------------------------------------------

class BrainPerformanceSample(Base):
    __tablename__ = "brain_performance_samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    timestamp = Column(Float)
    riskScore = Column(Float)
    slippageBps = Column(Float)
    impactBps = Column(Float)
    safetyTriggered = Column(Boolean)
    finalMode = Column(String)


# ---------------------------------------------------------
# Personality Engine
# ---------------------------------------------------------

class BrainPersonality(Base):
    __tablename__ = "brain_personalities"

    name = Column(String, primary_key=True)
    traits = Column(JSON)


# ---------------------------------------------------------
# Parliament Bills
# ---------------------------------------------------------

class ParliamentBill(Base):
    __tablename__ = "parliament_bills"

    id = Column(String, primary_key=True)
    title = Column(String)
    proposer = Column(String)
    content = Column(String)
    amendments = Column(JSON)
    committee = Column(String)
    passed = Column(Boolean)
    votes = Column(JSON)


# ---------------------------------------------------------
# Arbitration Court Precedents
# ---------------------------------------------------------

class ArbitrationPrecedent(Base):
    __tablename__ = "arbitration_precedents"

    id = Column(String, primary_key=True)
    timestamp = Column(Float)
    finalMode = Column(String)
    reason = Column(String)
    notes = Column(JSON)
