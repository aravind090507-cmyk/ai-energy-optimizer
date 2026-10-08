import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Loading, ErrorNote } from './Overview.jsx'

export default function Optimization() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [running, setRunning] = useState(false)

  const load = () => {
    setRunning(true)
    api.optimize().then((d) => { setData(d); setRunning(false) }).catch((e) => { setError(e.message); setRunning(false) })
  }

  useEffect(load, [])

  if (error) return <ErrorNote msg={error} />
  if (!data) return <Loading />

  const s = data.summary

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginBottom: 20 }}>
        <StatCard label="Weekly Savings" value={`₹${s.weekly_savings}`} accent="green" />
        <StatCard label="Monthly Savings" value={`₹${s.monthly_savings}`} accent="amber" />
        <StatCard label="CO₂ Cut / Month" value={`${s.co2_saved_kg_monthly} kg`} accent="violet" />
        <StatCard label="Trees Equivalent" value={`${s.trees_equivalent_yearly}/yr`} accent="cyan" />
      </div>

      <div className="glass" style={{ padding: 22, marginBottom: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontSize: 15 }}>Original vs. AI-Optimized Schedule</h3>
            <p style={{ fontSize: 12, color: 'var(--text-mid)', marginTop: 3 }}>Flexible appliances shifted from evening peak into cheaper windows</p>
          </div>
          <button
            onClick={load}
            disabled={running}
            style={{
              padding: '8px 16px', borderRadius: 10, border: '1px solid var(--panel-border-hi)',
              background: 'rgba(245,166,35,0.1)', color: 'var(--amber)', fontSize: 13, fontWeight: 600,
            }}
          >
            {running ? 'Optimizing…' : '↻ Re-run optimizer'}
          </button>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-low)', fontSize: 11.5, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                <th style={th}>Appliance</th>
                <th style={th}>Weekly kWh</th>
                <th style={th}>Original Hour</th>
                <th style={th}>Optimized Hour</th>
                <th style={th}>Tariff Change</th>
                <th style={th}>Weekly Savings</th>
              </tr>
            </thead>
            <tbody>
              {data.schedule.map((row) => (
                <tr key={row.appliance} style={{ borderTop: '1px solid var(--panel-border)' }}>
                  <td style={{ ...td, fontWeight: 600 }}>{row.appliance}</td>
                  <td className="mono" style={td}>{(row.kwh_per_cycle * row.cycles_per_week).toFixed(1)}</td>
                  <td style={td}>
                    <TimeBadge hour={row.original_hour} tariff={row.original_tariff} accent="red" />
                  </td>
                  <td style={td}>
                    <TimeBadge hour={row.optimized_hour} tariff={row.optimized_tariff} accent="green" />
                  </td>
                  <td className="mono" style={{ ...td, color: 'var(--text-mid)' }}>
                    ₹{row.original_tariff} → ₹{row.optimized_tariff}
                  </td>
                  <td className="mono" style={{ ...td, color: 'var(--green)', fontWeight: 700 }}>₹{row.weekly_savings}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{
        display: 'flex', gap: 16, alignItems: 'center', padding: '18px 22px',
        borderRadius: 20, background: 'linear-gradient(90deg, rgba(74,222,128,0.10), rgba(53,212,224,0.06))',
        border: '1px solid rgba(74,222,128,0.2)',
      }}>
        <div style={{ fontSize: 28 }}>🌍</div>
        <div>
          <div style={{ fontSize: 13.5, fontWeight: 600 }}>
            Shifting {s.shifted_kwh_weekly} kWh/week off-peak cuts ~{s.co2_saved_kg_monthly} kg CO₂ monthly
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-mid)', marginTop: 2 }}>
            That's roughly equivalent to {s.trees_equivalent_yearly} mature trees absorbing carbon for a year.
          </div>
        </div>
      </div>
    </div>
  )
}

function TimeBadge({ hour, tariff, accent }) {
  const label = `${hour.toString().padStart(2, '0')}:00`
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 10px', borderRadius: 20,
      background: `var(--${accent}-dim)`, color: `var(--${accent})`, fontSize: 12.5, fontFamily: 'var(--font-mono)',
    }}>
      {label}
    </span>
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

const th = { padding: '8px 10px' }
const td = { padding: '10px 10px' }
