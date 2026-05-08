import { useLocation, useNavigate } from 'react-router-dom'
import ChurnGauge from '../components/ChurnGauge'
import ChurnDriversChart from '../components/ChurnDriversChart'
import RetentionStrategy from '../components/RetentionStrategy'

export default function ResultsPage() {
  const { state } = useLocation()
  const navigate = useNavigate()

  if (!state?.prediction) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-400 text-sm mb-4">No results yet.</p>
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 text-sm hover:underline"
        >
          ← Go back to Analyze
        </button>
      </div>
    )
  }

  const { prediction, retention } = state

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Results</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            Customer: <span className="font-medium text-gray-600">{prediction.customer_id}</span>
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Analyze Another
        </button>
      </div>

      {/* Gauge + Drivers side by side on desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChurnGauge
          probability={prediction.churn_probability}
          riskTier={prediction.risk_tier}
        />
        <ChurnDriversChart
          drivers={prediction.top_churn_drivers || []}
          signals={prediction.retention_signals || []}
        />
      </div>

      {/* Prediction summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-3">Prediction Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Churn Probability', value: `${(prediction.churn_probability * 100).toFixed(1)}%` },
            { label: 'Risk Tier', value: prediction.risk_tier },
            { label: 'Prediction', value: prediction.churn_prediction },
            { label: 'Proceed to Retention', value: prediction.proceed_to_retention ? 'Yes' : 'No' },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-xs text-gray-400">{label}</p>
              <p className="text-sm font-semibold text-gray-800 mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Retention strategy */}
      {retention ? (
        <RetentionStrategy data={retention} />
      ) : (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
          <p className="text-green-700 font-semibold">Low Risk Customer</p>
          <p className="text-green-600 text-sm mt-1">
            Churn probability is below threshold — no retention action needed.
          </p>
        </div>
      )}
    </div>
  )
}