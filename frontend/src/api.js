const BASE = '/api'

async function handle(res) {
  if (!res.ok) throw new Error(`Request failed: ${res.status}`)
  return res.json()
}

export const api = {
  overview: () => fetch(`${BASE}/overview`).then(handle),
  analytics: () => fetch(`${BASE}/analytics`).then(handle),
  predict: () => fetch(`${BASE}/predict`, { method: 'POST' }).then(handle),
  anomalies: () => fetch(`${BASE}/anomalies`).then(handle),
  optimize: () => fetch(`${BASE}/optimize`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}),
  }).then(handle),
  simulate: (appliance, action, value) => fetch(`${BASE}/simulate`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ appliance, action, value }),
  }).then(handle),
  forecast: () => fetch(`${BASE}/forecast`).then(handle),
  assistant: (query) => fetch(`${BASE}/assistant`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }),
  }).then(handle),
  modelMetrics: () => fetch(`${BASE}/model-metrics`).then(handle),
}
