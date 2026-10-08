"""
dataset_generator.py
Loads household energy dataset from app/data folder.
"""

import pandas as pd


def load_real_dataset():

    file_path = "app/data/household_power_consumption.txt"

    df = pd.read_csv(
        file_path,
        sep=";",
        nrows=50000,
        low_memory=False
    )

    df.columns = [
        "Date",
        "Time",
        "global_active_power",
        "global_reactive_power",
        "voltage",
        "global_intensity",
        "sub_metering_1",
        "sub_metering_2",
        "sub_metering_3"
    ]

    df["timestamp"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True,
        errors="coerce"
    )

    numeric_cols = [
        "global_active_power",
        "voltage",
        "sub_metering_1",
        "sub_metering_2",
        "sub_metering_3"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["temperature_c"] = 28 + (df["hour"] / 24) * 8
    df["humidity"] = 75 - (df["temperature_c"] - 28)

    df["peak_hour_flag"] = (
        (df["hour"] >= 18) &
        (df["hour"] <= 22)
    ).astype(int)

    df["tariff_rate"] = 6.5

    return df