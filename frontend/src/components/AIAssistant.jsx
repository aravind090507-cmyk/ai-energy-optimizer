import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'

const SUGGESTIONS = [
  'Why is my bill high?',
  'How can I lower AC costs?',
  'What anomalies were detected?',
  'How much can I save with scheduling?',
  'What does tomorrow look like?',
]

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hi, I'm your energy assistant. Ask me about your bill, appliances, anomalies, or forecasts — I'll answer using your actual usage data." },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (q) => {
    const query = (q ?? input).trim()
    if (!query || busy) return
    setMessages((m) => [...m, { role: 'user', text: query }])
    setInput('')
    setBusy(true)
    try {
      const res = await api.assistant(query)
      setMessages((m) => [...m, { role: 'assistant', text: res.answer, source: res.source }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', text: `Sorry, I couldn't reach the backend (${e.message}).` }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="glass" style={{ padding: 0, display: 'flex', flexDirection: 'column', height: 560, overflow: 'hidden' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '22px 24px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        {messages.map((m, i) => <Bubble key={i} {...m} />)}
        {busy && <Bubble role="assistant" text="…" typing />}
        <div ref={endRef} />
      </div>

      <div style={{ padding: '10px 24px 0', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            style={{
              fontSize: 12, padding: '6px 12px', borderRadius: 16,
              border: '1px solid var(--panel-border)', background: 'rgba(255,255,255,0.02)',
              color: 'var(--text-mid)',
            }}
          >
            {s}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); send() }}
        style={{ display: 'flex', gap: 10, padding: 20, borderTop: '1px solid var(--panel-border)', marginTop: 16 }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your energy usage…"
          style={{
            flex: 1, background: 'rgba(255,255,255,0.03)', border: '1px solid var(--panel-border)',
            borderRadius: 12, padding: '11px 14px', color: 'var(--text-hi)', fontSize: 13.5, outline: 'none',
          }}
        />
        <button
          type="submit"
          disabled={busy}
          style={{
            padding: '0 20px', borderRadius: 12, border: 'none',
            background: 'linear-gradient(135deg, var(--amber), var(--violet))',
            color: '#0B0F1A', fontWeight: 700, fontSize: 13.5,
          }}
        >
          Ask
        </button>
      </form>
    </div>
  )
}

function Bubble({ role, text, source, typing }) {
  const isUser = role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      <div
        style={{
          maxWidth: '72%', padding: '11px 15px', borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          background: isUser ? 'linear-gradient(135deg, rgba(245,166,35,0.18), rgba(155,135,245,0.18))' : 'rgba(255,255,255,0.04)',
          border: `1px solid ${isUser ? 'rgba(245,166,35,0.25)' : 'var(--panel-border)'}`,
          fontSize: 13.5, lineHeight: 1.5, color: 'var(--text-hi)',
        }}
      >
        {typing ? <TypingDots /> : text}
        {source === 'openai' && !isUser && (
          <div style={{ fontSize: 10, color: 'var(--text-low)', marginTop: 4 }}>via OpenAI</div>
        )}
      </div>
    </div>
  )
}

function TypingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: 3 }}>
      {[0, 1, 2].map((i) => (
        <span key={i} style={{
          width: 5, height: 5, borderRadius: '50%', background: 'var(--text-mid)',
          animation: `pulse 1.2s ${i * 0.15}s infinite ease-in-out`,
        }} />
      ))}
      <style>{`@keyframes pulse { 0%,80%,100% { opacity: 0.3 } 40% { opacity: 1 } }`}</style>
    </span>
  )
}
