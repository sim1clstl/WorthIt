"""
Data models for ConvenienceCalc.

These models map directly to the technical specification constructs:
- User profiles (financial, lifestyle, behavioral)
- Decision options and contexts
- Outputs including detailed breakdowns

All numeric fields are floats in base units (e.g., currency in user's currency,
hours for time). We keep units explicit in names where helpful.
"""
from __future__ import annotations
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class Availability(str, Enum):
    FLEXIBLE = "flexible"     # Eq. (14) → 1.0
    SEMI_FLEXIBLE = "semi"    # Eq. (14) → 0.7
    FIXED = "fixed"           # Eq. (14) → 0.3

class Urgency(str, Enum):
    EMERGENCY = "emergency"   # Eq. (15) → 2.0
    URGENT = "urgent"         # Eq. (15) → 1.5
    TIME_PRESSED = "time_pressed" # Eq. (15) → 1.2
    NORMAL = "normal"         # Eq. (15) → 1.0
    RELAXED = "relaxed"       # Eq. (15) → 0.8

class DayContext(str, Enum):
    MONDAY_MORNING = "monday_morning" # Eq. (16) → 1.3
    RUSH_HOUR = "rush_hour"           # Eq. (16) → 1.2
    WEEKDAY = "weekday"               # Eq. (16) → 1.0
    WEEKEND = "weekend"               # Eq. (16) → 0.9
    HOLIDAY = "holiday"               # Eq. (16) → 0.7

class WeatherContext(str, Enum):
    SEVERE = "severe"     # Eq. (17) → 1.4
    RAIN_SNOW = "rain_snow" # Eq. (17) → 1.2
    EXTREME_TEMP = "extreme_temp" # Eq. (17) → 1.1
    NORMAL = "normal"     # Eq. (17) → 1.0

class StressTolerance(str, Enum):
    LOW = "low"           # Eq. (22) → 2.0
    MEDIUM_LOW = "medium_low" # 1.5
    MEDIUM = "medium"     # 1.0
    MEDIUM_HIGH = "medium_high" # 0.7
    HIGH = "high"         # 0.4

class ProfileFinancial(BaseModel):
    # Eq. (47)–(48)
    monthly_income: float = Field(..., description="Imonthly")
    disposable_income: float = Field(..., description="Idisposable")
    savings_goals: float = Field(..., description="Sgoals monetary target")
    debt_obligations: float = Field(..., description="Dobligations per month")
    emergency_fund: float = Field(..., description="Efund size")
    risk_tolerance: float = Field(..., ge=1, le=10, description="Rtolerance 1–10")
    budget_categories: Dict[str, float] = Field(default_factory=dict, description="Bcategories share per category")

class ProfileLifestyle(BaseModel):
    # Eq. (49)–(50)
    work_schedule_flex: Availability = Availability.SEMI_FLEXIBLE
    family_responsibilities: float = Field(0.0, description="Fresponsibilities score 0–10")
    health_status: float = Field(5.0, description="Hstatus 0–10")
    stress_tolerance: StressTolerance = StressTolerance.MEDIUM
    priorities: Dict[str, float] = Field(default_factory=dict, description="Ppriorities normalized weights")
    location: str = Field("Unknown", description="Llocation")

class ProfileBehavioral(BaseModel):
    # Eq. (51)–(52)
    decision_patterns: Dict[str, float] = Field(default_factory=dict, description="Dpatterns")
    time_prefs: Dict[str, float] = Field(default_factory=dict, description="Tpreferences")
    recency_history: float = Field(0.0, description="Rhistory aggregate score")
    feedback_level: float = Field(0.0, description="Lfeedback")
    adaptability: float = Field(0.5, description="Aadaptability 0–1")

class UserProfile(BaseModel):
    financial: ProfileFinancial
    lifestyle: ProfileLifestyle
    behavioral: ProfileBehavioral

class Context(BaseModel):
    urgency: Urgency = Urgency.NORMAL
    day: DayContext = DayContext.WEEKDAY
    weather: WeatherContext = WeatherContext.NORMAL
    availability: Availability = Availability.SEMI_FLEXIBLE
    base_multiplier: float = Field(1.0, description="Mbase for Eq. (13)")
    productivity_factor: float = Field(1.0, description="Fproductivity for Eq. (11)")
    minimum_rate: float = Field(0.0, description="Rminimum for Eq. (11)")

class TimeEconomics(BaseModel):
    annual_income: float = Field(..., description="Iannual for Eq. (12)")
    annual_work_hours: float = Field(..., description="Hwork_annual for Eq. (12)")
    overtime_premium: float = Field(0.0, description="Povertime for Eq. (12)")

class Option(BaseModel):
    name: str
    base_cost: float = Field(..., description="Cbase")
    extra_cost: float = Field(0.0, description="Cextra premium over base")
    time_saved_hours: float = 0.0  # Tsaved
    commute_time_hours: float = 0.0 # Tcommute for Bproductivity if relevant
    productivity_rate: float = 0.0  # Rproductive if applicable
    activity_value: float = 0.0     # Vactivity for commute productivity
    comfort_improvement: float = 0.0 # Cimprovement
    comfort_weight: float = 0.0      # Wcomfort
    reliability_premium: float = 0.0 # Rpremium - Rstandard
    failure_cost: float = 0.0        # Cfailure
    failure_probability: float = 0.0 # Pfailure
    stress_baseline: float = 0.0     # Sbase 1–10
    stress_cost_per_point: float = 0.0 # Cpersonal
    stress_tolerance: StressTolerance = StressTolerance.MEDIUM
    stress_multipliers: Dict[str, float] = Field(default_factory=dict, description="Msituation factors e.g., crowding, unpredictability, control")
    opportunity_catalog: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Activities: {name: {A, V, P}}")

class EvaluationResult(BaseModel):
    option: Option
    details: Dict[str, float]
    score: float
