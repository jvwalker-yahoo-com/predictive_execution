class ImpactBrain:
    def predict(self, features):
        order_size = features.get("order_size", 1000)
        liquidity = features.get("liquidity", 500000)

        impact_bps = (order_size / liquidity) * 10000
        return round(impact_bps, 2)
