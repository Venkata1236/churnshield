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
  if (active && payload && payload.length) {
    const d = payload[0].payload
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg max-w-xs">
        <p className="text-sm font-semibold text-gray-800 mb-1">{d.feature}</p>
        <p className="text-xs text-gray-500">{d.plain_english}</p>
        <p className="text-xs mt-1 font-medium" style={{ color: payload[0].fill }}>
          SHAP: {Math.abs(d.shap_value).toFixed(3)}
        </p>
      </div>
    )
  }
  return null
}

const shorten = (str) =>
  str.length > 22 ? str.slice(0, 20) + '…' : str

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
    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-6">
      <div>
        <h3 className="font-semibold text-gray-800 mb-1">Why This Customer Might Leave</h3>
        <p className="text-xs text-gray-400 mb-4">Top churn drivers — higher bar = stronger signal</p>

        {driverData.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">No churn drivers available</p>
        ) : (
          <ResponsiveContainer width="100%" height={driverData.length * 48}>
            <BarChart
              data={driverData}
              layout="vertical"
              margin={{ left: 8, right: 24, top: 0, bottom: 0 }}
            >
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="feature"
                width={140}
                tick={{ fontSize: 11, fill: '#6b7280' }}
                tickFormatter={shorten}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="abs" radius={[0, 4, 4, 0]} maxBarSize={20}>
                {driverData.map((_, i) => (
                  <Cell key={i} fill="#ef4444" fillOpacity={1 - i * 0.12} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {signalData.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-800 mb-1">Retention Signals</h3>
          <p className="text-xs text-gray-400 mb-4">Features reducing churn risk</p>

          <ResponsiveContainer width="100%" height={signalData.length * 48}>
            <BarChart
              data={signalData}
              layout="vertical"
              margin={{ left: 8, right: 24, top: 0, bottom: 0 }}
            >
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="feature"
                width={140}
                tick={{ fontSize: 11, fill: '#6b7280' }}
                tickFormatter={shorten}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="abs" radius={[0, 4, 4, 0]} maxBarSize={20}>
                {signalData.map((_, i) => (
                  <Cell key={i} fill="#22c55e" fillOpacity={1 - i * 0.15} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}