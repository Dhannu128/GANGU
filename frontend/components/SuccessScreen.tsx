'use client'

import { useGANGUStore } from '@/lib/store'
import { CheckCircle2, Package, Clock, RotateCcw, Sparkles } from 'lucide-react'

interface SuccessScreenProps {
  onNewOrder: () => void
}

export default function SuccessScreen({ onNewOrder }: SuccessScreenProps) {
  const { orderId, comparison, recommendation } = useGANGUStore()
  if (!orderId) return null

  const selectedProduct = comparison?.products[recommendation?.selected_index || 0]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-xl"
      style={{
        background:
          'radial-gradient(ellipse at center, rgba(16, 185, 129, 0.18), rgba(7, 9, 15, 0.96) 60%)',
      }}
    >
      {/* Ambient celebratory glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(10)].map((_, i) => (
          <span
            key={i}
            className="absolute rounded-full opacity-30 animate-float"
            style={{
              left: `${(i * 11) % 100}%`,
              top: `${(i * 17) % 100}%`,
              width: `${8 + (i % 3) * 6}px`,
              height: `${8 + (i % 3) * 6}px`,
              background: i % 2 === 0 ? '#FB923C' : '#A78BFA',
              animationDelay: `${i * 0.4}s`,
              filter: 'blur(2px)',
            }}
          />
        ))}
      </div>

      <div className="relative w-full max-w-md surface-card p-8 text-center animate-rise">
        {/* Success icon */}
        <div className="mb-5 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-emerald-400/30 blur-2xl animate-pulse-soft" />
            <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-2xl">
              <CheckCircle2 className="w-12 h-12 text-white" strokeWidth={2.5} />
            </div>
          </div>
        </div>

        <span className="pill-emerald mb-4 mx-auto">
          <Sparkles className="w-3 h-3" />
          Order placed
        </span>

        <h2 className="text-display text-3xl md:text-4xl mb-2">
          You're all set!
        </h2>
        <p className="text-slate-400 mb-7">Your groceries are on the way.</p>

        {/* Order details */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 mb-6 text-left space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase tracking-widest font-bold text-slate-500">Order ID</span>
            <span className="font-mono text-sm font-semibold text-amber-300">{orderId}</span>
          </div>

          {selectedProduct && (
            <>
              <div className="h-px bg-white/5" />
              <div className="flex items-start justify-between gap-3">
                <span className="text-xs uppercase tracking-widest font-bold text-slate-500 flex-shrink-0 pt-0.5">Item</span>
                <span className="text-sm text-white text-right line-clamp-2 max-w-[60%]">
                  {selectedProduct.name}
                </span>
              </div>

              <div className="h-px bg-white/5" />
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-widest font-bold text-slate-500">Platform</span>
                <span className="text-sm text-slate-200 font-semibold">{selectedProduct.platform}</span>
              </div>

              <div className="h-px bg-white/5" />
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-widest font-bold text-slate-500">Total</span>
                <span className="text-2xl font-display font-extrabold gradient-text-warm">
                  ₹{selectedProduct.price}
                </span>
              </div>

              {selectedProduct.delivery_time && (
                <div className="mt-2 px-3 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-300" />
                  <span className="text-sm font-semibold text-cyan-200">Arriving in {selectedProduct.delivery_time}</span>
                </div>
              )}
            </>
          )}
        </div>

        {/* Actions */}
        <div className="space-y-2.5">
          <button onClick={onNewOrder} className="btn-primary w-full">
            <RotateCcw className="w-4 h-4" />
            Order something else
          </button>
          <button className="btn-secondary w-full">
            <Package className="w-4 h-4" />
            Track this order
          </button>
        </div>

        <p className="mt-6 text-sm text-slate-500">
          Thank you for using <span className="text-amber-300 font-semibold">GANGU</span>
        </p>
      </div>
    </div>
  )
}
