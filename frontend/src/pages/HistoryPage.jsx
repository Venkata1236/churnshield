import { useState, useEffect } from 'react'
import CustomerHistory from '../components/CustomerHistory'
import { getHistory } from '../services/api'

export default function HistoryPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHistory()
      .then(setRecords)
      .catch(() => setError('Failed to load history. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Prediction History</h1>
        <p className="text-slate-500 text-sm mt-1">
          All past churn predictions — filter by tier, sort by probability.
        </p>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16 gap-3 text-slate-400 text-sm">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          Loading history…
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
          {error}
        </div>
      )}

      {!loading && !error && <CustomerHistory records={records} />}
    </div>
  )
}