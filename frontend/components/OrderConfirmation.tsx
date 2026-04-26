'use client'

import { useGANGUStore } from '@/lib/store'
import { useState } from 'react'
import { Check, X, Edit3, ShieldCheck, Truck, Sparkles, Loader } from 'lucide-react'

interface OrderConfirmationProps {
  onConfirm: () => void
  onCancel: () => void
  onChangeSelection: () => void
}

export default function OrderConfirmation({ onConfirm, onCancel, onChangeSelection }: OrderConfirmationProps) {
  const { comparison, recommendation } = useGANGUStore()
  const [loading, setLoading] = useState(false)

  if (!comparison || !comparison.products || comparison.products.length === 0) return null

  const selectedIndex = recommendation?.selected_index ?? comparison.recommended_index ?? 0
  const selectedProduct = comparison.products[selectedIndex]
  if (!selectedProduct) return null

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-md"
      style={{ background: 'radial-gradient(ellipse at center, rgba(7, 9, 15, 0.85), rgba(7, 9, 15, 0.95))' }}
      onClick={onCancel}
    >
      <div
        className="relative w-full max-w-lg surface-card p-7 md:p-8 animate-rise"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          onClick={onCancel}
          aria-label="Close"
          className="absolute top-4 right-4 w-9 h-9 rounded-lg bg-white/[0.04] border border-white/10
                     text-slate-400 hover:text-white hover:bg-white/10 flex items-center justify-center transition-all"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="mb-6">
          <span className="pill-amber mb-3">
            <Sparkles className="w-3 h-3" />
            Confirm your order
          </span>
          <h3 className="text-2xl md:text-3xl text-display mt-1">Ready to place this?</h3>
        </div>

        {/* Product summary */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 mb-5">
          <div className="flex items-start gap-4">
            {selectedProduct.image && (
              <div className="w-20 h-20 rounded-xl bg-white/[0.05] border border-white/10 flex-shrink-0 flex items-center justify-center overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={selectedProduct.image}
                  alt={selectedProduct.name}
                  className="w-full h-full object-contain"
                  onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
                />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">Selected</p>
              <p className="font-semibold text-white text-base leading-snug line-clamp-2 mb-2">
                {selectedProduct.name}
              </p>
              <p className="text-3xl font-display font-extrabold gradient-text-warm">₹{selectedProduct.price}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mt-5 pt-4 border-t border-white/5">
            <div>
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">Platform</p>
              <p className="text-sm text-slate-200 font-semibold">{selectedProduct.platform}</p>
            </div>
            {selectedProduct.delivery_time && (
              <div>
                <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1 flex items-center gap-1">
                  <Truck className="w-3 h-3" /> Delivery
                </p>
                <p className="text-sm text-cyan-300 font-semibold">{selectedProduct.delivery_time}</p>
              </div>
            )}
          </div>
        </div>

        {/* Reasoning */}
        {recommendation?.reasoning && (
          <div className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.04] p-4 mb-6">
            <p className="text-[10px] uppercase tracking-widest font-bold text-amber-300 mb-2 inline-flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Why GANGU picked this
            </p>
            <p className="text-sm text-slate-200 leading-relaxed">{recommendation.reasoning}</p>
          </div>
        )}

        {/* Trust line */}
        <p className="text-xs text-slate-500 text-center mb-5 inline-flex items-center gap-1.5 justify-center w-full">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          You'll be charged on <strong className="text-slate-300 mx-1">{selectedProduct.platform}</strong> only after confirming.
        </p>

        {/* Actions */}
        <div className="flex flex-col gap-2.5">
          <button onClick={handleConfirm} disabled={loading} className="btn-primary w-full text-base py-3.5">
            {loading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Placing order…
              </>
            ) : (
              <>
                <Check className="w-5 h-5" strokeWidth={3} />
                Confirm purchase
              </>
            )}
          </button>

          <button onClick={onChangeSelection} disabled={loading} className="btn-secondary w-full">
            <Edit3 className="w-4 h-4" />
            Change option
          </button>
        </div>
      </div>
    </div>
  )
}
