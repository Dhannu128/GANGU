'use client'

import { Quote } from 'lucide-react'

interface Testimonial {
  name: string
  city: string
  initials: string
  gradient: string
  quote: string
  age: number
}

const TESTIMONIALS: Testimonial[] = [
  {
    name: 'Lata aunty',
    city: 'Indore',
    initials: 'LA',
    gradient: 'from-amber-400 to-orange-600',
    age: 67,
    quote:
      'Pehle beta order karta tha. Ab main khud bol deti hoon — "doodh aur bread". Dus minute mein ghar pe. Bahut aasaan hai.',
  },
  {
    name: 'Ramesh uncle',
    city: 'Pune',
    initials: 'RU',
    gradient: 'from-violet-400 to-fuchsia-600',
    age: 71,
    quote:
      'I just speak English at it. No typing, no scrolling. It picks the cheapest option and tells me why. Trustworthy.',
  },
  {
    name: 'Geeta ji',
    city: 'Lucknow',
    initials: 'GJ',
    gradient: 'from-cyan-400 to-emerald-600',
    age: 64,
    quote:
      'मेरे पोते ने डाला था। अब हफ्ते भर का सामान एक बार में बोल देती हूँ — सब अपने आप आ जाता है। अच्छा लगता है।',
  },
]

export default function Testimonials() {
  return (
    <section className="relative max-w-7xl mx-auto px-6 py-24">
      <div className="text-center mb-12 max-w-2xl mx-auto">
        <span className="pill-amber mb-3 mx-auto inline-flex">Real users · real kitchens</span>
        <h2 className="text-display text-4xl md:text-5xl mt-2 mb-3">
          Built for the way <br className="hidden md:block" />
          <span className="gradient-text-warm">India actually shops</span>
        </h2>
        <p className="text-slate-400 text-lg">
          We talked to elders in Indore, Pune, Lucknow — and built around how they speak, not how apps usually demand.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {TESTIMONIALS.map((t, i) => (
          <article key={i} className="surface-card p-7 relative">
            <Quote className="absolute top-6 right-6 w-6 h-6 text-amber-500/20" strokeWidth={1.5} />

            <p className="text-slate-200 leading-relaxed text-[15px] mb-7">{t.quote}</p>

            <div className="flex items-center gap-3 pt-5 border-t border-white/5">
              <div
                className={`w-11 h-11 rounded-full bg-gradient-to-br ${t.gradient} flex items-center justify-center font-display font-extrabold text-ink-950 text-sm shadow-glow-sm`}
              >
                {t.initials}
              </div>
              <div>
                <p className="font-semibold text-white text-sm leading-tight">{t.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {t.city} <span className="text-slate-700 mx-1">·</span> Age {t.age}
                </p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
