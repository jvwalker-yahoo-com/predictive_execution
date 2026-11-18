from typing import Any, Dict
from engine.federation import run_tick


class Orchestrator:
    def __init__(self):
        self.state = DummyState()
        self.temporal = DummyTemporal()
        self.federation = DummyFederation()
        self.arbitration = DummyArbitration()
        self.evolution = DummyEvolution()
        self.personality_engine = DummyPersonality()

    def step(self, symbol: str = "AAPL") -> Dict[str, Any]:
        tick = run_tick(symbol)
        pred = tick["prediction"]
        st = tick["state"]
        fed = tick["federation"]["federation"]

        self.state.global_regime = st.get("regime", "NORMAL")
        self.state.global_risk = float(pred.get("risk", 0.1))
        self.state.global_slippage = float(pred.get("slippage", 0.0))
        self.state.global_impact = float(pred.get("impact", 0.0))
        self.state.global_latency = float(pred.get("latency", 10.0))

        return {
            "autonomous": "ON",
            "symbol": pred.get("symbol", symbol),
            "final_mode": fed.get("mode", "OK"),
            "signal_action": pred.get("signal_action", "HOLD"),
            "conviction_score": pred.get("conviction_score", 5.0),
            "openbb_decision": pred.get("openbb_decision", {}),
            "arbitration": {
                "finalMode": fed.get("mode", "OK"),
                "reason": "; ".join(fed.get("reasons", ["OpenBB multi-brain arbitration"])),
                "arbitrationNotes": {
                    "confidence": fed.get("confidence", 0.8),
                    "votes": fed.get("votes", {}),
                }
            }
        }

    def update_state_from_feed(self, feed: Dict[str, Any]):
        if not feed:
            return
        self.state.global_risk = float(feed.get("risk", self.state.global_risk))
        self.state.global_impact = float(feed.get("impact", self.state.global_impact))
        self.state.global_slippage = float(feed.get("slippage", self.state.global_slippage))
        self.state.global_latency = float(feed.get("latency", self.state.global_latency))


class DummyState:
    def __init__(self):
        self.global_regime = "NORMAL"
        self.global_risk = 0.1
        self.global_slippage = 0.0
        self.global_impact = 0.0
        self.global_latency = 10.0
        self.global_sync = 0
        self.global_fill_quality = 1.0

    def snapshot(self):
        return {
            "regime": self.global_regime,
            "risk": self.global_risk,
            "slippage": self.global_slippage,
            "impact": self.global_impact,
            "latency": self.global_latency,
            "sync": self.global_sync,
            "fill_quality": self.global_fill_quality
        }


class DummyTemporal:
    def evaluate(self):
        return {"temporal": "aligned"}


class DummyFederation:
    def evaluate(self, state):
        return {"outputs": ["RiskBrain", "ImpactBrain", "OpenBBBrain"], "federation": "active"}


class DummyArbitration:
    def rule(self, state, outputs, fed):
        return {"final_mode": "OK", "reason": "OpenBB multi-brain consensus", "arbitrationNotes": {}}


class DummyEvolution:
    def __init__(self):
        self.genomes = [
            {
                "name": "default",
                "aggression": 0.5,
                "riskAversion": 0.5,
                "latencySensitivity": 0.5,
                "routingBoldness": 0.5
            }
        ]


class DummyPersonality:
    def __init__(self):
        self.personalities = [
            {"name": "default", "traits": {"confidence": 0.5}}
        ]
