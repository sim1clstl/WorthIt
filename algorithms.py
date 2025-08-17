"""
Core algorithms implementing the mathematical framework.

Each function references the equation numbers from the Technical Specification
for traceability (e.g., Eq. (4), Eq. (9), etc.).
"""
from __future__ import annotations
from typing import Dict, Tuple
from .models import (
    Option, Context, TimeEconomics, UserProfile,
    Urgency, DayContext, WeatherContext, Availability,
    StressTolerance, EvaluationResult
)

def hourly_rate(econ: TimeEconomics) -> float:
    """Compute Rhourly per Eq. (12)."""
    base = econ.annual_income / max(econ.annual_work_hours, 1e-9)
    return base * (1.0 + econ.overtime_premium)

def effective_rate(econ: TimeEconomics, ctx: Context) -> float:
    """Reffective per Eq. (11): max(Rhourly, Rminimum) × Fproductivity."""
    r = max(hourly_rate(econ), ctx.minimum_rate)
    return r * ctx.productivity_factor

def context_multiplier(ctx: Context) -> float:
    """Mcontext per Eq. (13) with components (15)–(17) and Mbase."""
    m_urgency = {
        Urgency.EMERGENCY: 2.0,
        Urgency.URGENT: 1.5,
        Urgency.TIME_PRESSED: 1.2,
        Urgency.NORMAL: 1.0,
        Urgency.RELAXED: 0.8,
    }[ctx.urgency]
    m_day = {
        DayContext.MONDAY_MORNING: 1.3,
        DayContext.RUSH_HOUR: 1.2,
        DayContext.WEEKDAY: 1.0,
        DayContext.WEEKEND: 0.9,
        DayContext.HOLIDAY: 0.7,
    }[ctx.day]
    m_weather = {
        WeatherContext.SEVERE: 1.4,
        WeatherContext.RAIN_SNOW: 1.2,
        WeatherContext.EXTREME_TEMP: 1.1,
        WeatherContext.NORMAL: 1.0,
    }[ctx.weather]
    return ctx.base_multiplier * m_urgency * m_day * m_weather

def availability_multiplier(ctx: Context) -> float:
    """Aavailability per Eq. (14)."""
    return {
        Availability.FLEXIBLE: 1.0,
        Availability.SEMI_FLEXIBLE: 0.7,
        Availability.FIXED: 0.3,
    }[ctx.availability]

def time_value(opt: Option, econ: TimeEconomics, ctx: Context) -> float:
    """Btime per Eq. (9): Tsaved × Reffective × Mcontext × Aavailability."""
    return opt.time_saved_hours * effective_rate(econ, ctx) * context_multiplier(ctx) * availability_multiplier(ctx)

def stress_tolerance_factor(tol: StressTolerance) -> float:
    """Ftolerance per Eq. (22)."""
    return {
        StressTolerance.LOW: 2.0,
        StressTolerance.MEDIUM_LOW: 1.5,
        StressTolerance.MEDIUM: 1.0,
        StressTolerance.MEDIUM_HIGH: 0.7,
        StressTolerance.HIGH: 0.4,
    }[tol]

def stress_value(opt: Option) -> float:
    """Bstress per Eq. (18)–(26)."""
    msituation = 1.0
    for k, v in opt.stress_multipliers.items():
        msituation *= v
    ftol = stress_tolerance_factor(opt.stress_tolerance)
    return opt.stress_baseline * msituation * ftol * opt.stress_cost_per_point

def opportunity_value(opt: Option) -> float:
    """Bopportunity per Eq. (27)–(36). Expects opportunity_catalog entries with A, V, P."""
    total = 0.0
    for _name, d in opt.opportunity_catalog.items():
        A = d.get("A", 0.0)
        V = d.get("V", 0.0)
        P = d.get("P", 0.0)
        total += A * V * P
    return total

def comfort_value(opt: Option) -> float:
    """Bcomfort per Eq. (37)–(39). Here we use single aggregated improvement × weight."""
    return opt.comfort_improvement * opt.comfort_weight

def reliability_value(opt: Option) -> float:
    """Breliability per Eq. (41)–(46)."""
    return opt.reliability_premium * opt.failure_cost * opt.failure_probability

def master_convenience_value(opt: Option, econ: TimeEconomics, ctx: Context, w_financial: float = 1.0) -> Tuple[float, Dict[str, float]]:
    """
    V_convenience per Eq. (1)–(3): (Btotal − Cextra) / Cbase × Wfinancial.
    Returns (score, details dict).
    """
    b_time = time_value(opt, econ, ctx)
    b_stress = stress_value(opt)
    b_opp = opportunity_value(opt)
    b_comfort = comfort_value(opt)
    b_rel = reliability_value(opt)
    b_total = b_time + b_stress + b_opp + b_comfort + b_rel
    numerator = b_total - opt.extra_cost
    denom = max(opt.base_cost, 1e-9)
    score = (numerator / denom) * w_financial
    details = {
        "B_time": b_time,
        "B_stress": b_stress,
        "B_opportunity": b_opp,
        "B_comfort": b_comfort,
        "B_reliability": b_rel,
        "B_total": b_total,
        "C_extra": opt.extra_cost,
        "C_base": opt.base_cost,
        "score": score,
    }
    return score, details

def evaluate_option(opt: Option, econ: TimeEconomics, ctx: Context, profile: UserProfile | None = None, w_financial: float = 1.0) -> EvaluationResult:
    """Convenience wrapper producing an EvaluationResult with rich details."""
    score, details = master_convenience_value(opt, econ, ctx, w_financial=w_financial)
    return EvaluationResult(option=opt, details=details, score=score)
