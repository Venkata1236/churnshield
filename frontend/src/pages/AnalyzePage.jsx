import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import CustomerForm from '../components/CustomerForm'
import { predictChurn, getRetentionStrategy } from '../services/api'

export default function AnalyzePage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const prediction = await predictChurn(formData)
      let retention = null
      if (prediction.proceed_to_retention) {
        retention = await getRetentionStrategy(prediction.customer_id)
      }
      navigate('/results', { state: { prediction, retention } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Check the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analyze Churn Risk</h1>
        <p className="text-gray-500 text-sm mt-1">
          Enter customer details to predict churn probability and generate a retention strategy.
        </p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      <CustomerForm onSubmit={handleSubmit} loading={loading} />
    </div>
  )
}