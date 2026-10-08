"""
optimizer.py
Heuristic smart-scheduling engine: shifts flexible appliance loads
(washing machine, dishwasher, water heater, EV charger) out of
high-tariff peak windows into the cheapest allowed off-peak windows,
while respecting user preference windows.

Also estimates carbon savings using a grid emission factor.
"""

from dataclasses import dataclass, field
from typing import List, Dict

GRID_EMISSION_FACTOR_KG_PER_KWH = 0.82   # India grid average (approx.)
TREE_ABSORPTION_KG_PER_YEAR = 21.0       # kg CO2 absorbed by one mature tree / year


@dataclass
class FlexibleAppliance:
    name: str
    kwh_per_cycle: float
    cycles_per_week: int
    preferred_windows: List[tuple] = field(default_factory=lambda: [(0, 24)])  # allowed hour ranges


DEFAULT_APPLIANCES = [
    FlexibleAppliance("Washing Machine", 1.2, 5, preferred_windows=[(0, 7), (14, 17)]),
    FlexibleAppliance("Dishwasher", 0.9, 7, preferred_windows=[(0, 7), (13, 17)]),
    FlexibleAppliance("Water Heater", 1.5, 7, preferred_windows=[(5, 8), (22, 24), (0, 1)]),
    FlexibleAppliance("EV Charger", 7.0, 4, preferred_windows=[(0, 6)]),
]


def _tariff_for_hour(hour: int) -> float:
    if 18 <= hour < 22:
        return 10.5
    if 9 <= hour < 18:
        return 7.5
    return 5.0


def _cheapest_hour_in_windows(windows) -> int:
    candidates = []
    for start, end in windows:
        candidates.extend(range(start, min(end, 24)))
    if not candidates:
        candidates = list(range(24))
    return min(candidates, key=_tariff_for_hour)


def optimize_schedule(appliances: List[FlexibleAppliance] = None) -> Dict:
    appliances = appliances or DEFAULT_APPLIANCES

    schedule = []
    total_original_cost = 0.0
    total_optimized_cost = 0.0
    total_shifted_kwh = 0.0

    # Assume, pre-optimization, flexible loads were naively run during evening peak (18-22h)
    ORIGINAL_HOUR = 19

    for appliance in appliances:
        original_hour = ORIGINAL_HOUR
        optimized_hour = _cheapest_hour_in_windows(appliance.preferred_windows)

        weekly_kwh = appliance.kwh_per_cycle * appliance.cycles_per_week
        original_cost = weekly_kwh * _tariff_for_hour(original_hour)
        optimized_cost = weekly_kwh * _tariff_for_hour(optimized_hour)

        total_original_cost += original_cost
        total_optimized_cost += optimized_cost
        total_shifted_kwh += weekly_kwh

        schedule.append({
            "appliance": appliance.name,
            "kwh_per_cycle": appliance.kwh_per_cycle,
            "cycles_per_week": appliance.cycles_per_week,
            "original_hour": original_hour,
            "optimized_hour": optimized_hour,
            "original_tariff": _tariff_for_hour(original_hour),
            "optimized_tariff": _tariff_for_hour(optimized_hour),
            "weekly_original_cost": round(original_cost, 2),
            "weekly_optimized_cost": round(optimized_cost, 2),
            "weekly_savings": round(original_cost - optimized_cost, 2),
        })

    weekly_savings = total_original_cost - total_optimized_cost
    monthly_savings = weekly_savings * 4.345

    # Carbon impact: peak-hour grid is assumed marginally dirtier due to peaker plants
    peak_emission_factor = GRID_EMISSION_FACTOR_KG_PER_KWH * 1.15
    offpeak_emission_factor = GRID_EMISSION_FACTOR_KG_PER_KWH * 0.9
    co2_saved_weekly = total_shifted_kwh * (peak_emission_factor - offpeak_emission_factor)
    co2_saved_monthly = co2_saved_weekly * 4.345
    trees_equivalent = co2_saved_monthly * 12 / TREE_ABSORPTION_KG_PER_YEAR

    return {
        "schedule": schedule,
        "summary": {
            "weekly_original_cost": round(total_original_cost, 2),
            "weekly_optimized_cost": round(total_optimized_cost, 2),
            "weekly_savings": round(weekly_savings, 2),
            "monthly_savings": round(monthly_savings, 2),
            "co2_saved_kg_monthly": round(co2_saved_monthly, 2),
            "trees_equivalent_yearly": round(trees_equivalent, 2),
            "shifted_kwh_weekly": round(total_shifted_kwh, 2),
        },
    }
