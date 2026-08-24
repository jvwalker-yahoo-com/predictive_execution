class FederationBrain:
    def combine(self, outputs):
        # Combine multiple model outputs into a final decision
        return {
            "risk": outputs["risk"],
            "impact": outputs["impact"],
            "latency": outputs["latency"],
            "slippage": outputs["slippage"],
            "final_mode": outputs["mode"]
        }
