# paste your orchestrator code here
import time
import uuid

from engine.database import SessionLocal
from api.models import (
    TemporalEpisode,
    BrainPerformanceSample,
    BrainGenome,
    BrainPersonality,
    ArbitrationPrecedent
)

# Import your real engine
from engine.predictive_execution_full import Orchestrator as BaseOrchestrator


class Orchestrator(BaseOrchestrator):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()

        self._load_genomes()
        self._load_personalities()

    # ---------------------------------------------------------
    # Load persistent genomes into evolution engine
    # ---------------------------------------------------------
    def _load_genomes(self):
        rows = self.db.query(BrainGenome).all()

        if not rows:
            # First run: save initial genomes
            for g in self.evolution.genomes:
                self.db.add(BrainGenome(
                    name=g["name"],
                    aggression=g["aggression"],
                    riskAversion=g["riskAversion"],
                    latencySensitivity=g["latencySensitivity"],
                    routingBoldness=g["routingBoldness"]
                ))
            self.db.commit()
        else:
            # Load genomes from DB into engine
            self.evolution.genomes = [
                {
                    "name": r.name,
                    "aggression": r.aggression,
                    "riskAversion": r.riskAversion,
                    "latencySensitivity": r.latencySensitivity,
                    "routingBoldness": r.routingBoldness
                }
                for r in rows
            ]

    # ---------------------------------------------------------
    # Load persistent personalities into personality engine
    # ---------------------------------------------------------
    def _load_personalities(self):
        rows = self.db.query(BrainPersonality).all()

        if not rows:
            # First run: save initial personalities
            for p in self.personality_engine.personalities:
                self.db.add(BrainPersonality(
                    name=p["name"],
                    traits=p["traits"]
                ))
            self.db.commit()
        else:
            # Load personalities from DB
            self.personality_engine.personalities = [
                {"name": r.name, "traits": r.traits}
                for r in rows
            ]

    # ---------------------------------------------------------
    # Persist temporal episode
    # ---------------------------------------------------------
    def persist_episode(self, episode):
        ep = TemporalEpisode(
            id=str(uuid.uuid4()),
            timestamp=episode["timestamp"],
            symbol=episode["symbol"],
            regime=episode["regime"],
            riskScore=episode["riskScore"],
            slippageBps=episode["slippageBps"],
            impactBps=episode["impactBps"],
            latencyMs=episode["latencyMs"],
            syncDriftMs=episode["syncDriftMs"],
            fillQuality=episode["fillQuality"],
            autopilotMode=episode["autopilotMode"],
            safetyState=episode["safetyState"],
            twinStatus=episode["twinStatus"],
            narrativeSummary=episode["narrativeSummary"],
            tags=episode["tags"]
        )
        self.db.add(ep)
        self.db.commit()

    # ---------------------------------------------------------
    # Persist performance sample
    # ---------------------------------------------------------
    def persist_performance(self, sample):
        row = BrainPerformanceSample(
            name=sample["name"],
            timestamp=sample["timestamp"],
            riskScore=sample["riskScore"],
            slippageBps=sample["slippageBps"],
            impactBps=sample["impactBps"],
            safetyTriggered=sample["safetyTriggered"],
            finalMode=sample["finalMode"]
        )
        self.db.add(row)
        self.db.commit()

    # ---------------------------------------------------------
    # Persist arbitration precedent
    # ---------------------------------------------------------
    def persist_arbitration(self, ruling):
        row = ArbitrationPrecedent(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            finalMode=ruling["finalMode"],
            reason=ruling["reason"],
            notes=ruling["arbitrationNotes"]
        )
        self.db.add(row)
        self.db.commit()

    # ---------------------------------------------------------
    # Main engine step with persistence
    # ---------------------------------------------------------
    def step_with_persistence(self):
        result = super().step()

        # Build temporal episode record
        episode = {
            "timestamp": time.time() * 1000,
            "symbol": "CLOUD",
            "regime": self.state.global_regime,
            "riskScore": self.state.global_risk,
            "slippageBps": self.state.global_slippage,
            "impactBps": self.state.global_impact,
            "latencyMs": self.state.global_latency,
            "syncDriftMs": self.state.global_sync,
            "fillQuality": self.state.global_fill_quality,
            "autopilotMode": result["autonomous"],
            "safetyState": (
                "HALT" if result["final_mode"] == "HALT"
                else "SHADOW" if result["final_mode"] == "SHADOW"
                else "OK"
            ),
            "twinStatus": "ALIGNED",
            "narrativeSummary": "Cloud episode",
            "tags": []
        }

        self.persist_episode(episode)

        # Build performance sample
        perf = {
            "name": "RiskBrain",
            "timestamp": time.time(),
            "riskScore": self.state.global_risk,
            "slippageBps": self.state.global_slippage,
            "impactBps": self.state.global_impact,
            "safetyTriggered": result["final_mode"] == "HALT",
            "finalMode": result["final_mode"]
        }

        self.persist_performance(perf)

        # Persist arbitration ruling
        self.persist_arbitration(result["arbitration"])

        return result
