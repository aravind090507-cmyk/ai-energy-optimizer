import { useEffect, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { api } from '../api.js'

export default function Overview({ onNavigate }) {
  const [data, setData] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([api.overview(), api.forecast()])
      .then(([ov, fc]) => { setData(ov); setForecast(fc) })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorNote msg={error} />
  if (!data) return <Loading />

  const kpis = [
    { label: 'Current Draw', value: `${data.current_usage_kw} kW`, accent: 'cyan', icon: '⚡' },
    { label: 'Bill (period)', value: `₹${data.current_bill_estimate.toLocaleString('en-IN')}`, accent: 'amber', icon: '₹' },
    { label: 'Predicted / Month', value: `₹${data.predicted_bill_month.toLocaleString('en-IN')}`, accent: 'amber', icon: '📈' },
    { label: 'Savings Potential', value: `₹${data.monthly_savings_potential.toLocaleString('en-IN')}/mo`, accent: 'green', icon: '💰' },
    { label: 'Green Score', value: `${data.green_score}/100`, accent: 'green', icon: '🌿' },
    { label: 'CO₂ Saved', value: `${data.co2_saved_kg_monthly} kg/mo`, accent: 'violet', icon: '🌍' },
  ]

  const chartData = (forecast?.next_24h || []).map((r) => ({
    hour: r.timestamp.slice(11, 16),
    kw: r.predicted_kw,
    upper: r.upper,
    lower: r.lower,
  }))

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 14, marginBottom: 22 }}>
        {kpis.map((k) => <KpiCard key={k.label} {...k} />)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 16 }}>
        <div className="glass" style={{ padding: 22 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
            <h3 style={{ fontSize: 15 }}>Next 24-Hour Load Prediction</h3>
            <span style={{ fontSize: 11.5, color: 'var(--text-low)' }}>{data.anomaly_count} anomalies this period</span>
          </div>
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={chartData} margin={{ left: -18, right: 8 }}>
              <defs>
                <linearGradient id="kwGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--cyan)" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="var(--cyan)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="hour" stroke="var(--text-low)" fontSize={11} tickLine={false} axisLine={false} interval={2} />
              <YAxis stroke="var(--text-low)" fontSize={11} tickLine={false} axisLine={false} width={36} />
              <Tooltip content={<ChartTooltip />} />
              <Area type="monotone" dataKey="upper" stroke="none" fill="var(--cyan)" fillOpacity={0.06} />
              <Area type="monotone" dataKey="kw" stroke="var(--cyan)" strokeWidth={2} fill="url(#kwGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass" style={{ padding: 22, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <h3 style={{ fontSize: 15 }}>Quick Actions</h3>
          <QuickAction
            title="Run scheduling optimizer"
            desc="Shift flexible loads out of peak tariff hours"
            onClick={() => onNavigate('optimization')}
            accent="amber"
          />
          <QuickAction
            title="Review anomalies"
            desc={`${data.anomaly_count} unusual readings flagged`}
            onClick={() => onNavigate('anomalies')}
            accent="red"
          />
          <QuickAction
            title="Ask the AI assistant"
            desc="e.g. “Why is my bill high this month?”"
            onClick={() => onNavigate('assistant')}
            accent="violet"
          />
          <div style={{
            marginTop: 'auto', padding: 14, borderRadius: 12,
            background: 'var(--green-dim)', border: '1px solid rgba(74,222,128,0.25)',
          }}>
            <div style={{ fontSize: 12, color: 'var(--green)', fontWeight: 600, marginBottom: 4 }}>Equivalent impact</div>
            <div style={{ fontSize: 13, color: 'var(--text-mid)' }}>≈ {data.trees_equivalent_yearly} trees planted / year</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ label, value, accent, icon }) {
  return (
    <div className="glass" style={{ padding: '16px 18px', position: 'relative', overflow: 'hidden' }}>
      <div style={{
        position: 'absolute', top: -20, right: -20, width: 70, height: 70, borderRadius: '50%',
        background: `var(--${accent})`, opacity: 0.12, filter: 'blur(10px)',
      }} />
      <div style={{ fontSize: 18, marginBottom: 8 }}>{icon}</div>
      <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-hi)' }}>{value}</div>
      <div style={{ fontSize: 12, color: 'var(--text-mid)', marginTop: 3 }}>{label}</div>
    </div>
  )
}

function QuickAction({ title, desc, onClick, accent }) {
  return (
    <button
      onClick={onClick}
      style={{
        textAlign: 'left', border: `1px solid var(--panel-border)`, background: 'rgba(255,255,255,0.02)',
        borderRadius: 12, padding: '12px 14px', color: 'var(--text-hi)',
        display: 'flex', flexDirection: 'column', gap: 3, transition: 'border-color 0.15s',
      }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = `var(--${accent})`}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--panel-border)'}
    >
      <span style={{ fontSize: 13.5, fontWeight: 600 }}>{title}</span>
      <span style={{ fontSize: 11.5, color: 'var(--text-mid)' }}>{desc}</span>
    </button>
  )
}

export function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass" style={{ padding: '8px 12px', fontSize: 12 }}>
      <div style={{ color: 'var(--text-low)', marginBottom: 2 }}>{label}</div>
      {payload.filter(p => p.dataKey === 'kw' || p.dataKey === 'predicted_kw').map((p) => (
        <div key={p.dataKey} className="mono" style={{ color: 'var(--cyan)' }}>{p.value} kW</div>
      ))}
    </div>
  )
}

export function Loading() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300, color: 'var(--text-low)', fontSize: 13 }}>
      Loading data from the ML engine…
    </div>
  )
}

export function ErrorNote({ msg }) {
  return (
    <div className="glass" style={{ padding: 20, color: 'var(--red)', fontSize: 13 }}>
      Couldn't reach the API ({msg}). Make sure the backend is running on port 8000.
    </div>
  )
}
