# ConvenienceCalc

A Python implementation of the decision-support system described in the **ConvenienceCalc Comprehensive Technical Specification** (Aug 17, 2025). It quantifies time, stress, opportunity cost, comfort, and reliability to score premium convenience options and generate explanations, sensitivity analyses, and simulations.

## Features
- Master Convenience Value with modular sub-benefits (time, stress, opportunity, comfort, reliability)
- Context multipliers (urgency, day, weather, availability)
- Stress quantification with situational multipliers
- Opportunity cost across activity categories
- Learning loop for preference weights and choice prediction (logistic model)
- Monte Carlo simulation and what-if sensitivity
- CLI powered by `typer` and rich outputs
- Typed models using `pydantic`

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
conveniencecalc demo
conveniencecalc evaluate --config examples/lunch_vs_delivery.json
conveniencecalc simulate --config examples/commute_options.json --runs 2000
```

## Project Layout
```
conveniencecalc/
  __init__.py
  models.py         # Pydantic data models and enums
  algorithms.py     # Core formulas (Eq. 1–99)
  context.py        # Context detection and weighting
  learning.py       # Behavioral learning & preference updates
  simulation.py     # Monte Carlo + sensitivity (Eq. 143–147)
  cli.py            # Typer CLI bindings
examples/
  commute_options.json
  lunch_vs_delivery.json
tests/
  test_algorithms.py
  test_cli.py
```

## Notes
- This is a reference implementation intended for extension (APIs, persistence, integrations).
- All formulas have docstrings referencing the equation numbering from the spec for traceability.
