'use client'

import { useGANGUStore } from '@/lib/store'
import { Calendar } from 'lucide-react'

export default function TodayPanel() {
  const { pastOrders } = useGANGUStore()

  const today = new Date().toISOString().slice(0, 10)
  const todayOrders = pastOrders.filter((o) => o.date === today)
  const total = todayOrders.reduce((s, o) => s + o.total, 0)

  return (
    <div className="surface-card p-5 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400 inline-flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5" />
          Today
        </h3>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">Orders</p>
          <p className="text-2xl font-display font-extrabold text-white">{todayOrders.length}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">Spent</p>
          <p className="text-2xl font-display font-extrabold text-emerald-800">₹{total}</p>
        </div>
      </div>
    </div>
  )
}
