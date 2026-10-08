"""
data_pipeline.py
Cleaning and preprocessing for household power dataset.
"""

import pandas as pd


def clean_data(df):

    df = df.copy()

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    print("CLEANED COLUMNS:")
    print(df.columns.tolist())

    # create timestamp
    if "date" in df.columns and "time" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["date"] + " " + df["time"],
            errors="coerce",
            dayfirst=True
        )

    numeric_cols = [
        "global_active_power",
        "global_reactive_power",
        "voltage",
        "global_intensity",
        "sub_metering_1",
        "sub_metering_2",
        "sub_metering_3"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df[numeric_cols] = df[numeric_cols].ffill()
    df[numeric_cols] = df[numeric_cols].bfill()

    # time features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # peak hours
    df["peak_hour_flag"] = (
        (df["hour"] >= 18) &
        (df["hour"] < 22)
    ).astype(int)

    # tariff
    df["tariff_rate"] = 6.5

    df.loc[
        (df["hour"] >= 18) &
        (df["hour"] < 22),
        "tariff_rate"
    ] = 10.5

    df.loc[
        (df["hour"] >= 22) |
        (df["hour"] < 6),
        "tariff_rate"
    ] = 5.0

    # cost
    df["cost"] = (
        df["global_active_power"] *
        df["tariff_rate"]
    )

    # outliers
    q1 = df["global_active_power"].quantile(0.25)
    q3 = df["global_active_power"].quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    df["is_outlier"] = (
        (df["global_active_power"] < lower)
        |
        (df["global_active_power"] > upper)
    ).astype(int)

    return df


def compute_eda_stats(df):

    return {
        "total_records": int(len(df)),
        "total_energy": round(
            float(df["global_active_power"].sum()),
            2
        ),
        "average_voltage": round(
            float(df["voltage"].mean()),
            2
        ),
        "total_cost": round(
            float(df["cost"].sum()),
            2
        ),
        "outlier_count": int(
            df["is_outlier"].sum()
        )
    }