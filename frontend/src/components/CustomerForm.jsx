import { useState } from 'react'

const defaultForm = {
  customer_id: '',
  tenure: '',
  monthly_charges: '',
  total_charges: '',
  contract: 'Month-to-month',
  payment_method: 'Electronic check',
  internet_service: 'Fiber optic',
  tech_support: 'No',
  online_security: 'No',
  streaming_tv: 'No',
  streaming_movies: 'No',
  online_backup: 'No',
  device_protection: 'No',
  multiple_lines: 'No',
  phone_service: 'Yes',
  paperless_billing: 'Yes',
  senior_citizen: 0,
  partner: 'No',
  dependents: 'No',
}

const Toggle = ({ label, value, onChange }) => (
  <div className="flex items-center justify-between">
    <span className="text-sm text-gray-600">{label}</span>
    <button
      type="button"
      onClick={() => onChange(value === 'Yes' ? 'No' : 'Yes')}
      className={`w-12 h-6 rounded-full transition-colors duration-200 ${
        value === 'Yes' ? 'bg-blue-600' : 'bg-gray-300'
      }`}
    >
      <span
        className={`block w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200 mx-0.5 ${
          value === 'Yes' ? 'translate-x-6' : 'translate-x-0'
        }`}
      />
    </button>
  </div>
)

export default function CustomerForm({ onSubmit, loading }) {
  const [form, setForm] = useState(defaultForm)

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...form,
      tenure: Number(form.tenure),
      monthly_charges: Number(form.monthly_charges),
      total_charges: Number(form.total_charges),
      senior_citizen: Number(form.senior_citizen),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Account Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">Account Info</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-600 block mb-1">Customer ID</label>
            <input
              type="text"
              value={form.customer_id}
              onChange={(e) => set('customer_id', e.target.value)}
              placeholder="e.g. CUST-001"
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 block mb-1">Tenure (months)</label>
            <input
              type="number"
              value={form.tenure}
              onChange={(e) => set('tenure', e.target.value)}
              placeholder="e.g. 12"
              required
              min={0}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="mt-4">
          <label className="text-sm text-gray-600 block mb-2">Contract Type</label>
          <div className="flex gap-3">
            {['Month-to-month', 'One year', 'Two year'].map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => set('contract', c)}
                className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                  form.contract === c
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 text-gray-600 hover:border-blue-400'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <label className="text-sm text-gray-600 block mb-1">Payment Method</label>
          <select
            value={form.payment_method}
            onChange={(e) => set('payment_method', e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'].map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Services */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">Services</h3>
        <div className="mb-4">
          <label className="text-sm text-gray-600 block mb-2">Internet Service</label>
          <div className="flex gap-3">
            {['Fiber optic', 'DSL', 'No'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => set('internet_service', s)}
                className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                  form.internet_service === s
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 text-gray-600 hover:border-blue-400'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {[
            ['Tech Support', 'tech_support'],
            ['Online Security', 'online_security'],
            ['Streaming TV', 'streaming_tv'],
            ['Streaming Movies', 'streaming_movies'],
            ['Online Backup', 'online_backup'],
            ['Device Protection', 'device_protection'],
            ['Multiple Lines', 'multiple_lines'],
            ['Paperless Billing', 'paperless_billing'],
          ].map(([label, key]) => (
            <Toggle
              key={key}
              label={label}
              value={form[key]}
              onChange={(v) => set(key, v)}
            />
          ))}
        </div>
      </div>

      {/* Charges */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">Charges</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-600 block mb-1">Monthly Charges (₹)</label>
            <input
              type="number"
              value={form.monthly_charges}
              onChange={(e) => set('monthly_charges', e.target.value)}
              placeholder="e.g. 85.50"
              required
              min={0}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 block mb-1">Total Charges (₹)</label>
            <input
              type="number"
              value={form.total_charges}
              onChange={(e) => set('total_charges', e.target.value)}
              placeholder="e.g. 171.00"
              required
              min={0}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Demographics */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="font-semibold text-gray-800 mb-4">Demographics</h3>
        <div className="grid grid-cols-2 gap-3">
          <Toggle
            label="Senior Citizen"
            value={form.senior_citizen === 1 ? 'Yes' : 'No'}
            onChange={(v) => set('senior_citizen', v === 'Yes' ? 1 : 0)}
          />
          <Toggle label="Has Partner" value={form.partner} onChange={(v) => set('partner', v)} />
          <Toggle label="Has Dependents" value={form.dependents} onChange={(v) => set('dependents', v)} />
          <Toggle label="Phone Service" value={form.phone_service} onChange={(v) => set('phone_service', v)} />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 rounded-xl transition-colors"
      >
        {loading ? 'Analyzing...' : 'Analyze Churn Risk →'}
      </button>
    </form>
  )
}