"""
main.py
AI Energy Optimizer API using real household power dataset.
"""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dataset_generator import load_real_dataset
from app.data_pipeline import clean_data, compute_eda_stats
from app.ml_engine import EnergyMLEngine
from app.optimizer import optimize_schedule
from app.forecasting import build_all_forecasts
from app.ai_assistant import EnergyAssistant
import numpy as np

app = FastAPI(
    title="AI Energy Optimizer",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE = {}


def bootstrap():

    print("Loading dataset...")

    raw_df = load_real_dataset()

    print("Cleaning dataset...")

    df = clean_data(raw_df)

    print("Training models...")

    engine = EnergyMLEngine()

    reg_metrics = engine.train_forecaster(df)

    clf_metrics = engine.train_classifier(df)

    anomalies = engine.detect_anomalies(df)

    eda_stats = compute_eda_stats(df)

    print("Pre-computing forecasts and optimizations...")
    forecast_results = build_all_forecasts(engine, df)
    optimization_results = optimize_schedule()

    # Pre-build anomalies list for API response and assistant
    anomaly_rows = anomalies[anomalies["is_anomaly"] == 1]
    anomalies_list = []
    for _, row in anomaly_rows.iterrows():
        anomalies_list.append({
            "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
            "anomaly_reason": row["anomaly_reason"],
            "global_active_power": round(float(row["global_active_power"]), 2),
            "voltage": round(float(row["voltage"]), 1)
        })

    # Pre-calculate appliance share for assistant eda context
    total_energy_kwh = (df["global_active_power"] * 1/60).sum()
    sm1_kwh = df["sub_metering_1"].sum() / 1000
    sm2_kwh = df["sub_metering_2"].sum() / 1000
    sm3_kwh = df["sub_metering_3"].sum() / 1000
    other_kwh = max(0.0, total_energy_kwh - sm1_kwh - sm2_kwh - sm3_kwh)
    
    appliance_share = {
        "HVAC/AC": round(sm3_kwh, 2),
        "Kitchen": round(sm1_kwh, 2),
        "Laundry": round(sm2_kwh, 2),
        "Other / Always On": round(other_kwh, 2)
    }

    eda_context = {
        "total_kwh": round(total_energy_kwh, 2),
        "total_cost": round(float(df["cost"].sum()), 2),
        "peak_avg_kw": round(float(df[df["peak_hour_flag"] == 1]["global_active_power"].mean()), 2),
        "offpeak_avg_kw": round(float(df[df["peak_hour_flag"] == 0]["global_active_power"].mean()), 2),
        "appliance_share": appliance_share
    }

    assistant_inst = EnergyAssistant(
        eda_stats=eda_context,
        anomalies=anomalies_list,
        optimization=optimization_results,
        forecast=forecast_results
    )

    STATE["df"] = df
    STATE["engine"] = engine
    STATE["reg_metrics"] = reg_metrics
    STATE["clf_metrics"] = clf_metrics
    STATE["anomaly_metrics"] = engine.anomaly_metrics
    STATE["anomalies"] = anomalies
    STATE["anomalies_list"] = anomalies_list
    STATE["forecast"] = forecast_results
    STATE["optimization"] = optimization_results
    STATE["assistant"] = assistant_inst
    STATE["eda_stats"] = eda_stats
    STATE["generated_at"] = datetime.now().isoformat()

    print("System Ready")


@app.on_event("startup")
def startup_event():
    bootstrap()


@app.get("/")
def root():

    return {
        "status": "running",
        "generated_at": STATE.get("generated_at")
    }


@app.get("/api/analytics")
def analytics():
    df = STATE["df"]
    
    # hourly average
    hourly_avg = df.groupby("hour")["global_active_power"].mean().round(2).to_dict()
    hourly_avg = {str(k): v for k, v in hourly_avg.items()}
    
    # day of week average
    day_of_week_avg = df.groupby("day_of_week")["global_active_power"].mean().round(2).to_dict()
    day_of_week_avg = {str(k): v for k, v in day_of_week_avg.items()}
    
    # appliance share
    total_energy_kwh = (df["global_active_power"] * 1/60).sum()
    sm1_kwh = df["sub_metering_1"].sum() / 1000
    sm2_kwh = df["sub_metering_2"].sum() / 1000
    sm3_kwh = df["sub_metering_3"].sum() / 1000
    other_kwh = max(0.0, total_energy_kwh - sm1_kwh - sm2_kwh - sm3_kwh)
    
    appliance_share = {
        "HVAC/AC": round(sm3_kwh, 2),
        "Kitchen": round(sm1_kwh, 2),
        "Laundry": round(sm2_kwh, 2),
        "Other / Always On": round(other_kwh, 2)
    }
    
    # peak vs off-peak average
    peak_avg_kw = round(float(df[df["peak_hour_flag"] == 1]["global_active_power"].mean()), 2)
    offpeak_avg_kw = round(float(df[df["peak_hour_flag"] == 0]["global_active_power"].mean()), 2)
    
    # temperature correlation
    corr = df["global_active_power"].corr(df["temperature_c"])
    temperature_correlation = round(float(corr), 2) if not np.isnan(corr) else 0.0
    
    # outlier count
    outlier_count = int(df["is_outlier"].sum())
    
    return {
        "hourly_avg": hourly_avg,
        "day_of_week_avg": day_of_week_avg,
        "appliance_share": appliance_share,
        "peak_avg_kw": peak_avg_kw,
        "offpeak_avg_kw": offpeak_avg_kw,
        "temperature_correlation": temperature_correlation,
        "outlier_count": outlier_count
    }


@app.get("/api/overview")
def overview():
    df = STATE["df"]
    anomalies_list = STATE["anomalies_list"]
    opt = STATE["optimization"]
    
    current_usage_kw = round(float(df.iloc[-1]["global_active_power"]), 2)
    current_bill_estimate = round(float(df["cost"].sum()), 2)
    
    num_days = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / (24 * 3600)
    if num_days > 0:
        predicted_bill_month = round((current_bill_estimate / num_days) * 30, 2)
    else:
        predicted_bill_month = current_bill_estimate
        
    monthly_savings_potential = opt["summary"]["monthly_savings"]
    co2_saved_kg_monthly = opt["summary"]["co2_saved_kg_monthly"]
    trees_equivalent_yearly = opt["summary"]["trees_equivalent_yearly"]
    
    green_score = int(round(100 - (df["peak_hour_flag"].mean() * 100)))
    anomaly_count = len(anomalies_list)
    
    return {
        "current_usage_kw": current_usage_kw,
        "current_bill_estimate": current_bill_estimate,
        "predicted_bill_month": predicted_bill_month,
        "monthly_savings_potential": monthly_savings_potential,
        "green_score": green_score,
        "co2_saved_kg_monthly": co2_saved_kg_monthly,
        "anomaly_count": anomaly_count,
        "trees_equivalent_yearly": trees_equivalent_yearly
    }


@app.get("/api/anomalies")
def get_anomalies():
    return {
        "count": len(STATE["anomalies_list"]),
        "anomalies": STATE["anomalies_list"]
    }


@app.get("/api/model-metrics")
def metrics():

    return {
        "forecast_model": STATE["reg_metrics"],
        "classifier_model": STATE["clf_metrics"],
        "anomaly_model": STATE["anomaly_metrics"]
    }


@app.get("/api/forecast")
def get_forecast():
    return STATE["forecast"]


@app.post("/api/predict")
def predict():

    df = STATE["df"]

    latest = df.iloc[-1]

    return {
        "predicted_power": round(
            float(latest["global_active_power"]),
            2
        )
    }


@app.post("/api/optimize")
def optimize():
    return STATE["optimization"]


from pydantic import BaseModel
from .simulator import simulate_scenario

class SimulateRequest(BaseModel):
    appliance: str
    action: str
    value: float

@app.post("/api/simulate")
def post_simulate(req: SimulateRequest):
    return simulate_scenario(STATE["df"], req.appliance, req.action, req.value)


@app.post("/api/assistant")
def assistant(payload: dict):

    query = payload.get("query", "")
    assistant_inst = STATE["assistant"]
    return assistant_inst.answer(query)