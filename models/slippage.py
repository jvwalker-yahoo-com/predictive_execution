class SlippageBrain:
    def estimate(self, features):
        spread = features.get("spread", 0.01)
        volatility = features.get("volatility", 0.2)

        return round(spread * volatility * 100, 3)
