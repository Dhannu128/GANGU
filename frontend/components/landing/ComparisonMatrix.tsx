'use client'

import { Check, X, Mic, ShoppingCart } from 'lucide-react'

const ROWS = [
  { feature: 'Order by speaking',          gangu: true,  others: false },
  { feature: 'Hindi · English · Hinglish', gangu: true,  others: false },
  { feature: 'Searches every platform',    gangu: true,  others: false },
  { feature: 'AI picks the best deal',     gangu: true,  others: false },
  { feature: 'No menus or scrolling',      gangu: true,  others: false },
  { feature: 'Built for elders',           gangu: true,  others: false },
]

export default function ComparisonMatrix() {
  return (
    <section className="relative max-w-7xl mx-auto px-6 py-24 scroll-mt-20">
      <div className="text-center mb-14 max-w-2xl mx-auto">
        <span className="pill-rose mb-3 mx-auto inline-flex">The difference</span>
        <h2 className="text-display text-4xl md:text-5xl mt-2 mb-3">
          Why families switch <br className="hidden md:block" />
          <span className="gradient-text-warm">to GANGU</span>
        </h2>
        <p className="text-slate-400 text-lg">
          Traditional grocery apps were built for thumbs. GANGU was built for voices.
        </p>
      </div>

      <div className="surface-card overflow-hidden">
        {/* Header row */}
        <div className="grid grid-cols-[1.4fr_1fr_1fr] border-b border-white/5">
          <div className="px-6 py-5" />
          <div className="px-4 py-5 flex items-center justify-center gap-2 border-l border-white/5 bg-white/[0.02]">
            <ShoppingCart className="w-4 h-4 text-slate-500" />
            <span className="text-xs uppercase tracking-[0.18em] font-bold text-slate-400">
              Traditional Apps
            </span>
          </div>
          <div className="px-4 py-5 flex items-center justify-center gap-2 border-l border-white/5 bg-gradient-to-b from-amber-500/10 to-transparent">
            <Mic className="w-4 h-4 text-amber-300" />
            <span className="text-xs uppercase tracking-[0.18em] font-bold text-amber-300">
              GANGU
            </span>
          </div>
        </div>

        {/* Rows */}
        {ROWS.map((row, i) => (
          <div
            key={i}
            className={`grid grid-cols-[1.4fr_1fr_1fr] ${
              i !== ROWS.length - 1 ? 'border-b border-white/5' : ''
            }`}
          >
            <div className="px-6 py-5 text-slate-200 font-medium text-sm md:text-base">
              {row.feature}
            </div>
            <div className="px-4 py-5 flex items-center justify-center border-l border-white/5">
              {row.others ? (
                <Check className="w-5 h-5 text-emerald-400" strokeWidth={2.5} />
              ) : (
                <X className="w-5 h-5 text-slate-600" strokeWidth={2.5} />
              )}
            </div>
            <div className="px-4 py-5 flex items-center justify-center border-l border-white/5 bg-gradient-to-b from-amber-500/[0.04] to-transparent">
              {row.gangu ? (
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-glow-sm">
                  <Check className="w-4 h-4 text-white" strokeWidth={3} />
                </div>
              ) : (
                <X className="w-5 h-5 text-slate-600" strokeWidth={2.5} />
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
