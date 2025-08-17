"""
Behavioral learning and preference updates.

Implements:
- Logistic choice prediction (Eq. 116)
- Online weight updates (Eq. 122)
- Confidence scoring (Eq. 127)
"""
from __future__ import annotations
from typing import List, Dict
import math
from dataclasses import dataclass

@dataclass
class LogisticModel:
    weights: List[float]
    bias: float = 0.0
    k_conf: float = 0.2   # k in Eq. (127)
    theta: int = 20       # θ in Eq. (127)
    seen: int = 0         # number of decisions observed

    def predict_prob(self, features: List[float]) -> float:
        z = sum(w*x for w, x in zip(self.weights, features)) + self.bias
        return 1.0 / (1.0 + math.exp(-z))  # σ

    def update(self, features: List[float], actual_choice: float, lr: float = 0.05) -> None:
        """Online update per Eq. (122) with δ = (actual - predicted)."""
        p = self.predict_prob(features)
        delta = (actual_choice - p)
        for i in range(len(self.weights)):
            self.weights[i] += lr * delta * features[i]
        self.bias += lr * delta
        self.seen += 1

    def confidence(self) -> float:
        """Sigmoid confidence per Eq. (127)."""
        return 1.0 / (1.0 + math.exp(-self.k_conf * (self.seen - self.theta)))
