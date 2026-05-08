import { useState } from 'react'
import { Copy, Check, ExternalLink, AlertTriangle, Target, Gift } from 'lucide-react'

const TIER_CONFIG = {
  LOW: {
    label: 'Standard Loyalty Offer',
    icon: Gift,
    bg: 'bg-green-50',
    border: 'border-green-200',
    badge: 'bg-green-100 text-green-700',
    accent: 'text-green-600',
    bar: 'bg-green-500',
  },
  MEDIUM: {
    label: 'Targeted Retention Offer',
    icon: Target,
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-700',
    accent: 'text-yellow-600',
    bar: 'bg-yellow-500',
  },
  HIGH: {
    label: 'Escalate to Senior Specialist',
    icon: AlertTriangle,
    bg: 'bg-red-50',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-700',
    accent: 'text-red-600',
    bar: 'bg-red-500',
  },
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg px-3 py-1.5 transition-colors"
    >
      {copied ? (
        <>
          <Check size={12} className="text-green-500" />
          Copied
        </>
      ) : (
        <>
          <Copy size={12} />
          Copy Message
        </>
      )}
    </button>
  )
}

export default function RetentionStrategy({ data }) {
  const [message, setMessage] = useState(data?.message_draft || '')

  if (!data) return null

  const tier = data.risk_tier || 'LOW'
  const config = TIER_CONFIG[tier] || TIER_CONFIG.LOW
  const Icon = config.icon
  const offer = data.offer_details || {}
  const savePct = ((data.estimated_save_probability || 0) * 100).toFixed(0)

  return (
    <div className={`rounded-xl border ${config.border} ${config.bg} p-5 space-y-5`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.badge}`}>
            <Icon size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">{config.label}</h3>
            <p className="text-xs text-gray-500">Strategy: {data.retention_strategy}</p>
          </div>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${config.badge}`}>
          {tier} RISK
        </span>
      </div>

      {/* Save probability */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Estimated Save Probability</span>
          <span className={`font-semibold ${config.accent}`}>{savePct}%</span>
        </div>
        <div className="w-full bg-white rounded-full h-2 border border-gray-200">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${config.bar}`}
            style={{ width: `${savePct}%` }}
          />
        </div>
      </div>

      {/* Offer details */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-2">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Offer Details</p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-gray-400">Offer Type</p>
            <p className="text-sm font-semibold text-gray-800">{offer.offer_type || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Discount</p>
            <p className={`text-sm font-semibold ${config.accent}`}>{offer.discount_pct || 0}% off</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Valid For</p>
            <p className="text-sm font-semibold text-gray-800">{offer.validity_days || 30} days</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Urgency</p>
            <p className="text-sm font-semibold text-gray-800">
              {offer.urgency || (tier === 'HIGH' ? 'CRITICAL' : 'Standard')}
            </p>
          </div>
        </div>
        {offer.conditions && (
          <p className="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-100">
            {offer.conditions}
          </p>
        )}
        {offer.escalation_brief && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-500 mb-1">Escalation Brief</p>
            <p className="text-xs text-gray-600">{offer.escalation_brief}</p>
          </div>
        )}
      </div>

      {/* Message draft */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {tier === 'HIGH' ? 'Call Opening Script' : 'Customer Message'}
          </p>
          <CopyButton text={message} />
        </div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          className="w-full text-sm text-gray-700 bg-white border border-gray-200 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* LangSmith trace */}
      {data.langsmith_trace_url && (
        <a
          href={data.langsmith_trace_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs text-blue-500 hover:text-blue-700"
        >
          <ExternalLink size={12} />
          View AI reasoning trace →
        </a>
      )}
    </div>
  )
}