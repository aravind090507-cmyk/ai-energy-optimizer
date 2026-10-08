"""
ai_assistant.py
Data-grounded conversational agent. Uses a rule-based / statistical engine
by default (fully offline). If OPENAI_API_KEY is set in the environment,
it will optionally use the OpenAI API to phrase richer answers around the
same computed facts.
"""

import os
import re

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _try_openai_completion(prompt: str) -> str | None:
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise home-energy assistant. "
                                               "Use ONLY the facts given in the prompt."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=220,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


class EnergyAssistant:
    """Answers natural-language queries grounded in the computed dataset context."""

    def __init__(self, eda_stats: dict, anomalies: list, optimization: dict, forecast: dict):
        self.eda = eda_stats
        self.anomalies = anomalies
        self.optimization = optimization
        self.forecast = forecast

    def answer(self, query: str) -> dict:
        q = query.lower().strip()

        if re.search(r"\bac\b|hvac|cooling|air.?condition", q):
            fact = self._ac_explanation()
        elif re.search(r"anomal|spike|unusual|weird", q):
            fact = self._anomaly_explanation()
        elif re.search(r"save|saving|optimi[sz]e|reduce", q):
            fact = self._savings_explanation()
        elif re.search(r"forecast|predict|tomorrow|next week|next month", q):
            fact = self._forecast_explanation()
        elif re.search(r"peak|off.?hour|off.?peak|running.*peak", q):
            fact = self._peak_hour_explanation()
        elif re.search(r"bill|cost|expensive|why.*high", q):
            fact = self._bill_explanation()
        else:
            fact = self._general_summary()

        llm_answer = _try_openai_completion(f"Facts: {fact}\n\nUser question: {query}\nAnswer in 2-3 sentences.")
        return {
            "query": query,
            "answer": llm_answer or fact,
            "source": "openai" if llm_answer else "rule_based",
        }

    # ---- fact generators, each grounded in computed data ----
    def _bill_explanation(self) -> str:
        share = self.eda.get("appliance_share", {})
        top = max(share, key=share.get) if share else "your appliances"
        return (f"Your total estimated usage is {self.eda.get('total_kwh', 0)} kWh "
                f"costing approximately ₹{self.eda.get('total_cost', 0)}. "
                f"{top} is your largest contributor at {share.get(top, 0)} kWh. "
                f"Average peak-hour draw ({self.eda.get('peak_avg_kw', 0)} kW) is "
                f"{'higher' if self.eda.get('peak_avg_kw',0) > self.eda.get('offpeak_avg_kw',0) else 'similar to'} "
                f"off-peak draw ({self.eda.get('offpeak_avg_kw', 0)} kW), and peak tariffs are more expensive.")

    def _ac_explanation(self) -> str:
        share = self.eda.get("appliance_share", {})
        hvac = share.get("HVAC/AC", 0)
        total = sum(share.values()) or 1
        pct = round(100 * hvac / total, 1)
        return (f"HVAC/AC accounts for {hvac} kWh, about {pct}% of your total consumption. "
                f"Running the AC during off-peak night hours (10 PM–6 AM, ₹5.0/kWh) instead of "
                f"the evening peak (6–10 PM, ₹10.5/kWh) can roughly halve its cost.")

    def _anomaly_explanation(self) -> str:
        n = len(self.anomalies)
        if n == 0:
            return "No significant usage anomalies were detected in the analyzed period."
        sample = self.anomalies[:3]
        details = "; ".join(f"{a['timestamp']} ({a['anomaly_reason']})" for a in sample)
        return f"{n} anomalies were detected. Examples: {details}."

    def _peak_hour_explanation(self) -> str:
        return (f"During peak hours (6–10 PM), average draw is {self.eda.get('peak_avg_kw', 0)} kW, "
                f"billed at ₹10.5/kWh — the most expensive tariff band. Shifting flexible loads "
                f"like laundry and water heating out of this window is the single biggest lever "
                f"for reducing your bill.")

    def _savings_explanation(self) -> str:
        summary = self.optimization.get("summary", {})
        return (f"The optimizer can save approximately ₹{summary.get('monthly_savings', 0)} per month "
                f"by shifting flexible appliances to cheaper hours, cutting about "
                f"{summary.get('co2_saved_kg_monthly', 0)} kg CO₂ monthly "
                f"(~{summary.get('trees_equivalent_yearly', 0)} trees/year equivalent).")

    def _forecast_explanation(self) -> str:
        nxt = self.forecast.get("next_24h", [])
        if not nxt:
            return "Forecast data is not yet available."
        peak_point = max(nxt, key=lambda r: r["predicted_kw"])
        return (f"Over the next 24 hours, predicted load peaks at {peak_point['predicted_kw']} kW "
                f"around {peak_point['timestamp'][11:16]}. Plan flexible usage away from that window.")

    def _general_summary(self) -> str:
        return (f"You've used {self.eda.get('total_kwh', 0)} kWh (₹{self.eda.get('total_cost', 0)}) "
                f"in the analyzed period, with {len(self.anomalies)} anomalies detected. "
                f"Ask me about your bill, AC usage, anomalies, peak hours, savings, or forecasts.")
