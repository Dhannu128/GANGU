'use client'

import { useGANGUStore } from '@/lib/store'
import { Repeat } from 'lucide-react'

interface QuickReorderProps {
  onPick: (item: string) => void
}

export default function QuickReorder({ onPick }: QuickReorderProps) {
  const { pastOrders } = useGANGUStore()

  // Top 3 most-ordered (by appearance frequency)
  const counts = new Map<string, number>()
  pastOrders.forEach((o) => {
    o.itemSummary.split('·').forEach((part) => {
      const key = part.trim()
      if (key) counts.set(key, (counts.get(key) || 0) + 1)
    })
  })
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3)

  if (top.length === 0) return null

  return (
    <div className="surface-card p-5 mt-4">
      <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-3 inline-flex items-center gap-2">
        <Repeat className="w-3.5 h-3.5" />
        Quick re-order
      </h3>
      <div className="flex flex-col gap-2">
        {top.map(([item], i) => (
          <button
            key={i}
            onClick={() => onPick(`Order ${item}`)}
            className="text-left px-3.5 py-2.5 rounded-xl bg-white/[0.04] border border-white/10
                       hover:border-amber-500/40 hover:bg-amber-500/[0.06] hover:text-white
                       text-slate-300 text-sm font-medium transition-all"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  )
}
