from __future__ import annotations
import json
from pathlib import Path
import typer
from rich import print, box
from rich.table import Table
from .models import *
from .algorithms import evaluate_option
from .simulation import monte_carlo

app = typer.Typer(help="ConvenienceCalc CLI")

@app.command()
def evaluate(config: Path = typer.Option(..., exists=True, help="JSON file for one option")):
    """
    Evaluate a single option described by a JSON file with keys:
    - option, economics, context, w_financial
    See examples/ for templates.
    """
    data = json.loads(Path(config).read_text())
    opt = Option(**data["option"])
    econ = TimeEconomics(**data["economics"])
    ctx = Context(**data["context"])
    w_fin = data.get("w_financial", 1.0)
    result = evaluate_option(opt, econ, ctx, w_financial=w_fin)

    table = Table(title=f"Evaluation: {opt.name}", box=box.SIMPLE)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for k, v in result.details.items():
        table.add_row(k, f"{v:,.4f}")
    print(table)

@app.command()
def simulate(config: Path = typer.Option(..., exists=True), runs: int = 1000):
    """
    Monte Carlo simulation. Config must include 'distributions' describing how to sample:
    - You may specify ranges for time_saved_hours and extra_cost, etc.
    """
    data = json.loads(Path(config).read_text())
    base_opt = Option(**data["option"])
    econ = TimeEconomics(**data["economics"])
    ctx = Context(**data["context"])
    w_fin = data.get("w_financial", 1.0)
    dists = data.get("distributions", {})

    def sample_option() -> Option:
        d = base_opt.model_dump()
        for field, spec in dists.items():
            if "uniform" in spec:
                lo, hi = spec["uniform"]
                d[field] = random.uniform(lo, hi)
            elif "normal" in spec:
                mu, sigma = spec["normal"]
                d[field] = random.gauss(mu, sigma)
        return Option(**d)

    def run_once() -> float:
        opt = sample_option()
        from .algorithms import master_convenience_value
        score, _ = master_convenience_value(opt, econ, ctx, w_financial=w_fin)
        return score

    summary = monte_carlo(run_once, runs=runs)
    table = Table(title=f"Monte Carlo: {base_opt.name} ({runs} runs)", box=box.SIMPLE)
    for k in ["mean","median","stdev","ci_low","ci_high"]:
        table.add_row(k, f"{summary[k]:,.4f}")
    print(table)

@app.command()
def demo():
    """Run a self-contained demo with a taxi vs bus style scenario."""
    option = Option(
        name="Taxi upgrade",
        base_cost=3.0,        # baseline (e.g., bus fare) to normalize Eq. (1)
        extra_cost=12.0,      # premium over base
        time_saved_hours=0.33,
        comfort_improvement=0.6,
        comfort_weight=10.0,
        reliability_premium=0.1,
        failure_cost=50.0,
        failure_probability=0.1,
        stress_baseline=4.0,
        stress_cost_per_point=2.0,
        stress_tolerance=StressTolerance.MEDIUM_LOW,
        stress_multipliers={"crowding":1.2,"unpredictability":1.3,"control":1.1},
        opportunity_catalog={"work":{"A":0.33,"V":20.0,"P":0.6}}
    )
    econ = TimeEconomics(annual_income=24000, annual_work_hours=1800, overtime_premium=0.1)
    ctx = Context(urgency=Urgency.NORMAL, day=DayContext.WEEKDAY, weather=WeatherContext.NORMAL, availability=Availability.SEMI_FLEXIBLE, base_multiplier=1.0, productivity_factor=1.0, minimum_rate=8.0)
    res = evaluate_option(option, econ, ctx, w_financial=1.0)
    table = Table(title="Demo Result", box=box.SIMPLE)
    for k, v in res.details.items():
        table.add_row(k, f"{v:,.4f}")
    print(table)

if __name__ == "__main__":
    app()
