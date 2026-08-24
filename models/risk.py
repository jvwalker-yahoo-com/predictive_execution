import numpy as np

class RiskBrain:
    def __init__(self):
        # Example: load a trained model
        # self.model = joblib.load("risk_model.pkl")
        pass

    def score(self, features):
        # Example real logic
        volatility = features.get("volatility", 0.2)
        spread = features.get("spread", 0.01)
        volume = features.get("volume", 100000)

        risk = (volatility * 0.6) + (spread * 10) - (np.log(volume) * 0.05)
        return max(0, min(risk, 1))
