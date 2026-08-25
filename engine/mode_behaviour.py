# engine/mode_behaviour.py

def apply_mode_behaviour(pred, mode):
    """
    Applies LIVE / SHADOW / HALT behaviour to prediction output.
    """

    adjusted = pred.copy()

    if mode == "LIVE":
        # Normal operation
        adjusted["risk"] *= 1.0
        adjusted["impact"] *= 1.0
        adjusted["latency"] *= 1.0
        adjusted["slippage"] *= 1.0
        adjusted["behaviour"] = "Normal execution"

    elif mode == "SHADOW":
        # Safe degraded mode
        adjusted["risk"] *= 1.25
        adjusted["impact"] *= 0.8
        adjusted["latency"] *= 1.5
        adjusted["slippage"] *= 0.7
        adjusted["behaviour"] = "Shadow mode: execution suppressed"

    elif mode == "HALT":
        # Emergency stop
        adjusted["risk"] *= 2.0
        adjusted["impact"] *= 1.8
        adjusted["latency"] *= 3.0
        adjusted["slippage"] *= 1.5
        adjusted["behaviour"] = "HALT: execution blocked"

    else:
        adjusted["behaviour"] = "Unknown mode"

    return adjusted
