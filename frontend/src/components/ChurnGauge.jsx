import { useEffect, useRef } from 'react'

const RISK_COLORS = {
  LOW: '#16a34a',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
}

const RISK_LABELS = {
  LOW: 'Low Risk',
  MEDIUM: 'Medium Risk',
  HIGH: 'High Risk',
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const toRad = (deg) => (deg * Math.PI) / 180
  const x1 = cx + r * Math.cos(toRad(startAngle))
  const y1 = cy + r * Math.sin(toRad(startAngle))
  const x2 = cx + r * Math.cos(toRad(endAngle))
  const y2 = cy + r * Math.sin(toRad(endAngle))
  return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`
}

export default function ChurnGauge({ probability = 0, riskTier = 'LOW' }) {
  const needleRef = useRef(null)
  const pct = Math.min(Math.max(probability, 0), 1)
  const angle = -90 + pct * 180
  const color = RISK_COLORS[riskTier] || RISK_COLORS.LOW
  const pctDisplay = (pct * 100).toFixed(1)

  useEffect(() => {
    if (needleRef.current) {
      needleRef.current.style.transition = 'transform 900ms cubic-bezier(0.22, 1, 0.36, 1)'
      needleRef.current.style.transform = `rotate(${angle}deg)`
    }
  }, [angle])

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">Churn Risk Score</h3>
        <p className="text-xs text-slate-500">Higher score means stronger churn pressure</p>
      </div>

      <div className="relative mx-auto h-56 w-full max-w-sm">
        <svg viewBox="0 0 220 130" className="h-full w-full">
          <path
            d={describeArc(110, 110, 82, -180, 0)}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="18"
            strokeLinecap="round"
          />
          <path
            d={describeArc(110, 110, 82, -180, -108)}
            fill="none"
            stroke="#16a34a"
            strokeWidth="18"
            strokeLinecap="round"
          />
          <path
            d={describeArc(110, 110, 82, -108, -54)}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="18"
            strokeLinecap="round"
          />
          <path
            d={describeArc(110, 110, 82, -54, 0)}
            fill="none"
            stroke="#ef4444"
            strokeWidth="18"
            strokeLinecap="round"
          />

          <g
            ref={needleRef}
            style={{ transformOrigin: '110px 110px', transform: 'rotate(-90deg)' }}
          >
            <line
              x1="110"
              y1="110"
              x2="110"
              y2="42"
              stroke="#0f172a"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="110" cy="110" r="7" fill="#0f172a" />
          </g>

          <text x="22" y="118" fontSize="9" fill="#16a34a" fontWeight="600">
            LOW
          </text>
          <text x="102" y="20" fontSize="9" fill="#f59e0b" fontWeight="600">
            MED
          </text>
          <text x="182" y="118" fontSize="9" fill="#ef4444" fontWeight="600">
            HIGH
          </text>
        </svg>

        <div className="absolute inset-x-0 bottom-8 flex flex-col items-center">
          <div className="text-4xl font-bold tracking-tight" style={{ color }}>
            {pctDisplay}%
          </div>
          <div
            className="mt-2 rounded-full px-3 py-1 text-xs font-semibold text-white"
            style={{ backgroundColor: color }}
          >
            {RISK_LABELS[riskTier]}
          </div>
        </div>
      </div>

      <div className="mt-2">
        <div className="mb-1 flex justify-between text-xs text-slate-400">
          <span>0%</span>
          <span>Churn Probability</span>
          <span>100%</span>
        </div>
        <div className="h-2 w-full rounded-full bg-slate-100">
          <div
            className="h-2 rounded-full transition-all duration-700"
            style={{ width: `${pct * 100}%`, backgroundColor: color }}
          />
        </div>
      </div>
    </div>
  )
}