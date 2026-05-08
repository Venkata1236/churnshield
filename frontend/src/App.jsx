import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import AnalyzePage from './pages/AnalyzePage'
import ResultsPage from './pages/ResultsPage'
import HistoryPage from './pages/HistoryPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <nav className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur">
          <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
                <span className="text-sm font-bold">CS</span>
              </div>
              <div className="leading-tight">
                <div className="font-semibold text-slate-900">ChurnShield</div>
                <div className="text-xs text-slate-500">Airtel retention intelligence</div>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-full bg-slate-100 p-1">
              {[
                { to: '/', label: 'Analyze' },
                { to: '/history', label: 'History' },
              ].map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end
                  className={({ isActive }) =>
                    `rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-white text-slate-900 shadow-sm'
                        : 'text-slate-500 hover:text-slate-900'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-10">
          <Routes>
            <Route path="/" element={<AnalyzePage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}