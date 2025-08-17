"""
Simulation and sensitivity analysis.

- Sensitivity ∂V/∂p via finite differences (Eq. 143)
- Monte Carlo simulation over parameter distributions (Algorithm 3)
"""
from __future__ import annotations
from typing import Callable, Dict, Tuple
import random
import statistics

def sensitivity(score_fn: Callable[[float], float], p: float, delta: float = 1e-4) -> float:
    """Approximate ∂V/∂p via symmetric finite difference around p."""
    v_plus = score_fn(p + delta)
    v_minus = score_fn(p - delta)
    return (v_plus - v_minus) / (2 * delta)

def monte_carlo(run_fn: Callable[[], float], runs: int = 1000) -> Dict[str, float]:
    """Run N simulations and summarize mean, median, stdev, and 95% CI."""
    results = [run_fn() for _ in range(runs)]
    mean = statistics.fmean(results)
    median = statistics.median(results)
    stdev = statistics.pstdev(results) if len(results) > 1 else 0.0
    # 95% normal CI approximation
    ci_low = mean - 1.96 * (stdev / max(len(results)**0.5, 1.0))
    ci_high = mean + 1.96 * (stdev / max(len(results)**0.5, 1.0))
    return {"mean": mean, "median": median, "stdev": stdev, "ci_low": ci_low, "ci_high": ci_high}
