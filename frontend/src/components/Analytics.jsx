import { useEffect, useState, Fragment } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend } from 'recharts'
import { api } from '../api.js'
import { Loading, ErrorNote, ChartTooltip } from './Overview.jsx'

const COLORS = ['var(--amber)', 'var(--cyan)', 'var(--violet)', 'var(--green)']
const HEX = { 'var(--amber)': '#F5A623', 'var(--cyan)': '#35D4E0', 'var(--violet)': '#9B87F5', 'var(--green)': '#4ADE80' }

export default function Analytics() {
  const [data, setData] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState(null)
  const [selectedCm, setSelectedCm] = useState('classifier')

  useEffect(() => {
    Promise.all([api.analytics(), api.modelMetrics()])
      .then(([analyticsData, metricsData]) => {
        setData(analyticsData)
        setMetrics(metricsData)
      })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorNote msg={error} />
  if (!data) return <Loading />

  const hourly = Object.entries(data.hourly_avg).map(([h, v]) => ({ hour: `${h}h`, kw: v }))
  const pieData = Object.entries(data.appliance_share).map(([name, value], i) => ({ name, value, color: HEX[COLORS[i % COLORS.length]] }))
  const dow = Object.entries(data.day_of_week_avg).map(([d, v]) => ({
    day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][Number(d)], kw: v,
  }))

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginBottom: 18 }}>
        <StatCard label="Peak-hour Avg" value={`${data.peak_avg_kw} kW`} accent="amber" />
        <StatCard label="Off-peak Avg" value={`${data.offpeak_avg_kw} kW`} accent="cyan" />
        <StatCard label="Temp Correlation" value={data.temperature_correlation} accent="violet" />
        <StatCard label="Outliers Flagged" value={data.outlier_count} accent="red" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16, marginBottom: 16 }}>
        <div className="glass" style={{ padding: 22 }}>
          <h3 style={{ fontSize: 15, marginBottom: 14 }}>Average Load by Hour of Day</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={hourly} margin={{ left: -18, right: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="hour" stroke="var(--text-low)" fontSize={10.5} tickLine={false} axisLine={false} interval={2} />
              <YAxis stroke="var(--text-low)" fontSize={11} tickLine={false} axisLine={false} width={36} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="kw" radius={[4, 4, 0, 0]}>
                {hourly.map((entry, i) => (
                  <Cell key={i} fill={entry.hour.replace('h', '') >= 18 && entry.hour.replace('h', '') < 22 ? '#F5A623' : '#35D4E0'} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <Legend24 />
        </div>

        <div className="glass" style={{ padding: 22 }}>
          <h3 style={{ fontSize: 15, marginBottom: 14 }}>Appliance Share (kWh)</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                {pieData.map((entry, i) => <Cell key={i} fill={entry.color} stroke="none" />)}
              </Pie>
              <Tooltip content={<PieTooltip />} />
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: 12, color: 'var(--text-mid)' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass" style={{ padding: 22 }}>
        <h3 style={{ fontSize: 15, marginBottom: 14 }}>Average Load by Day of Week</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={dow} margin={{ left: -18, right: 8 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="day" stroke="var(--text-low)" fontSize={11.5} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--text-low)" fontSize={11} tickLine={false} axisLine={false} width={36} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="kw" fill="#9B87F5" fillOpacity={0.8} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="glass" style={{ padding: 22, marginTop: 16 }}>
        <h3 style={{ fontSize: 15, marginBottom: 14 }}>Model Performance Comparison</h3>
        <p style={{ color: 'var(--text-low)', fontSize: 12.5, marginBottom: 18 }}>
           Volt automatically trains multiple machine learning models and activates the one with the best test performance (R² for forecasting, Accuracy for classification & anomalies).
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {/* Forecasting comparison */}
          {metrics?.forecast_model && (
            <div style={{ border: '1px solid var(--panel-border)', borderRadius: 12, padding: 16, background: 'rgba(255,255,255,0.01)' }}>
              <h4 style={{ fontSize: 13.5, color: 'var(--text-hi)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span>Forecasting Model</span>
                <span className="mono" style={{ fontSize: 11, padding: '3px 8px', borderRadius: 20, background: 'var(--violet-dim)', color: 'var(--violet)', fontWeight: 600 }}>Regression</span>
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <ModelRow 
                  name="Random Forest" 
                  metrics={[`R²: ${metrics.forecast_model.rf.r2}`, `RMSE: ${metrics.forecast_model.rf.rmse}`]} 
                  isActive={metrics.forecast_model.active === "Random Forest Regressor"} 
                />
                <ModelRow 
                  name="Gradient Boosting" 
                  metrics={[`R²: ${metrics.forecast_model.gb.r2}`, `RMSE: ${metrics.forecast_model.gb.rmse}`]} 
                  isActive={metrics.forecast_model.active === "Gradient Boosting Regressor"} 
                />
              </div>
            </div>
          )}

          {/* Classification comparison */}
          {metrics?.classifier_model && (
            <div style={{ border: '1px solid var(--panel-border)', borderRadius: 12, padding: 16, background: 'rgba(255,255,255,0.01)' }}>
              <h4 style={{ fontSize: 13.5, color: 'var(--text-hi)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span>Usage Classifier</span>
                <span className="mono" style={{ fontSize: 11, padding: '3px 8px', borderRadius: 20, background: 'var(--amber-dim)', color: 'var(--amber)', fontWeight: 600 }}>Classification</span>
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <ModelRow 
                  name="Random Forest" 
                  metrics={[`Acc: ${metrics.classifier_model.rf.accuracy}`, `F1: ${metrics.classifier_model.rf.f1}`]} 
                  isActive={metrics.classifier_model.active === "Random Forest Classifier"} 
                />
                <ModelRow 
                  name="Gradient Boosting" 
                  metrics={[`Acc: ${metrics.classifier_model.gb.accuracy}`, `F1: ${metrics.classifier_model.gb.f1}`]} 
                  isActive={metrics.classifier_model.active === "Gradient Boosting Classifier"} 
                />
              </div>
            </div>
          )}

          {/* Anomaly model comparison */}
          {metrics?.anomaly_model && (
            <div style={{ border: '1px solid var(--panel-border)', borderRadius: 12, padding: 16, background: 'rgba(255,255,255,0.01)' }}>
              <h4 style={{ fontSize: 13.5, color: 'var(--text-hi)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <span>Anomaly Detector</span>
                <span className="mono" style={{ fontSize: 11, padding: '3px 8px', borderRadius: 20, background: 'var(--cyan-dim)', color: 'var(--cyan)', fontWeight: 600 }}>Anomaly</span>
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <ModelRow 
                  name="Isolation Forest" 
                  metrics={[`Acc: ${metrics.anomaly_model.if.accuracy}`, `F1: ${metrics.anomaly_model.if.f1}`]} 
                  isActive={metrics.anomaly_model.active === "Isolation Forest"} 
                />
                <ModelRow 
                  name="One-Class SVM" 
                  metrics={[`Acc: ${metrics.anomaly_model.svm.accuracy}`, `F1: ${metrics.anomaly_model.svm.f1}`]} 
                  isActive={metrics.anomaly_model.active === "One-Class SVM"} 
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Unified Tab Selector for Metrics */}
      {metrics && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 24, marginBottom: 16, borderBottom: '1px solid var(--panel-border)', paddingBottom: 12 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700 }}>Model Evaluation Metrics</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <button 
              onClick={() => setSelectedCm('classifier')}
              style={{
                padding: '6px 14px', borderRadius: 8, fontSize: 12.5, fontWeight: 600, border: 'none',
                background: selectedCm === 'classifier' ? 'var(--amber-dim)' : 'transparent',
                color: selectedCm === 'classifier' ? 'var(--amber)' : 'var(--text-mid)',
                cursor: 'pointer', transition: 'all 0.15s ease'
              }}
            >
              Usage Classifier
            </button>
            <button 
              onClick={() => setSelectedCm('anomaly')}
              style={{
                padding: '6px 14px', borderRadius: 8, fontSize: 12.5, fontWeight: 600, border: 'none',
                background: selectedCm === 'anomaly' ? 'var(--cyan-dim)' : 'transparent',
                color: selectedCm === 'anomaly' ? 'var(--cyan)' : 'var(--text-mid)',
                cursor: 'pointer', transition: 'all 0.15s ease'
              }}
            >
              Anomaly Detector
            </button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16 }}>
        {/* ROC Curve Graph */}
        {metrics && (
          <div className="glass" style={{ padding: 22 }}>
            {selectedCm === 'classifier' ? (
              // Usage Classifier ROC Curve
              <Fragment>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
                  <h3 style={{ fontSize: 15 }}>Usage Classifier ROC Curve</h3>
                  <span style={{ fontSize: 11.5, color: 'var(--text-low)' }}>Multiclass (One-vs-Rest)</span>
                </div>
                <ResponsiveContainer width="100%" height={230}>
                  <LineChart data={metrics.classifier_model.roc_curve} margin={{ left: -22, right: 8, top: 10 }}>
                    <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                    <XAxis dataKey="fpr" stroke="var(--text-low)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} />
                    <YAxis stroke="var(--text-low)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} />
                    <Tooltip content={<ClassifierRocTooltip />} />
                    {/* Diagonal Reference Line */}
                    <Line type="monotone" dataKey="fpr" stroke="rgba(255,255,255,0.15)" strokeWidth={1.5} strokeDasharray="4 4" dot={false} activeDot={false} />
                    {/* Low vs Rest */}
                    <Line type="monotone" dataKey="low_tpr" name="Low vs Rest" stroke="var(--amber)" strokeWidth={2.5} dot={false} />
                    {/* Medium vs Rest */}
                    <Line type="monotone" dataKey="med_tpr" name="Medium vs Rest" stroke="var(--cyan)" strokeWidth={2.5} dot={false} />
                    {/* High vs Rest */}
                    <Line type="monotone" dataKey="high_tpr" name="High vs Rest" stroke="var(--violet)" strokeWidth={2.5} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, fontSize: 11, color: 'var(--text-mid)', marginTop: 8 }}>
                  <span><i style={{ display: 'inline-block', width: 10, height: 3, background: 'var(--amber)', borderRadius: 2, marginRight: 5 }} />Low vs Rest (AUC: {metrics.classifier_model.auc.low})</span>
                  <span><i style={{ display: 'inline-block', width: 10, height: 3, background: 'var(--cyan)', borderRadius: 2, marginRight: 5 }} />Med vs Rest (AUC: {metrics.classifier_model.auc.med})</span>
                  <span><i style={{ display: 'inline-block', width: 10, height: 3, background: 'var(--violet)', borderRadius: 2, marginRight: 5 }} />High vs Rest (AUC: {metrics.classifier_model.auc.high})</span>
                </div>
              </Fragment>
            ) : (
              // Anomaly Detector ROC Curve
              <Fragment>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14 }}>
                  <h3 style={{ fontSize: 15 }}>Anomaly Detector ROC Curve</h3>
                  <span style={{ fontSize: 11.5, color: 'var(--text-low)' }}>Anomaly Models Comparison</span>
                </div>
                <ResponsiveContainer width="100%" height={230}>
                  <LineChart data={metrics.anomaly_model.roc_curve} margin={{ left: -22, right: 8, top: 10 }}>
                    <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                    <XAxis dataKey="fpr" stroke="var(--text-low)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} />
                    <YAxis stroke="var(--text-low)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 1]} tickFormatter={(v) => v.toFixed(1)} />
                    <Tooltip content={<RocTooltip />} />
                    {/* Diagonal Reference Line */}
                    <Line type="monotone" dataKey="fpr" stroke="rgba(255,255,255,0.15)" strokeWidth={1.5} strokeDasharray="4 4" dot={false} activeDot={false} />
                    {/* Isolation Forest Line */}
                    <Line type="monotone" dataKey="if_tpr" name="Isolation Forest" stroke="var(--cyan)" strokeWidth={2.5} dot={false} />
                    {/* One-Class SVM Line */}
                    <Line type="monotone" dataKey="svm_tpr" name="One-Class SVM" stroke="var(--violet)" strokeWidth={2.5} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, fontSize: 11, color: 'var(--text-mid)', marginTop: 8 }}>
                  <span><i style={{ display: 'inline-block', width: 10, height: 3, background: 'var(--cyan)', borderRadius: 2, marginRight: 5 }} />Isolation Forest (AUC: {metrics.anomaly_model.if.auc})</span>
                  <span><i style={{ display: 'inline-block', width: 10, height: 3, background: 'var(--violet)', borderRadius: 2, marginRight: 5 }} />One-Class SVM (AUC: {metrics.anomaly_model.svm.auc})</span>
                  <span style={{ color: 'var(--text-low)' }}><i style={{ display: 'inline-block', width: 10, height: 1, borderTop: '1px dashed rgba(255,255,255,0.4)', marginRight: 5 }} />Random Baseline (AUC: 0.50)</span>
                </div>
              </Fragment>
            )}
          </div>
        )}

        {/* Confusion Matrix Card */}
        {metrics && (
          <div className="glass" style={{ padding: 22, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <RenderConfusionMatrix selectedCm={selectedCm} metrics={metrics} />
          </div>
        )}
      </div>
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

function Legend24() {
  return (
    <div style={{ display: 'flex', gap: 16, fontSize: 11, color: 'var(--text-mid)', marginTop: 6 }}>
      <span><i style={{ display: 'inline-block', width: 8, height: 8, background: '#F5A623', borderRadius: 2, marginRight: 5 }} />Peak hours (6–10 PM)</span>
      <span><i style={{ display: 'inline-block', width: 8, height: 8, background: '#35D4E0', borderRadius: 2, marginRight: 5 }} />Other hours</span>
    </div>
  )
}

function PieTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const p = payload[0]
  return (
    <div className="glass" style={{ padding: '8px 12px', fontSize: 12 }}>
      <div style={{ color: p.payload.color }}>{p.name}</div>
      <div className="mono">{p.value} kWh</div>
    </div>
  )
}

function ModelRow({ name, metrics, isActive }) {
  return (
    <div 
      style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '10px 12px', 
        borderRadius: 8, 
        border: isActive ? '1px solid rgba(74,222,128,0.3)' : '1px solid transparent',
        background: isActive ? 'var(--green-dim)' : 'rgba(255,255,255,0.02)',
        position: 'relative'
      }}
    >
      <div>
        <div style={{ fontSize: 12.5, fontWeight: isActive ? 600 : 500, color: isActive ? 'var(--green)' : 'var(--text-hi)' }}>
          {name} {isActive && <span style={{ marginLeft: 4 }}>⚡</span>}
        </div>
        <div className="mono" style={{ fontSize: 10.5, color: isActive ? 'var(--text-hi)' : 'var(--text-low)', marginTop: 4, display: 'flex', gap: 8 }}>
          {metrics.map((m, idx) => <span key={idx}>{m}</span>)}
        </div>
      </div>
      {isActive && (
        <span style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', color: 'var(--green)', letterSpacing: '0.05em' }}>
          Active
        </span>
      )}
    </div>
  )
}

function ClassifierRocTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const lowPoint = payload.find(p => p.dataKey === 'low_tpr')
  const medPoint = payload.find(p => p.dataKey === 'med_tpr')
  const highPoint = payload.find(p => p.dataKey === 'high_tpr')
  const fprVal = payload[0]?.payload?.fpr
  return (
    <div className="glass" style={{ padding: '8px 12px', fontSize: 12 }}>
      <div style={{ color: 'var(--text-low)', marginBottom: 4 }}>FPR: {fprVal}</div>
      {lowPoint && <div style={{ color: 'var(--amber)' }}>Low vs Rest TPR: {lowPoint.value}</div>}
      {medPoint && <div style={{ color: 'var(--cyan)' }}>Medium vs Rest TPR: {medPoint.value}</div>}
      {highPoint && <div style={{ color: 'var(--violet)' }}>High vs Rest TPR: {highPoint.value}</div>}
    </div>
  )
}

function RocTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const ifPoint = payload.find(p => p.dataKey === 'if_tpr')
  const svmPoint = payload.find(p => p.dataKey === 'svm_tpr')
  const fprVal = payload[0]?.payload?.fpr
  return (
    <div className="glass" style={{ padding: '8px 12px', fontSize: 12 }}>
      <div style={{ color: 'var(--text-low)', marginBottom: 4 }}>FPR: {fprVal}</div>
      {ifPoint && <div style={{ color: 'var(--cyan)' }}>Isolation Forest TPR: {ifPoint.value}</div>}
      {svmPoint && <div style={{ color: 'var(--violet)' }}>One-Class SVM TPR: {svmPoint.value}</div>}
    </div>
  )
}

function RenderConfusionMatrix({ selectedCm, metrics }) {
  if (!metrics) return null;

  if (selectedCm === 'classifier') {
    const activeClf = metrics.classifier_model.active.includes('Gradient Boosting') 
      ? metrics.classifier_model.gb 
      : metrics.classifier_model.rf;
    const matrix = activeClf.confusion_matrix || [[0,0,0],[0,0,0],[0,0,0]];
    const labels = ["Low", "Medium", "High"];
    
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h4 style={{ fontSize: 13, color: 'var(--text-mid)', fontWeight: 600 }}>Usage Classifier Confusion Matrix</h4>
          <span className="mono" style={{ fontSize: 10, color: 'var(--text-low)', padding: '2px 6px', borderRadius: 4, background: 'rgba(255,255,255,0.04)' }}>
            Active: {metrics.classifier_model.active.split(' ')[0]}
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '70px repeat(3, 1fr)', gap: 6, textAlign: 'center', fontSize: 11.5 }}>
          {/* Header row */}
          <div></div>
          {labels.map(l => <div key={l} style={{ fontWeight: 600, color: 'var(--text-low)', padding: 4 }}>Pred {l}</div>)}

          {/* Grid rows */}
          {labels.map((rowLabel, rIdx) => (
            <Fragment key={rowLabel}>
              <div style={{ fontWeight: 600, color: 'var(--text-low)', display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: 4 }}>
                Act {rowLabel}
              </div>
              {matrix[rIdx].map((val, cIdx) => {
                const totalRow = matrix[rIdx].reduce((a,b)=>a+b, 0) || 1;
                const ratio = val / totalRow;
                const bg = rIdx === cIdx 
                  ? `rgba(74, 222, 128, ${0.1 + ratio * 0.4})` 
                  : `rgba(239, 68, 68, ${ratio * 0.25})`;
                return (
                  <div key={cIdx} style={{ background: bg, padding: '10px 4px', borderRadius: 6, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <span className="mono" style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-hi)' }}>{val}</span>
                    <span style={{ fontSize: 9, color: 'var(--text-low)', marginTop: 2 }}>{Math.round(ratio * 100)}%</span>
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
    );
  } else {
    const activeAnomaly = metrics.anomaly_model.active === 'One-Class SVM' 
      ? metrics.anomaly_model.svm 
      : metrics.anomaly_model.if;
    const matrix = activeAnomaly.confusion_matrix || [[0,0],[0,0]];
    const labels = ["Normal", "Anomaly"];
    
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h4 style={{ fontSize: 13, color: 'var(--text-mid)', fontWeight: 600 }}>Anomaly Detector Confusion Matrix</h4>
          <span className="mono" style={{ fontSize: 10, color: 'var(--text-low)', padding: '2px 6px', borderRadius: 4, background: 'rgba(255,255,255,0.04)' }}>
            Active: {metrics.anomaly_model.active.split(' ')[0]}
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '70px repeat(2, 1fr)', gap: 6, textAlign: 'center', fontSize: 11.5 }}>
          {/* Header row */}
          <div></div>
          {labels.map(l => <div key={l} style={{ fontWeight: 600, color: 'var(--text-low)', padding: 4 }}>Pred {l}</div>)}

          {/* Grid rows */}
          {labels.map((rowLabel, rIdx) => (
            <Fragment key={rowLabel}>
              <div style={{ fontWeight: 600, color: 'var(--text-low)', display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: 4 }}>
                Act {rowLabel}
              </div>
              {matrix[rIdx].map((val, cIdx) => {
                const totalRow = matrix[rIdx].reduce((a,b)=>a+b, 0) || 1;
                const ratio = val / totalRow;
                const bg = rIdx === cIdx 
                  ? `rgba(74, 222, 128, ${0.1 + ratio * 0.4})` 
                  : `rgba(239, 68, 68, ${ratio * 0.25})`;
                return (
                  <div key={cIdx} style={{ background: bg, padding: '14px 4px', borderRadius: 6, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <span className="mono" style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-hi)' }}>{val}</span>
                    <span style={{ fontSize: 9, color: 'var(--text-low)', marginTop: 2 }}>{Math.round(ratio * 100)}%</span>
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
    );
  }
}
