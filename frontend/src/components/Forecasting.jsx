import { useEffect, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Line, ComposedChart } from 'recharts'
import { api } from '../api.js'
import { Loading, ErrorNote } from './Overview.jsx'

const HORIZONS = [
  { id: 'next_24h', label: '24 Hours', fmt: (t) => t.slice(11, 16) },
  { id: 'next_7d', label: '7 Days', fmt: (t) => t.slice(5, 16).replace('T', ' ') },
  { id: 'next_30d', label: '30 Days', fmt: (t) => t.slice(5, 10) },
]

export default function Forecasting() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [horizon, setHorizon] = useState('next_24h')

  useEffect(() => {
    api.forecast().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorNote msg={error} />
  if (!data) return <Loading />

  const cfg = HORIZONS.find((h) => h.id === horizon)
  const chartData = data[horizon].map((r) => ({
    t: cfg.fmt(r.timestamp),
    predicted: r.predicted_kw,
    band: [r.lower, r.upper],
  }))

  const avg = (chartData.reduce((s, r) => s + r.predicted, 0) / chartData.length).toFixed(2)
  const peak = Math.max(...chartData.map((r) => r.predicted)).toFixed(2)

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 18 }}>
        {HORIZONS.map((h) => (
          <button
            key={h.id}
            onClick={() => setHorizon(h.id)}
            style={{
              padding: '8px 16px', borderRadius: 20, fontSize: 13, fontWeight: 600,
              border: `1px solid ${horizon === h.id ? 'var(--violet)' : 'var(--panel-border)'}`,
              background: horizon === h.id ? 'var(--violet-dim)' : 'transparent',
              color: horizon === h.id ? 'var(--violet)' : 'var(--text-mid)',
            }}
          >
            {h.label}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 18 }}>
        <StatCard label="Avg Predicted Load" value={`${avg} kW`} accent="cyan" />
        <StatCard label="Peak Predicted Load" value={`${peak} kW`} accent="amber" />
        <StatCard label="Data Points" value={chartData.length} accent="violet" />
      </div>

      <div className="glass" style={{ padding: 22 }}>
        <h3 style={{ fontSize: 15, marginBottom: 14 }}>Predicted Load — {cfg.label}</h3>
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={chartData} margin={{ left: -18, right: 8 }}>
            <defs>
              <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--violet)" stopOpacity={0.35} />
                <stop offset="100%" stopColor="var(--violet)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="t" stroke="var(--text-low)" fontSize={10.5} tickLine={false} axisLine={false}
              interval={Math.max(0, Math.floor(chartData.length / 10))} />
            <YAxis stroke="var(--text-low)" fontSize={11} tickLine={false} axisLine={false} width={36} />
            <Tooltip content={<ForecastTooltip />} />
            <Area type="monotone" dataKey="band" stroke="none" fill="url(#bandGrad)" />
            <Line type="monotone" dataKey="predicted" stroke="var(--violet)" strokeWidth={2.5} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 16, fontSize: 11.5, color: 'var(--text-mid)', marginTop: 8 }}>
          <span><i style={{ display: 'inline-block', width: 14, height: 3, background: '#9B87F5', borderRadius: 2, marginRight: 6 }} />Predicted load</span>
          <span><i style={{ display: 'inline-block', width: 14, height: 8, background: 'rgba(155,135,245,0.25)', borderRadius: 2, marginRight: 6 }} />95% confidence band</span>
        </div>
      </div>
    </div>
  )
}

function ForecastTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const p = payload.find((x) => x.dataKey === 'predicted')
  if (!p) return null
  return (
    <div className="glass" style={{ padding: '8px 12px', fontSize: 12 }}>
      <div style={{ color: 'var(--text-low)', marginBottom: 2 }}>{label}</div>
      <div className="mono" style={{ color: 'var(--violet)' }}>{p.value} kW</div>
    </div>
  )
}

function StatCard({ label, value, accent }) {
  return (
    <div className="glass" style={{ padding: '14px 16px' }}>
      <div className="mono" style={{ fontSize: 19, fontWeight: 700, color: `var(--${accent})` }}>{value}</div>
      <div style={{ fontSize: 11.5, color: 'var(--text-mid)', marginTop: 3 }}>{label}</div>
    </div>
  )
}
