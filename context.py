"""
Context detection and dynamic weighting.

Implements tables from the spec for weighting different context factors by decision type.
"""
from __future__ import annotations
from typing import Dict

DECISION_CONTEXT_WEIGHTS: Dict[str, Dict[str, float]] = {
    # Section 6.2 table
    "transportation": {"weather": 0.8, "time": 0.9, "calendar": 0.7, "location": 0.9},
    "food":           {"weather": 0.6, "time": 0.8, "calendar": 0.8, "location": 0.5},
    "shopping":       {"weather": 0.4, "time": 0.6, "calendar": 0.5, "location": 0.7},
    "services":       {"weather": 0.3, "time": 0.7, "calendar": 0.9, "location": 0.4},
    "entertainment":  {"weather": 0.5, "time": 0.8, "calendar": 0.6, "location": 0.8},
}

def weighted_context_importance(decision_type: str) -> Dict[str, float]:
    """Return weight dict for decision_type; defaults to transportation if unknown."""
    return DECISION_CONTEXT_WEIGHTS.get(decision_type, DECISION_CONTEXT_WEIGHTS["transportation"]).copy()
