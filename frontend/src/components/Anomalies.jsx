import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Loading, ErrorNote } from './Overview.jsx'

export default function Anomalies() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.anomalies().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorNote msg={error} />
  if (!data) return <Loading />

  return (
    <div>
      <div className="glass" style={{ padding: '16px 22px', marginBottom: 18, display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{
          width: 44, height: 44, borderRadius: 12, background: 'var(--red-dim)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
        }}>⚠️</div>
        <div>
          <div style={{ fontSize: 19, fontWeight: 700 }}>{data.count} anomalies detected</div>
          <div style={{ fontSize: 12.5, color: 'var(--text-mid)' }}>Flagged via Isolation Forest across the analyzed period</div>
        </div>
      </div>

      <div className="glass" style={{ padding: 6 }}>
        {data.anomalies.length === 0 && (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-mid)', fontSize: 13 }}>No anomalies to show.</div>
        )}
        {data.anomalies.map((a, i) => (
          <div
            key={i}
            style={{
              display: 'flex', gap: 16, alignItems: 'center', padding: '14px 18px',
              borderBottom: i < data.anomalies.length - 1 ? '1px solid var(--panel-border)' : 'none',
            }}
          >
            <div style={{
              width: 8, height: 8, borderRadius: '50%', background: 'var(--red)', flexShrink: 0,
              boxShadow: '0 0 10px var(--red)',
            }} />
            <div style={{ width: 150, flexShrink: 0 }}>
              <div className="mono" style={{ fontSize: 12.5, color: 'var(--text-hi)' }}>{a.timestamp.slice(0, 16)}</div>
            </div>
            <div style={{ flex: 1, fontSize: 13, color: 'var(--text-mid)' }}>{a.anomaly_reason}</div>
            <div className="mono" style={{ fontSize: 13, color: 'var(--amber)', fontWeight: 600, width: 80, textAlign: 'right' }}>
              {a.global_active_power} kW
            </div>
            <div className="mono" style={{ fontSize: 12, color: 'var(--text-low)', width: 90, textAlign: 'right' }}>
              {a.voltage} V
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
