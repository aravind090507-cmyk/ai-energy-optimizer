# AI Energy Optimizer & Smart Scheduling System

An end-to-end system that predicts household energy consumption, detects usage
anomalies, classifies usage intensity, optimizes appliance schedules to cut
cost & carbon footprint, answers natural-language questions about your bill,
and presents it all in a dark-themed interactive dashboard.

## What's implemented

| Area | Status | Notes |
|---|---|---|
| Synthetic dataset generator | ✅ | 90-day hourly household data: power, voltage, sub-metering, weather, tariff |
| Data cleaning / EDA pipeline | ✅ | Interpolation, outlier tagging, peak/off-peak stats, appliance share, heatmap |
| Load forecasting (RandomForest) | ✅ | R² / RMSE / MAE + feature importances |
| Anomaly detection (IsolationForest) | ✅ | Contextual reason tags per anomaly |
| Usage classification (Low/Med/High) | ✅ | RandomForestClassifier, precision/recall/F1 |
| Multi-horizon forecasting | ✅ | Next 24h / 7d / 30d with confidence bands |
| Smart scheduling optimizer | ✅ | Heuristic peak→off-peak load shifting, ₹ + CO₂ savings |
| AI assistant | ✅ (rule-based) | Data-grounded answers; optional OpenAI upgrade via `OPENAI_API_KEY` |
| FastAPI backend + all 7 endpoints | ✅ | See below |
| React dashboard (dark glassmorphism) | ✅ | Overview, Analytics, Scheduling, Anomalies, Forecast, Assistant |
| Automated tests (pytest) | ⏳ not yet added | Manual endpoint verification done |

This covers dataset generation, preprocessing, all three ML models,
forecasting, the optimizer, the AI assistant, the full API surface, and a
working interactive dashboard — the core of the implementation plan end to
end, wired together and verified to run.

## Project structure

```
ai-energy-optimizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & routes
│   │   ├── dataset_generator.py # Synthetic household dataset
│   │   ├── data_pipeline.py     # Cleaning + EDA
│   │   ├── ml_engine.py         # Forecast / anomaly / classification models
│   │   ├── optimizer.py         # Smart scheduling engine
│   │   ├── forecasting.py       # Multi-horizon forecasts
│   │   └── ai_assistant.py      # Rule-based + optional OpenAI assistant
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Overview.jsx
    │   │   ├── Analytics.jsx
    │   │   ├── Optimization.jsx
    │   │   ├── Anomalies.jsx
    │   │   ├── Forecasting.jsx
    │   │   └── AIAssistant.jsx
    │   ├── App.jsx
    │   ├── api.js
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## Running it locally

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The first startup trains all models on a freshly generated 90-day dataset
(~10–20 seconds), then serves:

- `GET  /api/overview` — KPI summary
- `GET  /api/analytics` — EDA stats, appliance share, heatmap
- `POST /api/predict` — next-24h predictions + model metrics
- `GET  /api/anomalies` — detected anomalies with reasons
- `POST /api/optimize` — schedule optimization + savings
- `POST /api/assistant` — ask a question, body `{"query": "..."}`
- `GET  /api/forecast` — 24h / 7d / 30d forecasts

Optional: set `OPENAI_API_KEY` in your environment for the assistant to
phrase richer answers using the OpenAI API (it works fully offline without
this).

### 2. Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`). The dev
server proxies `/api/*` to `http://localhost:8000`, so run the backend
first.

### 3. Production build

```bash
cd frontend
npm run build
```

Outputs static files to `frontend/dist/`.

## Verification performed

- Ran the full pipeline (generate → clean → train all 3 models → detect
  anomalies → optimize → forecast → assistant) end to end in Python —
  no errors, sensible metrics (regressor R² ≈ 0.6–0.8, classifier
  accuracy ≈ 0.75–0.85 depending on data draw).
- Started the FastAPI server and exercised all 7 endpoints with `curl` —
  all return 200 with well-formed JSON.
- Ran `npm run build` — compiles cleanly with no JSX/CSS errors.
- Ran the Vite dev server against the live backend and confirmed the
  `/api/*` proxy returns real data from the ML engine.

## Not yet built (remaining ~40–50%)

- Automated `pytest` suite for the API
- MILP-based (vs. heuristic) optimizer for more complex constraint sets
- Persistent storage (currently in-memory, recomputed on restart)
- User-configurable appliance list from the UI (currently backend defaults)
- Deployment packaging (Docker, etc.)
