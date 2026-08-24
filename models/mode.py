class ModeBrain:
    def decide(self, risk, impact, latency, slippage):
        if risk > 0.7:
            return "HALT"
        if impact > 50:
            return "SLOW"
        if latency > 200:
            return "WAIT"
        if slippage > 5:
            return "ADJUST"
        return "OK"
