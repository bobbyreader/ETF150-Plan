from __future__ import annotations


def estimate_max_drawdown(category: str) -> str:
    """Return expected maximum drawdown range by category."""
    mapping = {
        "financial": "50%-60%",
        "securities": "50%-60%",
        "growth": "40%-60%",
        "chinext": "40%-60%",
        "small_mid": "25%-40%",
        "dividend": "25%-40%",
        "broad": "25%-40%",
    }
    return mapping.get(category, "25%-40%")
