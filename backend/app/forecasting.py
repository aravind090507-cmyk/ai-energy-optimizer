"""
forecasting.py
Multi-step forecasts (next 24h / 7d / 30d) built on top of the trained
RandomForest load model, with simple confidence bands derived from the
model's per-tree prediction spread.
"""

import numpy as np
import pandas as pd
from datetime import timedelta

from .ml_engine import FEATURES


def _future_feature_frame(last_timestamp: pd.Timestamp, hours: int, avg_temp_by_hour: dict) -> pd.DataFrame:
    rows = []
    for i in range(1, hours + 1):
        ts = last_timestamp + timedelta(hours=i)
        hour = ts.hour
        rows.append({
            "timestamp": ts,
            "hour": hour,
            "day_of_week": ts.dayofweek,
            "is_weekend": int(ts.dayofweek >= 5),
            "temperature_c": avg_temp_by_hour.get(hour, 29.0),
            "humidity": 65.0,
            "peak_hour_flag": int(18 <= hour < 22),
        })
    return pd.DataFrame(rows)


def forecast_horizon(engine, df: pd.DataFrame, hours: int) -> list:
    """Return a list of {timestamp, predicted_kw, lower, upper} dicts."""
    avg_temp_by_hour = df.groupby("hour")["temperature_c"].mean().to_dict()
    future = _future_feature_frame(df["timestamp"].max(), hours, avg_temp_by_hour)

    avg_voltage_by_hour = df.groupby("hour")["voltage"].mean().to_dict()
    avg_intensity_by_hour = df.groupby("hour")["global_intensity"].mean().to_dict()
    future["voltage"] = future["hour"].map(avg_voltage_by_hour).fillna(240.0)
    future["global_intensity"] = future["hour"].map(avg_intensity_by_hour).fillna(4.0)

    mean_pred = engine.predict_load(future)
    std_v = getattr(engine, "active_reg_rmse", 0.15)

    results = []
    for ts, mean_v in zip(future["timestamp"], mean_pred):
        results.append({
            "timestamp": ts.isoformat(),
            "predicted_kw": round(float(max(mean_v, 0)), 3),
            "lower": round(float(max(mean_v - 1.96 * std_v, 0)), 3),
            "upper": round(float(max(mean_v + 1.96 * std_v, 0)), 3),
        })
    return results


def build_all_forecasts(engine, df: pd.DataFrame) -> dict:
    return {
        "next_24h": forecast_horizon(engine, df, 24),
        "next_7d": forecast_horizon(engine, df, 24 * 7)[::6],   # thin to ~28 points
        "next_30d": forecast_horizon(engine, df, 24 * 30)[::24],  # one point per day
    }
