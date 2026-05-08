import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export const predictChurn = async (customerData) => {
  const { data } = await api.post('/api/v1/predict-churn', customerData)
  return data
}

export const getRetentionStrategy = async (customerId) => {
  const { data } = await api.post(`/api/v1/retention-strategy/${customerId}`)
  return data
}

export const getHistory = async () => {
  const { data } = await api.get('/api/v1/history')
  return data
}

export const updateOutcome = async (customerId, outcome) => {
  const { data } = await api.patch(`/api/v1/history/${customerId}/outcome`, {
    outcome,
  })
  return data
}

export const getSavedRetention = async (customerId) => {
  const { data } = await api.get(`/api/v1/retention-strategy/${customerId}`)
  return data
}