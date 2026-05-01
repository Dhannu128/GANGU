'use client'

import { useEffect } from 'react'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react'
import { useGANGUStore, type Toast as ToastType } from '@/lib/store'

const ICONS = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
}

const STYLES = {
  success: 'border-emerald-500/40 bg-emerald-500/[0.08] text-emerald-200',
  error:   'border-rose-500/40    bg-rose-500/[0.08]    text-rose-200',
  info:    'border-amber-500/40   bg-amber-500/[0.08]   text-amber-200',
}

function ToastItem({ toast }: { toast: ToastType }) {
  const dismissToast = useGANGUStore((s) => s.dismissToast)
  const Icon = ICONS[toast.variant]

  useEffect(() => {
    const id = setTimeout(() => dismissToast(toast.id), 3500)
    return () => clearTimeout(id)
  }, [toast.id, dismissToast])

  return (
    <div
      className={`glass-strong border ${STYLES[toast.variant]} rounded-2xl px-4 py-3.5 flex items-start gap-3 min-w-[280px] max-w-sm shadow-card animate-rise`}
      role="status"
    >
      <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" strokeWidth={2} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold leading-tight">{toast.title}</p>
        {toast.description && (
          <p className="text-xs text-slate-300/80 mt-1 leading-relaxed">{toast.description}</p>
        )}
      </div>
      <button
        onClick={() => dismissToast(toast.id)}
        aria-label="Dismiss"
        className="flex-shrink-0 text-slate-400 hover:text-white transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

export default function ToastViewport() {
  const toasts = useGANGUStore((s) => s.toasts)
  if (toasts.length === 0) return null
  return (
    <div className="fixed top-5 right-5 z-[100] flex flex-col gap-2 pointer-events-auto">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  )
}
