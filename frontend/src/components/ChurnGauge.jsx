import { useEffect, useRef } from 'react'

const RISK_COLORS = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
}

const RISK_LABELS = {
  LOW: 'Low Risk',
  MEDIUM: 'Medium Risk',
  HIGH: 'High Risk',
}

export default function ChurnGauge({ probability = 0, riskTier = 'LOW' }) {
  const needleRef = useRef(null)

  const pct = Math.min(Math.max(probability, 0), 1)
  const angle = -90 + pct * 180 // -90deg (left) to +90deg (right)
  const color = RISK_COLORS[riskTier] || '#22c55e'
  const pctDisplay = (pct * 100).toFixed(1)

  useEffect(() => {
    if (needleRef.current) {
      needleRef.current.style.transition = 'transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)'
      needleRef.current.style.transform = `rotate(${angle}deg)`
    }
  }, [angle])

  // Arc path helper
  const describeArc = (cx, cy, r, startAngle, endAngle) => {
    const toRad = (deg) => (deg * Math.PI) / 180
    const x1 = cx + r * Math.cos(toRad(startAngle))
    const y1 = cy + r * Math.sin(toRad(startAngle))
    const x2 = cx + r * Math.cos(toRad(endAngle))
    const y2 = cy + r * Math.sin(toRad(endAngle))
    return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col items-center">
      <h3 className="font-semibold text-gray-800 mb-4">Churn Risk Score</h3>

      <div className="relative w-64 h-36">
        <svg viewBox="0 0 200 110" className="w-full h-full">
          {/* Background track */}
          <path
            d={describeArc(100, 100, 75, -180, 0)}
            fill="none"
            stroke="#f3f4f6"
            strokeWidth="18"
            strokeLinecap="round"
          />

          {/* Green zone 0–40% */}
          <path
            d={describeArc(100, 100, 75, -180, -108)}
            fill="none"
            stroke="#22c55e"
            strokeWidth="18"
            opacity="0.85"
          />

          {/* Yellow zone 40–70% */}
          <path
            d={describeArc(100, 100, 75, -108, -54)}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="18"
            opacity="0.85"
          />

          {/* Red zone 70–100% */}
          <path
            d={describeArc(100, 100, 75, -54, 0)}
            fill="none"
            stroke="#ef4444"
            strokeWidth="18"
            opacity="0.85"
          />

          {/* Needle */}
          <g
            ref={needleRef}
            style={{ transformOrigin: '100px 100px', transform: 'rotate(-90deg)' }}
          >
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="32"
              stroke="#1e293b"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill="#1e293b" />
          </g>

          {/* Zone labels */}
          <text x="22" y="108" fontSize="8" fill="#22c55e" fontWeight="600">LOW</text>
          <text x="88" y="20" fontSize="8" fill="#f59e0b" fontWeight="600">MED</text>
          <text x="163" y="108" fontSize="8" fill="#ef4444" fontWeight="600">HIGH</text>
        </svg>

        {/* Center percentage */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center">
          <span className="text-3xl font-bold" style={{ color }}>
            {pctDisplay}%
          </span>
        </div>
      </div>

      {/* Risk badge */}
      <div
        className="mt-3 px-4 py-1.5 rounded-full text-sm font-semibold text-white"
        style={{ backgroundColor: color }}
      >
        {RISK_LABELS[riskTier]}
      </div>

      {/* Probability bar */}
      <div className="w-full mt-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>0%</span>
          <span>Churn Probability</span>
          <span>100%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-1000"
            style={{ width: `${pct * 100}%`, backgroundColor: color }}
          />
        </div>
      </div>
    </div>
  )
}