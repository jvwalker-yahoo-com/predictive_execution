# engine/mode_history.py

from collections import deque
import time

# Keep the last 100 mode switches
MODE_HISTORY_LIMIT = 100

mode_history = deque(maxlen=MODE_HISTORY_LIMIT)


def record_mode_switch(mode, federation, pred):
    """
    Store a mode switch event with full context.
    """
    event = {
        "timestamp": time.time(),
        "mode": mode,
        "confidence": federation.get("confidence", 0),
        "votes": federation.get("votes", {}),
        "reasons": federation.get("reasons", []),
        "risk": pred.get("risk", 0),
        "impact": pred.get("impact", 0),
        "latency": pred.get("latency", 0),
        "slippage": pred.get("slippage", 0),
    }

    mode_history.append(event)


def get_mode_history():
    """
    Return the rolling mode switch history.
    """
    return list(mode_history)
