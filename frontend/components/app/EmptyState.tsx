'use client'

import { Mic } from 'lucide-react'

interface EmptyStateProps {
  onTry: (prompt: string) => void
}

const SAMPLE = 'doodh khatam ho gaya'

export default function EmptyState({ onTry }: EmptyStateProps) {
  return (
    <div className="surface-card p-7 md:p-9 text-center max-w-xl mx-auto mt-8">
      <div className="w-14 h-14 mx-auto mb-5 rounded-full bg-[#ddf3f0] border border-[#9ed7d0] flex items-center justify-center">
        <Mic className="w-7 h-7 text-[#0f766e]" />
      </div>
      <h3 className="text-display text-2xl md:text-3xl mb-2">Not sure what to say?</h3>
      <p className="text-slate-400 mb-6">Start with a simple household need:</p>
      <button
        onClick={() => onTry(SAMPLE)}
        className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl border border-amber-500/40 bg-amber-500/[0.06] hover:bg-amber-500/[0.10] transition-all group"
      >
        <Mic className="w-5 h-5 text-amber-300 group-hover:scale-110 transition-transform" />
        <span className="text-amber-100 font-semibold">&ldquo;{SAMPLE}&rdquo;</span>
      </button>
    </div>
  )
}
