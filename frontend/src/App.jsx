import { useState } from 'react'
import Overview from './components/Overview.jsx'
import Analytics from './components/Analytics.jsx'
import Optimization from './components/Optimization.jsx'
import Anomalies from './components/Anomalies.jsx'
import Forecasting from './components/Forecasting.jsx'
import AIAssistant from './components/AIAssistant.jsx'
import Simulator from './components/Simulator.jsx'

const TABS = [
  { id: 'overview', label: 'Overview', icon: BoltIcon },
  { id: 'analytics', label: 'Analytics', icon: ChartIcon },
  { id: 'optimization', label: 'Scheduling', icon: ClockIcon },
  { id: 'anomalies', label: 'Anomalies', icon: WarnIcon },
  { id: 'forecast', label: 'Forecast', icon: TrendIcon },
  { id: 'assistant', label: 'Assistant', icon: SparkIcon },
  { id: 'simulator', label: 'What-If Simulation', icon: SimulatorIcon },
]

export default function App() {
  const [tab, setTab] = useState('overview')

  return (
    <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh', display: 'flex' }}>
      <Sidebar tab={tab} setTab={setTab} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <Topbar tab={tab} />
        <main style={{ padding: '28px 36px 60px', maxWidth: 1360, margin: '0 auto' }}>
          {tab === 'overview' && <Overview onNavigate={setTab} />}
          {tab === 'analytics' && <Analytics />}
          {tab === 'optimization' && <Optimization />}
          {tab === 'anomalies' && <Anomalies />}
          {tab === 'forecast' && <Forecasting />}
          {tab === 'assistant' && <AIAssistant />}
          {tab === 'simulator' && <Simulator />}
        </main>
      </div>
    </div>
  )
}

function Sidebar({ tab, setTab }) {
  return (
    <aside
      style={{
        width: 236,
        flexShrink: 0,
        borderRight: '1px solid var(--panel-border)',
        padding: '26px 16px',
        position: 'sticky',
        top: 0,
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '4px 10px 26px' }}>
        <div
          style={{
            width: 34, height: 34, borderRadius: 10,
            background: 'linear-gradient(135deg, var(--amber), var(--violet))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 24px rgba(245,166,35,0.35)',
          }}
        >
          <BoltIcon color="#0B0F1A" size={18} />
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 17, lineHeight: 1 }}>Volt</div>
          <div style={{ fontSize: 10.5, color: 'var(--text-low)', letterSpacing: '0.06em' }}>ENERGY OPTIMIZER</div>
        </div>
      </div>

      {TABS.map(({ id, label, icon: Icon }) => {
        const active = tab === id
        return (
          <button
            key={id}
            onClick={() => setTab(id)}
            style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 12px', borderRadius: 12, border: 'none',
              background: active ? 'rgba(255,255,255,0.06)' : 'transparent',
              color: active ? 'var(--text-hi)' : 'var(--text-mid)',
              fontSize: 14, fontWeight: active ? 600 : 500,
              textAlign: 'left', transition: 'all 0.15s ease',
              position: 'relative',
            }}
            onMouseEnter={(e) => { if (!active) e.currentTarget.style.background = 'rgba(255,255,255,0.03)' }}
            onMouseLeave={(e) => { if (!active) e.currentTarget.style.background = 'transparent' }}
          >
            {active && (
              <span style={{
                position: 'absolute', left: -16, top: '50%', transform: 'translateY(-50%)',
                width: 3, height: 18, borderRadius: 4, background: 'var(--amber)',
              }} />
            )}
            <Icon size={17} color={active ? 'var(--amber)' : 'var(--text-low)'} />
            {label}
          </button>
        )
      })}

      <div style={{ marginTop: 'auto', padding: '14px 12px', fontSize: 11, color: 'var(--text-low)', lineHeight: 1.5 }}>
        Backend: FastAPI · ML: scikit-learn
        <br />Synthetic 90-day household dataset
      </div>
    </aside>
  )
}

function Topbar({ tab }) {
  const titles = {
    overview: ['Overview', 'Live snapshot of usage, cost, and green score'],
    analytics: ['Analytics', 'Consumption patterns, appliance share, weather correlation'],
    optimization: ['Smart Scheduling', 'Shift flexible loads to the cheapest, cleanest hours'],
    anomalies: ['Anomaly Detection', 'Spikes, faults, and off-hour usage flagged automatically'],
    forecast: ['Forecasting', 'Next 24 hours, 7 days, and 30 days of predicted load'],
    assistant: ['AI Assistant', 'Ask about your bill, appliances, or savings'],
    simulator: ['What-If Scenario Simulator', 'Simulate appliance shifts and reduction percentages to evaluate savings'],
  }
  const [title, sub] = titles[tab]
  return (
    <header style={{
      position: 'sticky', top: 0, zIndex: 5, padding: '22px 36px 18px',
      background: 'linear-gradient(var(--bg-0) 60%, transparent)',
    }}>
      <div style={{ maxWidth: 1360, margin: '0 auto' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>{title}</h1>
        <p style={{ color: 'var(--text-mid)', fontSize: 13.5, marginTop: 4 }}>{sub}</p>
      </div>
    </header>
  )
}

// ---- inline icon set (no external icon lib needed) ----
function BoltIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none"><path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z" fill={color} /></svg>
}
function ChartIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2"><path d="M4 20V10M12 20V4M20 20v-7" strokeLinecap="round" /></svg>
}
function ClockIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2"><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3.5 2" strokeLinecap="round" /></svg>
}
function WarnIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2"><path d="M12 3l10 18H2L12 3z" strokeLinejoin="round" /><path d="M12 10v4M12 17.5v.1" strokeLinecap="round" /></svg>
}
function TrendIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2"><path d="M3 17l6-6 4 4 8-8" strokeLinecap="round" strokeLinejoin="round" /><path d="M15 7h6v6" strokeLinecap="round" strokeLinejoin="round" /></svg>
}
function SparkIcon({ size = 18, color = 'currentColor' }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none"><path d="M12 2l1.8 5.6L19 9l-5.2 1.6L12 16l-1.8-5.4L5 9l5.2-1.4L12 2z" fill={color} /></svg>
}
function SimulatorIcon({ size = 18, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
      <path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 12h6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export { BoltIcon, ChartIcon, ClockIcon, WarnIcon, TrendIcon, SparkIcon, SimulatorIcon }
