import { useState } from 'react'
import { Copy, Check, ExternalLink, AlertTriangle, Target, Gift } from 'lucide-react'

const TIER_CONFIG = {
  LOW: {
    label: 'Standard Loyalty Offer',
    icon: Gift,
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    badge: 'bg-emerald-100 text-emerald-700',
    accent: 'text-emerald-700',
    bar: 'bg-emerald-500',
  },
  MEDIUM: {
    label: 'Targeted Retention Offer',
    icon: Target,
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    badge: 'bg-amber-100 text-amber-700',
    accent: 'text-amber-700',
    bar: 'bg-amber-500',
  },
  HIGH: {
    label: 'Escalate to Senior Specialist',
    icon: AlertTriangle,
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    badge: 'bg-rose-100 text-rose-700',
    accent: 'text-rose-700',
    bar: 'bg-rose-500',
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
      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-700"
    >
      {copied ? (
        <>
          <Check size={12} className="text-emerald-500" />
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
    <div className={`rounded-2xl border ${config.border} ${config.bg} p-6 shadow-sm`}>
      <div className="flex flex-col gap-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`rounded-xl p-2.5 ${config.badge}`}>
              <Icon size={18} />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900">{config.label}</h3>
              <p className="text-xs text-slate-500">Strategy: {data.retention_strategy}</p>
            </div>
          </div>

          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${config.badge}`}>
            {tier} RISK
          </span>
        </div>

        <div>
          <div className="mb-1 flex justify-between text-xs text-slate-500">
            <span>Estimated Save Probability</span>
            <span className={`font-semibold ${config.accent}`}>{savePct}%</span>
          </div>
          <div className="h-2 rounded-full bg-white/80 ring-1 ring-slate-200">
            <div
              className={`h-2 rounded-full transition-all duration-700 ${config.bar}`}
              style={{ width: `${savePct}%` }}
            />
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Offer Details
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-400">Offer Type</p>
              <p className="text-sm font-semibold text-slate-900">{offer.offer_type || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400">Discount</p>
              <p className={`text-sm font-semibold ${config.accent}`}>{offer.discount_pct || 0}% off</p>
            </div>
            <div>
              <p className="text-xs text-slate-400">Valid For</p>
              <p className="text-sm font-semibold text-slate-900">{offer.validity_days || 30} days</p>
            </div>
            <div>
              <p className="text-xs text-slate-400">Urgency</p>
              <p className="text-sm font-semibold text-slate-900">
                {offer.urgency || (tier === 'HIGH' ? 'CRITICAL' : 'Standard')}
              </p>
            </div>
          </div>

          {offer.conditions && (
            <p className="mt-3 border-t border-slate-100 pt-3 text-xs leading-5 text-slate-500">
              {offer.conditions}
            </p>
          )}

          {offer.escalation_brief && (
            <div className="mt-3 border-t border-slate-100 pt-3">
              <p className="mb-1 text-xs font-semibold text-slate-500">Escalation Brief</p>
              <p className="text-xs leading-5 text-slate-600">{offer.escalation_brief}</p>
            </div>
          )}
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              {tier === 'HIGH' ? 'Call Opening Script' : 'Customer Message'}
            </p>
            <CopyButton text={message} />
          </div>

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
            className="w-full resize-none rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-700 shadow-sm outline-none ring-0 focus:border-slate-300 focus:ring-2 focus:ring-slate-200"
          />
        </div>

        {data.langsmith_trace_url && (
          <a
            href={data.langsmith_trace_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-700"
          >
            <ExternalLink size={12} />
            View AI reasoning trace →
          </a>
        )}
      </div>
    </div>
  )
}