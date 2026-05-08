import { useState } from 'react'
import { ChevronUp, ChevronDown } from 'lucide-react'

const TIER_STYLES = {
  HIGH: 'bg-red-100 text-red-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-green-100 text-green-700',
}

const OUTCOME_STYLES = {
  PENDING: 'bg-gray-100 text-gray-500',
  SAVED: 'bg-green-100 text-green-700',
  CHURNED: 'bg-red-100 text-red-700',
}

export default function CustomerHistory({ records = [] }) {
  const [filter, setFilter] = useState('ALL')
  const [sortDir, setSortDir] = useState('desc')
  const [outcomes, setOutcomes] = useState({})

  const toggleOutcome = (id, current) => {
    const cycle = { PENDING: 'SAVED', SAVED: 'CHURNED', CHURNED: 'PENDING' }
    setOutcomes((prev) => ({ ...prev, [id]: cycle[current] }))
  }

  const filtered = records
    .filter((r) => filter === 'ALL' || r.risk_tier === filter)
    .sort((a, b) => {
      const diff = a.churn_probability - b.churn_probability
      return sortDir === 'desc' ? -diff : diff
    })

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
        <h3 className="font-semibold text-gray-800">Prediction History</h3>
        <div className="flex gap-2">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                filter === t
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-200 text-gray-500 hover:border-blue-400'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400 text-sm">
          No predictions found
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Date
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Customer ID
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Risk Tier
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  <button
                    onClick={() => setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))}
                    className="flex items-center gap-1 hover:text-gray-700"
                  >
                    Churn Prob
                    {sortDir === 'desc' ? <ChevronDown size={12} /> : <ChevronUp size={12} />}
                  </button>
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Strategy
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Outcome
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.map((r) => {
                const outcome = outcomes[r.id] || r.outcome || 'PENDING'
                return (
                  <tr key={r.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">
                      {new Date(r.predicted_at || r.created_at).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-800">
                      {r.customer_id}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${TIER_STYLES[r.risk_tier] || TIER_STYLES.LOW}`}>
                        {r.risk_tier}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-100 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full bg-blue-500"
                            style={{ width: `${(r.churn_probability * 100).toFixed(0)}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-700">
                          {(r.churn_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      {r.retention_strategy || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => toggleOutcome(r.id, outcome)}
                        className={`text-xs px-2.5 py-1 rounded-full font-semibold transition-colors ${OUTCOME_STYLES[outcome]}`}
                      >
                        {outcome}
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}