class LatencyBrain:
    def estimate(self, features):
        hops = features.get("network_hops", 5)
        congestion = features.get("congestion", 0.1)

        return hops * 3 + congestion * 50
