'use client'

import { useMemo, useState } from 'react'
import { useGANGUStore, type PastOrder } from '@/lib/store'
import { Package, Truck, ShieldCheck, ChevronRight, Check, RotateCcw, Filter, Calendar } from 'lucide-react'

const STATUS_META: Record<PastOrder['status'], { label: string; pill: string }> = {
  delivered:   { label: 'Delivered',   pill: 'pill-emerald' },
  in_transit:  { label: 'In transit',  pill: 'pill-cyan' },
  cancelled:   { label: 'Cancelled',   pill: 'pill-rose' },
}

export default function OrdersPage() {
  const { pastOrders } = useGANGUStore()
  const [platformFilter, setPlatformFilter] = useState<string>('all')
  const [expanded, setExpanded] = useState<string | null>(null)

  const platforms = useMemo(
    () => ['all', ...Array.from(new Set(pastOrders.map((o) => o.platform)))],
    [pastOrders]
  )

  const filtered = pastOrders.filter((o) => platformFilter === 'all' || o.platform === platformFilter)

  const totalSpent = filtered.reduce((s, o) => s + o.total, 0)

  return (
    <main className="min-h-screen pb-12">
      <div className="max-w-5xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <header className="mb-8">
          <span className="pill-amber mb-3 inline-flex">
            <Package className="w-3 h-3" />
            Order history
          </span>
          <h1 className="text-display text-3xl md:text-4xl mb-2">Past orders</h1>
          <p className="text-slate-400">
            {filtered.length} {filtered.length === 1 ? 'order' : 'orders'}
            <span className="text-slate-700 mx-2">·</span>
            <span className="text-slate-300 font-semibold">₹{totalSpent}</span> total
          </p>
        </header>

        {/* Filter bar */}
        <div className="surface-card p-4 mb-5 flex flex-wrap items-center gap-3">
          <span className="text-xs uppercase tracking-widest font-bold text-slate-500 inline-flex items-center gap-1.5">
            <Filter className="w-3 h-3" />
            Platform
          </span>
          {platforms.map((p) => (
            <button
              key={p}
              onClick={() => setPlatformFilter(p)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                platformFilter === p
                  ? 'bg-amber-500/15 border-amber-500/45 text-amber-200'
                  : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
              }`}
            >
              {p === 'all' ? 'All platforms' : p}
            </button>
          ))}
        </div>

        {/* Orders list */}
        {filtered.length === 0 ? (
          <div className="surface-card p-10 text-center">
            <Package className="w-10 h-10 mx-auto mb-4 text-slate-700" />
            <p className="text-slate-400">No orders yet. Start with your first one!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((order) => {
              const isOpen = expanded === order.id
              const statusMeta = STATUS_META[order.status]
              return (
                <article
                  key={order.id}
                  className={`surface-card transition-all ${isOpen ? 'border-amber-500/30' : ''}`}
                >
                  <button
                    onClick={() => setExpanded(isOpen ? null : order.id)}
                    className="w-full text-left p-5 grid grid-cols-12 gap-3 items-center"
                  >
                    <div className="col-span-12 md:col-span-2">
                      <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1 inline-flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        Date
                      </p>
                      <p className="text-sm font-semibold text-slate-200">{order.date}</p>
                      <p className="text-[10px] text-slate-600 font-mono mt-0.5">{order.id}</p>
                    </div>

                    <div className="col-span-12 md:col-span-5">
                      <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">
                        Item
                      </p>
                      <p className="text-sm font-semibold text-white line-clamp-1">
                        {order.itemSummary}
                      </p>
                    </div>

                    <div className="col-span-4 md:col-span-2">
                      <span className="pill-slate">
                        {order.platform === 'Amazon' ? <Package className="w-3 h-3" /> : <Truck className="w-3 h-3" />}
                        {order.platform}
                      </span>
                    </div>

                    <div className="col-span-4 md:col-span-1 text-right md:text-left">
                      <p className="text-base font-display font-extrabold gradient-text-warm">₹{order.total}</p>
                    </div>

                    <div className="col-span-3 md:col-span-1">
                      <span className={statusMeta.pill}>
                        {order.status === 'delivered' && <Check className="w-3 h-3" />}
                        {statusMeta.label}
                      </span>
                    </div>

                    <div className="col-span-1 flex justify-end">
                      <ChevronRight
                        className={`w-4 h-4 text-slate-500 transition-transform ${
                          isOpen ? 'rotate-90 text-amber-300' : ''
                        }`}
                      />
                    </div>
                  </button>

                  {isOpen && (
                    <div className="px-5 pb-5 pt-1 border-t border-white/5 animate-fade-in">
                      <p className="text-xs uppercase tracking-widest font-bold text-slate-500 mb-3 mt-4 inline-flex items-center gap-1.5">
                        <ShieldCheck className="w-3 h-3" />
                        Pipeline replay
                      </p>
                      <div className="space-y-2">
                        {[
                          'Understanding request',
                          'Searching platforms',
                          'Comparing products',
                          'Selected best option',
                          'Order placed',
                        ].map((step, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-3 px-3 py-2 rounded-xl bg-emerald-500/[0.04] border border-emerald-500/20"
                          >
                            <div className="w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center">
                              <Check className="w-3.5 h-3.5 text-emerald-300" strokeWidth={3} />
                            </div>
                            <span className="text-sm text-emerald-200 font-semibold">{step}</span>
                          </div>
                        ))}
                      </div>

                      <div className="mt-5 flex flex-wrap gap-2">
                        <button className="btn-primary text-sm">
                          <RotateCcw className="w-4 h-4" />
                          Re-order
                        </button>
                        <button className="btn-secondary text-sm">View invoice</button>
                        <button className="btn-ghost text-sm">Report issue</button>
                      </div>
                    </div>
                  )}
                </article>
              )
            })}
          </div>
        )}
      </div>
    </main>
  )
}
