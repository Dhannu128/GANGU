'use client'

import { useGANGUStore } from '@/lib/store'
import { Check, Loader, X, ClipboardList, Brain, ListChecks, Search, Scale, BadgeCheck, ShoppingBag, Bell, AlertTriangle } from 'lucide-react'
import { cancelProcessing } from '@/lib/api'
import { useState } from 'react'

const STEP_META: Record<string, { label: string; icon: React.ComponentType<{ className?: string }>; tint: string }> = {
  init:               { label: 'Getting ready',         icon: ClipboardList, tint: 'slate' },
  intent_extraction:  { label: 'Understanding request', icon: Brain,         tint: 'amber' },
  task_planning:      { label: 'Planning tasks',        icon: ListChecks,    tint: 'amber' },
  search:             { label: 'Searching platforms',   icon: Search,        tint: 'cyan' },
  comparison:         { label: 'Comparing products',    icon: Scale,         tint: 'violet' },
  decision:           { label: 'Selecting best option', icon: BadgeCheck,    tint: 'violet' },
  purchase:           { label: 'Processing order',      icon: ShoppingBag,   tint: 'emerald' },
  notification:       { label: 'Sending confirmation',  icon: Bell,          tint: 'emerald' },
  error:              { label: 'Error occurred',        icon: AlertTriangle, tint: 'rose' },
}

const STEP_ORDER = [
  'intent_extraction',
  'task_planning',
  'search',
  'comparison',
  'decision',
  'purchase',
  'notification',
]

