import { useState } from 'react'
import { api } from '../api.js'
import { ErrorNote } from './Overview.jsx'

export default function Simulator() {
  const [appliance, setAppliance] = useState('HVAC/AC')
  const [action, setAction] = useState('shift_hours')
  const [value, setValue] = useState(action === 'shift_hours' ? -2 : 30)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)

  const handleActionChange = (newAction) => {
    setAction(newAction)
    setValue(newAction === 'shift_hours' ? -2 : 30)
  }

  const handleSubmit = (e) => {
    e?.preventDefault()
    setLoading(true)
    setError(null)
    api.simulate(appliance, action, parseFloat(value))
      .then((res) => {
        setResults(res)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 24, alignItems: 'start' }}>
      {/* Left: Input Panel */}
      <div className="glass" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 18, background: 'linear-gradient(135deg, var(--text-hi), var(--text-mid))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Simulation Configuration
        </h3>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Select Appliance */}
          <div>
            <label style={{ display: 'block', fontSize: 12.5, color: 'var(--text-mid)', fontWeight: 600, marginBottom: 8 }}>
              Select Appliance
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              {['Kitchen', 'Laundry', 'HVAC/AC'].map((app) => {
                const active = appliance === app
                const icons = { Kitchen: '🍳', Laundry: '🧺', 'HVAC/AC': '❄️' }
                return (
                  <button
                    key={app}
                    type="button"
                    onClick={() => setAppliance(app)}
                    style={{
                      padding: '12px 8px',
                      borderRadius: 12,
                      border: active ? '1px solid var(--amber)' : '1px solid var(--panel-border)',
                      background: active ? 'var(--amber-dim)' : 'rgba(255,255,255,0.02)',
                      color: active ? 'var(--text-hi)' : 'var(--text-mid)',
                      fontSize: 13,
                      fontWeight: 600,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 6,
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <span style={{ fontSize: 20 }}>{icons[app]}</span>
                    {app}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Select Action */}
          <div>
            <label style={{ display: 'block', fontSize: 12.5, color: 'var(--text-mid)', fontWeight: 600, marginBottom: 8 }}>
              Simulation Action
            </label>
            <div style={{ display: 'flex', background: 'rgba(0,0,0,0.2)', padding: 4, borderRadius: 10, border: '1px solid var(--panel-border)' }}>
              <button
                type="button"
                onClick={() => handleActionChange('shift_hours')}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: 8,
                  border: 'none',
                  background: action === 'shift_hours' ? 'rgba(255,255,255,0.08)' : 'transparent',
                  color: action === 'shift_hours' ? 'var(--text-hi)' : 'var(--text-low)',
                  fontSize: 13,
                  fontWeight: 600,
                  transition: 'all 0.15s ease',
                }}
              >
                ⏰ Shift Hours
              </button>
              <button
                type="button"
                onClick={() => handleActionChange('reduce_pct')}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: 8,
                  border: 'none',
                  background: action === 'reduce_pct' ? 'rgba(255,255,255,0.08)' : 'transparent',
                  color: action === 'reduce_pct' ? 'var(--text-hi)' : 'var(--text-low)',
                  fontSize: 13,
                  fontWeight: 600,
                  transition: 'all 0.15s ease',
                }}
              >
                📉 Reduce Usage (%)
              </button>
            </div>
          </div>

          {/* Parameter Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12.5, color: 'var(--text-mid)', fontWeight: 600, marginBottom: 8 }}>
              <span>{action === 'shift_hours' ? 'Shift Hours' : 'Reduction Percentage'}</span>
              <span className="mono" style={{ color: action === 'shift_hours' ? 'var(--amber)' : 'var(--cyan)' }}>
                {action === 'shift_hours' 
                  ? (value > 0 ? `+${value} hours` : `${value} hours`) 
                  : `${value}%`}
              </span>
            </div>
            
            {action === 'shift_hours' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <input
                  type="range"
                  min="-12"
                  max="12"
                  step="1"
                  value={value}
                  onChange={(e) => setValue(parseInt(e.target.value))}
                  style={{
                    width: '100%',
                    accentColor: 'var(--amber)',
                    background: 'var(--bg-2)',
                    height: 6,
                    borderRadius: 3,
                    outline: 'none',
                  }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-low)' }}>
                  <span>-12 hrs (Earlier)</span>
                  <span>0 (No shift)</span>
                  <span>+12 hrs (Later)</span>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={value}
                  onChange={(e) => setValue(parseInt(e.target.value))}
                  style={{
                    width: '100%',
                    accentColor: 'var(--cyan)',
                    background: 'var(--bg-2)',
                    height: 6,
                    borderRadius: 3,
                    outline: 'none',
                  }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-low)' }}>
                  <span>0% (No reduction)</span>
                  <span>50%</span>
                  <span>100% (Complete shutoff)</span>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 16px',
              borderRadius: 12,
              border: 'none',
              background: 'linear-gradient(135deg, var(--amber), var(--violet))',
              color: '#0B0F1A',
              fontSize: 14,
              fontWeight: 700,
              boxShadow: '0 4px 20px rgba(245,166,35,0.25)',
              transition: 'transform 0.1s ease',
              marginTop: 10,
            }}
            onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.98)'}
            onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            {loading ? 'Running simulation...' : '⚡ Run Scenario Simulation'}
          </button>
        </form>
      </div>

      {/* Right: Results Panel */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {error && <ErrorNote msg={error} />}

        {!results && !loading && (
          <div className="glass" style={{ padding: 40, textAlign: 'center', color: 'var(--text-low)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 40 }}>💡</span>
            <div>
              <h4 style={{ color: 'var(--text-mid)', fontSize: 14, fontWeight: 600 }}>Ready to Simulate</h4>
              <p style={{ fontSize: 12, color: 'var(--text-low)', marginTop: 4 }}>Configure the parameters on the left and run the simulation to see potential cost and carbon impacts.</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="glass" style={{ padding: 40, textAlign: 'center', color: 'var(--text-low)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              border: '2px solid rgba(255,255,255,0.1)',
              borderTopColor: 'var(--amber)',
              animation: 'spin 1s linear infinite'
            }} />
            <style>{`
              @keyframes spin {
                to { transform: rotate(360deg); }
              }
            `}</style>
            <div>
              <h4 style={{ color: 'var(--text-mid)', fontSize: 14, fontWeight: 600 }}>Simulating Scenario</h4>
              <p style={{ fontSize: 12, color: 'var(--text-low)', marginTop: 4 }}>Analyzing 90-day active power load curves and grid factors...</p>
            </div>
          </div>
        )}

        {results && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Top Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="glass" style={{ padding: 18, position: 'relative' }}>
                <span style={{ position: 'absolute', top: 12, right: 14, fontSize: 16 }}>💰</span>
                <div style={{ fontSize: 12, color: 'var(--text-mid)', fontWeight: 500 }}>Cost Savings</div>
                <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: results.cost_savings >= 0 ? 'var(--green)' : 'var(--red)', marginTop: 6 }}>
                  {results.cost_savings >= 0 ? `₹${results.cost_savings.toLocaleString('en-IN')}` : `-₹${Math.abs(results.cost_savings).toLocaleString('en-IN')}`}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-low)', marginTop: 4 }}>
                  Estimated bill change
                </div>
              </div>

              <div className="glass" style={{ padding: 18, position: 'relative' }}>
                <span style={{ position: 'absolute', top: 12, right: 14, fontSize: 16 }}>🌍</span>
                <div style={{ fontSize: 12, color: 'var(--text-mid)', fontWeight: 500 }}>CO₂ Emissions Savings</div>
                <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: results.co2_savings_kg >= 0 ? 'var(--violet)' : 'var(--red)', marginTop: 6 }}>
                  {results.co2_savings_kg.toFixed(2)} kg
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-low)', marginTop: 4 }}>
                  Carbon footprint offset
                </div>
              </div>
            </div>

            {/* Comparison Details Card */}
            <div className="glass" style={{ padding: 20 }}>
              <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Details & Visual Comparison</h4>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {/* Cost Comparison bar */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-mid)', marginBottom: 6 }}>
                    <span>Total Cost comparison</span>
                    <span className="mono">₹{results.cost_before.toLocaleString()} → ₹{results.cost_after.toLocaleString()}</span>
                  </div>
                  <div style={{ height: 24, background: 'rgba(0,0,0,0.2)', borderRadius: 6, overflow: 'hidden', display: 'flex', border: '1px solid var(--panel-border)' }}>
                    <div style={{
                      width: `${Math.min(100, Math.max(0, (results.cost_after / results.cost_before) * 100))}%`,
                      background: results.cost_savings >= 0 ? 'linear-gradient(90deg, var(--green-dim), var(--green))' : 'linear-gradient(90deg, var(--red-dim), var(--red))',
                      transition: 'width 0.5s ease',
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: 8,
                      fontSize: 10,
                      color: '#0B0F1A',
                      fontWeight: 700
                    }}>
                      New ({( (results.cost_after / results.cost_before) * 100 ).toFixed(0)}%)
                    </div>
                  </div>
                </div>

                {/* CO2 Comparison bar */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-mid)', marginBottom: 6 }}>
                    <span>CO₂ Emissions comparison</span>
                    <span className="mono">{results.co2_before_kg.toFixed(0)} kg → {results.co2_after_kg.toFixed(0)} kg</span>
                  </div>
                  <div style={{ height: 24, background: 'rgba(0,0,0,0.2)', borderRadius: 6, overflow: 'hidden', display: 'flex', border: '1px solid var(--panel-border)' }}>
                    <div style={{
                      width: `${Math.min(100, Math.max(0, (results.co2_after_kg / results.co2_before_kg) * 100))}%`,
                      background: results.co2_savings_kg >= 0 ? 'linear-gradient(90deg, var(--violet-dim), var(--violet))' : 'linear-gradient(90deg, var(--red-dim), var(--red))',
                      transition: 'width 0.5s ease',
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: 8,
                      fontSize: 10,
                      color: '#0B0F1A',
                      fontWeight: 700
                    }}>
                      New ({( (results.co2_after_kg / results.co2_before_kg) * 100 ).toFixed(0)}%)
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Environmental Impact card */}
            {results.co2_savings_kg > 0 && (
              <div style={{
                display: 'flex', gap: 14, alignItems: 'center', padding: '14px 18px',
                borderRadius: 16, background: 'linear-gradient(90deg, rgba(74,222,128,0.08), rgba(53,212,224,0.04))',
                border: '1px solid rgba(74,222,128,0.15)',
              }}>
                <div style={{ fontSize: 24 }}>🌱</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>
                    Equivalent to absorbing carbon of {((results.co2_savings_kg * 12) / 21).toFixed(1)} mature trees!
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-mid)', marginTop: 2 }}>
                    Based on standard Indian grid factors and tree absorption metrics.
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
