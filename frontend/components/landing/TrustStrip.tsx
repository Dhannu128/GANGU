'use client'

import { Package, Star, MapPin, Bot } from 'lucide-react'

const STATS = [
  { icon: Package, value: '10,000+', label: 'orders placed' },
  { icon: Star,    value: '4.9 / 5',  label: 'family rating' },
  { icon: MapPin,  value: '50+',      label: 'cities served' },
  { icon: Bot,     value: '6',        label: 'AI agents working' },
]

export default function TrustStrip() {
  return (
    <section className="relative max-w-7xl mx-auto px-6 -mt-2 mb-2">
      <div className="surface-card grid grid-cols-2 md:grid-cols-4 divide-x divide-white/5 overflow-hidden">
        {STATS.map((s, i) => {
          const Icon = s.icon
          return (
            <div
              key={i}
              className="px-6 py-7 md:py-9 flex flex-col items-center text-center"
            >
              <Icon className="w-5 h-5 text-amber-300/80 mb-3" strokeWidth={2} />
              <span className="stat-num leading-none">{s.value}</span>
              <span className="text-[11px] uppercase tracking-[0.18em] font-bold text-slate-500 mt-3">
                {s.label}
              </span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