export default function AgentTimeline() {
  const {
    agentSteps,
    sessionId,
    isCancelling,
    setCancelling,
    setCancelled,
    abortController,
    pushToast,
  } = useGANGUStore()
  const [cancelError, setCancelError] = useState('')

  const handleCancel = async () => {
    if (!sessionId) return

    // 1) Abort the in-flight HTTP call locally — frees the UI instantly,
    //    no waiting for the backend to finish the current agent.
    abortController?.abort()

    // 2) Optimistically update UI: mark as cancelled now, even before the
    //    backend ack arrives. setCancelled also clears isCancelling +
    //    isProcessing in the store.
    setCancelling(true)
    setCancelError('')

    // 3) Tell the backend so it can .cancel() the running pipeline task
    //    (stops the slow Zepto MCP retries). Fire-and-forget — don't block UI.
    try {
      await cancelProcessing(sessionId)
      setCancelled(true)
      pushToast({ variant: 'info', title: 'Order cancelled', description: 'The pipeline was stopped.' })
    } catch (error) {
      console.error('Cancel error:', error)
      // Still mark cancelled locally — the user expects the UI to update.
      setCancelled(true)
      setCancelError('Cancelled locally — backend may still be cleaning up.')
    }
  }

  // Empty state
  if (agentSteps.length === 0) {
    return (
      <div className="surface-card p-7 animate-fade-in">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Request progress</h3>
          <span className="pill-slate">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
            Idle
          </span>
        </div>

        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <ClipboardList className="w-7 h-7 text-emerald-700" />
          </div>
          <p className="text-base font-semibold text-slate-200 mb-1">Ready when you are</p>
          <p className="text-sm text-slate-500">You will see each check here after making a request.</p>
        </div>

        {/* Skeleton preview */}
        <div className="space-y-2.5 mt-6">
          {STEP_ORDER.slice(0, 4).map((s) => {
            const meta = STEP_META[s]
            const Icon = meta.icon
            return (
              <div key={s} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.02] border border-white/5">
                <div className="w-8 h-8 rounded-lg bg-white/[0.03] border border-white/5 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-slate-600" />
                </div>
                <span className="text-sm text-slate-600 font-medium">{meta.label}</span>
              </div>
            )
          })}
          <p className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold text-center pt-2">+ 3 more checks</p>
        </div>
      </div>
    )
  }

  const stepStatusMap: Record<string, 'processing' | 'complete' | 'error'> = {}
  agentSteps.forEach((s) => {
    stepStatusMap[s.step] = s.status as 'processing' | 'complete' | 'error'
  })

  const completedCount = agentSteps.filter((s) => s.status === 'complete').length
  const totalSteps = STEP_ORDER.length
  const allComplete = completedCount === totalSteps
  const hasError = agentSteps.some((s) => s.status === 'error')
  const progress = Math.round((completedCount / totalSteps) * 100)

  const headerLabel = isCancelling
    ? 'Cancelling…'
    : hasError
    ? 'Issue occurred'
    : allComplete
    ? 'All checks done'
    : 'Working'

  const headerPill = isCancelling
    ? 'pill-rose'
    : hasError
    ? 'pill-rose'
    : allComplete
    ? 'pill-emerald'
    : 'pill-amber'

  return (
    <div className="surface-card p-7 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-400">Request progress</h3>
        <span className={headerPill}>
          {!allComplete && !hasError && !isCancelling && (
            <span className="w-1.5 h-1.5 rounded-full bg-amber-300 animate-pulse"></span>
          )}
          {allComplete && <Check className="w-3 h-3" />}
          {hasError && <AlertTriangle className="w-3 h-3" />}
          {headerLabel}
        </span>
      </div>

      {/* Cancel button */}
      {!allComplete && !hasError && !isCancelling && (
        <button
          onClick={handleCancel}
          className="w-full mb-5 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30
                     hover:bg-rose-500/20 hover:border-rose-500/50 text-rose-300 text-sm font-semibold
                     flex items-center justify-center gap-2 transition-all"
        >
          <X className="w-4 h-4" />
          Cancel order
        </button>
      )}

      {isCancelling && (
        <div className="w-full mb-5 px-4 py-2.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-200 text-sm font-bold flex items-center justify-center gap-2">
          <X className="w-4 h-4 animate-spin" />
          Cancelling order…
        </div>
      )}

      {cancelError && (
        <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
          {cancelError}
        </div>
      )}

      {/* Progress */}
      <div className="mb-6">
        <div className="flex justify-between items-end mb-2">
          <span className="text-xs text-slate-500 font-medium">
            {completedCount} of {totalSteps} checks
          </span>
          <span className="text-xl font-display font-extrabold text-emerald-800">
            {progress}%
          </span>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden border border-white/5">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out shimmer"
            style={{
              width: `${progress}%`,
              background: '#2f6b4f',
            }}
          />
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        <div className="absolute left-[19px] top-2 bottom-2 w-px bg-emerald-900/15" />

        <div className="space-y-2.5">
          {STEP_ORDER.map((stepKey) => {
            const stepData = agentSteps.find((s) => s.step === stepKey)
            const status = stepStatusMap[stepKey]
            const isComplete = status === 'complete'
            const isActive = status === 'processing'
            const isPending = !stepData || status === undefined
            const meta = STEP_META[stepKey]
            const Icon = meta.icon

            return (
              <div key={stepKey} className="relative flex items-start gap-3">
                <div className="relative z-10 flex-shrink-0">
                  {isComplete && (
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center">
                      <Check className="w-5 h-5 text-emerald-300" strokeWidth={3} />
                    </div>
                  )}
                  {isActive && (
                    <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/50 flex items-center justify-center shadow-glow-sm">
                      <Loader className="w-5 h-5 text-amber-300 animate-spin" strokeWidth={2.5} />
                    </div>
                  )}
                  {isPending && (
                    <div className="w-10 h-10 rounded-xl bg-white/[0.03] border border-white/10 flex items-center justify-center">
                      <Icon className="w-4 h-4 text-slate-600" />
                    </div>
                  )}
                </div>

                <div className="flex-grow pt-0.5">
                  <div
                    className={`px-3.5 py-2.5 rounded-xl border transition-all ${
                      isComplete
                        ? 'bg-emerald-500/[0.04] border-emerald-500/20'
                        : isActive
                        ? 'bg-amber-500/[0.06] border-amber-500/30'
                        : 'bg-transparent border-transparent'
                    }`}
                  >
                    <p
                      className={`text-sm font-semibold ${
                        isComplete ? 'text-emerald-200' : isActive ? 'text-amber-200' : 'text-slate-500'
                      }`}
                    >
                      {meta.label}
                    </p>
                    {stepData?.message && (isComplete || isActive) && (
                      <p className="text-xs text-slate-400 mt-0.5 line-clamp-2 leading-relaxed">{stepData.message}</p>
                    )}

                    {stepKey === 'search' && isComplete && stepData?.data?.platforms && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {stepData.data.platforms.map((p: string, i: number) => (
                          <span key={i} className="pill-cyan text-[10px] px-2 py-0.5">
                            {p}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
