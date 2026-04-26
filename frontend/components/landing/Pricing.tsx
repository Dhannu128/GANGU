'use client'

import Link from 'next/link'
import { Check, Sparkles } from 'lucide-react'

interface Plan {
  name: string
  tagline: string
  price: string
  period: string
  features: string[]
  cta: string
  href: string
  highlight?: boolean
}

const PLANS: Plan[] = [
  {
    name: 'Free',
    tagline: 'Try GANGU with no commitment.',
    price: '₹0',
    period: 'first 5 orders',
    features: [
      'Voice ordering in Hindi · English · Hinglish',
      'All 6 AI agents',
      'Search across Zepto + Amazon',
      'COD or UPI checkout',
    ],
    cta: 'Start free',
    href: '/signup',
  },
  {
    name: 'Family',
    tagline: 'For households who shop weekly.',
    price: '₹99',
    period: '/ month',
    features: [
      'Everything in Free',
      'Unlimited orders',
      'Saved shopping lists',
      'Up to 4 family members',
      'Spending limits & wallet top-up',
      'Priority delivery slots',
    ],
    cta: 'Get Family',
    href: '/signup',
    highlight: true,
  },
  {
    name: 'Lifetime',
    tagline: 'One payment. Forever.',
    price: '₹999',
    period: 'one time',
    features: [
      'Everything in Family',
      'Lifetime unlimited orders',
      'Early access to new platforms',
      'Direct WhatsApp support',
    ],
    cta: 'Buy lifetime',
    href: '/signup',
  },
]

export default function Pricing() {
  return (
    <section id="pricing" className="relative max-w-7xl mx-auto px-6 py-24 scroll-mt-20">
      <div className="text-center mb-14 max-w-2xl mx-auto">
        <span className="pill-emerald mb-3 mx-auto inline-flex">Simple pricing</span>
        <h2 className="text-display text-4xl md:text-5xl mt-2 mb-3">
          Pay only for what your <br className="hidden md:block" />
          <span className="gradient-text-warm">family actually uses</span>
        </h2>
        <p className="text-slate-400 text-lg">No asterisks. No hidden fees. Cancel anytime.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {PLANS.map((plan) => (
          <article
            key={plan.name}
            className={`surface-card relative p-7 md:p-8 flex flex-col ${
              plan.highlight ? 'border-amber-500/45' : ''
            }`}
            style={
              plan.highlight
                ? {
                    background:
                      'linear-gradient(180deg, rgba(251,146,60,0.10) 0%, rgba(14,20,36,0.78) 100%)',
                    boxShadow:
                      '0 30px 80px -25px rgba(251, 146, 60, 0.35), inset 0 1px 0 rgba(251, 146, 60, 0.2)',
                  }
                : undefined
            }
          >
            {plan.highlight && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[10px] font-bold text-ink-950 bg-gradient-to-r from-amber-300 to-orange-400 shadow-glow-sm">
                  <Sparkles className="w-3 h-3" strokeWidth={3} />
                  Most popular
                </span>
              </div>
            )}

            <div className="mb-7">
              <h3 className="text-display text-2xl mb-2 tracking-tight">{plan.name}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{plan.tagline}</p>
            </div>

            <div className="mb-7 flex items-baseline gap-2">
              <span className="text-5xl font-display font-extrabold text-white tracking-tight">
                {plan.price}
              </span>
              <span className="text-sm text-slate-500 font-medium">{plan.period}</span>
            </div>

            <ul className="space-y-3 mb-8 flex-1">
              {plan.features.map((f, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-300 leading-relaxed">
                  <span
                    className={`flex-shrink-0 mt-0.5 w-5 h-5 rounded-full flex items-center justify-center ${
                      plan.highlight
                        ? 'bg-amber-500/20 border border-amber-500/40'
                        : 'bg-emerald-500/15 border border-emerald-500/30'
                    }`}
                  >
                    <Check
                      className={`w-3 h-3 ${plan.highlight ? 'text-amber-300' : 'text-emerald-300'}`}
                      strokeWidth={3}
                    />
                  </span>
                  {f}
                </li>
              ))}
            </ul>

            <Link
              href={plan.href}
              className={`${plan.highlight ? 'btn-primary' : 'btn-secondary'} w-full`}
            >
              {plan.cta}
            </Link>
          </article>
        ))}
      </div>

      <p className="text-center text-xs text-slate-500 mt-8">
        Prices in Indian Rupees, inclusive of GST. Platform delivery charges (where applicable) are passed through unchanged.
      </p>
    </section>
  )
}
