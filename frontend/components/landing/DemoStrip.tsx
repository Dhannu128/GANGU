'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Mic, Check, Loader, Sparkles, Star, Truck, ArrowRight, Brain, Search, Scale } from 'lucide-react'

interface DemoStage {
  transcription: string
  agentIndex: number
  showProducts: boolean
  recommendedIndex: number
}

const STAGES: DemoStage[] = [
  { transcription: '', agentIndex: -1, showProducts: false, recommendedIndex: 0 },
  { transcription: 'Doodh khatam ho gaya, le aao', agentIndex: 0, showProducts: false, recommendedIndex: 0 },
  { transcription: 'Doodh khatam ho gaya, le aao', agentIndex: 1, showProducts: false, recommendedIndex: 0 },
  { transcription: 'Doodh khatam ho gaya, le aao', agentIndex: 2, showProducts: false, recommendedIndex: 0 },
  { transcription: 'Doodh khatam ho gaya, le aao', agentIndex: 3, showProducts: true, recommendedIndex: 1 },
]

const AGENTS = [
  { label: 'Understanding', icon: Brain },
  { label: 'Searching', icon: Search },
  { label: 'Comparing', icon: Scale },
  { label: 'Picked best', icon: Sparkles },
]

const PRODUCTS = [
  { platform: 'Zepto', name: 'Amul Taaza Toned Milk 1 L', price: 64, rating: 4.6, eta: '10 min' },
  { platform: 'Swiggy Instamart', name: 'Amul Gold Full Cream 1 L', price: 62, rating: 4.5, eta: '15 min' },
]

export default function DemoStrip() {
  const [stage, setStage] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setStage((s) => (s + 1) % STAGES.length)
    }, 2400)
    return () => clearInterval(id)
  }, [])

  const cur = STAGES[stage]

  return (
    <section className="relative max-w-7xl mx-auto px-6 py-12 md:py-16">
      <div className="surface-card relative p-6 md:p-10 overflow-hidden">
        {/* Ambient glow */}
        <div
          className="absolute inset-0 pointer-events-none opacity-60"
          style={{
            background:
              'radial-gradient(ellipse 700px 300px at 20% 20%, rgba(251, 146, 60, 0.10), transparent 60%), radial-gradient(ellipse 700px 300px at 80% 80%, rgba(139, 92, 246, 0.10), transparent 60%)',
          }}
        />

        <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          {/* LEFT — voice + transcription */}
          <div>
            <span className="pill-amber mb-4">
              <Sparkles className="w-3 h-3" />
              Live demo
            </span>
            <h3 className="text-display text-3xl md:text-4xl mb-3">See it in motion</h3>
            <p className="text-slate-400 mb-7 leading-relaxed">
              No signup needed to peek. Watch GANGU listen, understand, and pick the best deal.
            </p>

            <div className="flex items-center gap-5">
              <div className="relative">
                <span
                  className={`absolute inset-0 rounded-full transition-opacity ${
                    cur.agentIndex >= 0 ? 'opacity-100 animate-ping bg-rose-500/30' : 'opacity-0'
                  }`}
                />
                <div
                  className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
                    cur.agentIndex >= 0
                      ? 'bg-gradient-to-br from-rose-500 to-rose-700 shadow-glow-sm'
                      : 'bg-gradient-to-br from-amber-400 to-orange-600 shadow-glow-sm'
                  }`}
                >
                  <Mic className="w-9 h-9 text-white" />
                </div>
              </div>

              <div className="flex-1 min-w-0">
                {cur.transcription ? (
                  <div className="glass rounded-2xl px-4 py-3 animate-fade-in">
                    <p className="text-[10px] text-amber-300 uppercase tracking-widest font-bold mb-1">
                      You said
                    </p>
                    <p className="text-white font-medium">{cur.transcription}</p>
                  </div>
                ) : (
                  <div className="glass rounded-2xl px-4 py-3 opacity-50">
                    <p className="text-sm text-slate-500 italic">Waiting for your voice…</p>
                  </div>
                )}
              </div>
            </div>

            {/* Mini timeline */}
            <div className="mt-7 space-y-2">
              {AGENTS.map((a, i) => {
                const isComplete = cur.agentIndex > i
                const isActive = cur.agentIndex === i
                const Icon = a.icon
                return (
                  <div
                    key={i}
                    className={`flex items-center gap-3 px-3 py-2 rounded-xl border transition-all ${
                      isComplete
                        ? 'border-emerald-500/25 bg-emerald-500/[0.04]'
                        : isActive
                        ? 'border-amber-500/35 bg-amber-500/[0.06]'
                        : 'border-white/5 bg-white/[0.015]'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                        isComplete
                          ? 'bg-emerald-500/15 border border-emerald-500/40'
                          : isActive
                          ? 'bg-amber-500/15 border border-amber-500/50'
                          : 'bg-white/5 border border-white/10'
                      }`}
                    >
                      {isComplete ? (
                        <Check className="w-3.5 h-3.5 text-emerald-300" strokeWidth={3} />
                      ) : isActive ? (
                        <Loader className="w-3.5 h-3.5 text-amber-300 animate-spin" />
                      ) : (
                        <Icon className="w-3.5 h-3.5 text-slate-600" />
                      )}
                    </div>
                    <span
                      className={`text-sm font-semibold ${
                        isComplete ? 'text-emerald-200' : isActive ? 'text-amber-200' : 'text-slate-500'
                      }`}
                    >
                      {a.label}
                    </span>
                  </div>
                )
              })}
            </div>

            <Link href="/signup" className="btn-primary mt-7 inline-flex">
              Try the real thing
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* RIGHT — mini product cards */}
          <div className="relative">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-3">
              {cur.showProducts ? 'Best options found' : 'Searching across platforms…'}
            </p>
            <div className="space-y-3">
              {PRODUCTS.map((p, i) => {
                const visible = cur.showProducts
                const isReco = i === cur.recommendedIndex
                return (
                  <div
                    key={i}
                    className={`relative surface-card p-4 transition-all duration-500 ${
                      visible ? 'opacity-100 translate-y-0' : 'opacity-30 translate-y-2'
                    } ${isReco && visible ? 'border-amber-500/50' : ''}`}
                    style={{ transitionDelay: `${i * 100}ms` }}
                  >
                    {isReco && visible && (
                      <span className="absolute -top-2.5 left-3 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold text-ink-950 bg-gradient-to-r from-amber-300 to-orange-400">
                        <Sparkles className="w-2.5 h-2.5" strokeWidth={3} />
                        Best pick
                      </span>
                    )}
                    <div className="flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-xs text-slate-500 font-semibold">{p.platform}</p>
                        <p className="text-sm font-semibold text-white truncate">{p.name}</p>
                        <div className="mt-1.5 flex items-center gap-2">
                          <span className="inline-flex items-center gap-1 text-[11px] text-amber-300 font-semibold">
                            <Star className="w-3 h-3 fill-amber-300" /> {p.rating}
                          </span>
                          <span className="inline-flex items-center gap-1 text-[11px] text-cyan-300 font-semibold">
                            <Truck className="w-3 h-3" /> {p.eta}
                          </span>
                        </div>
                      </div>
                      <p className="text-2xl font-display font-extrabold text-white tracking-tight">
                        ₹{p.price}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
