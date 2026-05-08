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
        <h1 className="text-2xl font-bold text-gray-900">Prediction History</h1>
        <p className="text-gray-500 text-sm mt-1">
          All past churn predictions — filter by tier, sort by probability.
        </p>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-400 text-sm">Loading history...</div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {!loading && !error && <CustomerHistory records={records} />}
    </div>
  )
}