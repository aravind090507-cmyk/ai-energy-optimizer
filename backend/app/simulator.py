import pandas as pd
import numpy as np
from app.optimizer import GRID_EMISSION_FACTOR_KG_PER_KWH

SUB_METER_COLS = {
    "Kitchen": "sub_metering_1",
    "Laundry": "sub_metering_2",
    "HVAC/AC": "sub_metering_3",
}

def _tariff_rate(hours: np.ndarray) -> np.ndarray:
    """Vectorized tariff rate calculator matching dynamic rates in data_pipeline.py."""
    rates = np.full(hours.shape, 6.5)
    rates[(hours >= 18) & (hours < 22)] = 10.5
    rates[(hours >= 22) | (hours < 6)] = 5.0
    return rates

def simulate_scenario(df: pd.DataFrame, appliance: str, action: str, value: float) -> dict:
    if appliance not in SUB_METER_COLS:
        raise ValueError(f"Unknown appliance: {appliance}")
    
    col = SUB_METER_COLS[appliance]
    sim = df.copy()

    if action == "shift_hours":
        shift = int(value)
        sim["hour_new"] = (sim["hour"] + shift) % 24
        moved = sim[[col]].copy()
        moved["hour"] = sim["hour_new"]
        new_by_hour = moved.groupby("hour")[col].mean()
        sim[col + "_new"] = sim["hour_new"].map(new_by_hour)
        sim["tariff_new"] = _tariff_rate(sim["hour_new"].to_numpy())
    elif action == "reduce_pct":
        sim[col + "_new"] = sim[col] * (1 - value / 100)
        sim["tariff_new"] = sim["tariff_rate"]
    else:
        raise ValueError("action must be 'shift_hours' or 'reduce_pct'")

    sim["global_active_power_new"] = (
        sim["global_active_power"] - sim[col] + sim[col + "_new"]
    ).clip(lower=0)
    sim["cost_new"] = sim["global_active_power_new"] * sim["tariff_new"]

    original_cost = float(df["cost"].sum())
    new_cost = float(sim["cost_new"].sum())
    original_kwh = float(df["global_active_power"].sum())
    new_kwh = float(sim["global_active_power_new"].sum())

    co2_before = original_kwh * GRID_EMISSION_FACTOR_KG_PER_KWH
    co2_after = new_kwh * GRID_EMISSION_FACTOR_KG_PER_KWH

    return {
        "appliance": appliance,
        "action": action,
        "value": value,
        "cost_before": round(original_cost, 2),
        "cost_after": round(new_cost, 2),
        "cost_savings": round(original_cost - new_cost, 2),
        "co2_before_kg": round(co2_before, 2),
        "co2_after_kg": round(co2_after, 2),
        "co2_savings_kg": round(co2_before - co2_after, 2),
    }
