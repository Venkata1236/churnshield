import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="max-w-xs rounded-xl border border-slate-200 bg-white p-3 shadow-lg">
      <p className="mb-1 text-sm font-semibold text-slate-900">{d.feature}</p>
      <p className="text-xs text-slate-500">{d.plain_english}</p>
      <p className="mt-1 text-xs font-medium text-slate-700">
        SHAP: {Math.abs(d.shap_value).toFixed(3)}
      </p>
    </div>
  )
}

const shorten = (str) => (str.length > 18 ? `${str.slice(0, 16)}…` : str)

export default function ChurnDriversChart({ drivers = [], signals = [] }) {
  const driverData = [...drivers]
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .slice(0, 5)
    .map((d) => ({ ...d, abs: Math.abs(d.shap_value) }))

  const signalData = [...signals]
    .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
    .slice(0, 3)
    .map((s) => ({ ...s, abs: Math.abs(s.shap_value) }))

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <h3 className="text-base font-semibold text-slate-900">Why This Customer Might Leave</h3>
        <p className="text-xs text-slate-500">Top churn drivers and retention signals</p>
      </div>

      <div className="space-y-6">
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Churn Drivers
          </p>
          {driverData.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">No churn drivers available</p>
          ) : (
            <ResponsiveContainer width="100%" height={driverData.length * 44 + 12}>
              <BarChart
                data={driverData}
                layout="vertical"
                margin={{ left: 10, right: 24, top: 0, bottom: 0 }}
              >
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="feature"
                  width={150}
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickFormatter={shorten}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="abs" radius={[0, 6, 6, 0]} maxBarSize={18}>
                  {driverData.map((_, i) => (
                    <Cell key={i} fill="#ef4444" fillOpacity={1 - i * 0.1} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {signalData.length > 0 && (
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Retention Signals
            </p>
            <ResponsiveContainer width="100%" height={signalData.length * 44 + 12}>
              <BarChart
                data={signalData}
                layout="vertical"
                margin={{ left: 10, right: 24, top: 0, bottom: 0 }}
              >
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="feature"
                  width={150}
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  tickFormatter={shorten}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="abs" radius={[0, 6, 6, 0]} maxBarSize={18}>
                  {signalData.map((_, i) => (
                    <Cell key={i} fill="#22c55e" fillOpacity={1 - i * 0.12} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}