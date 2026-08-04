'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface FAQItem {
  q: string
  a: string
}

const FAQS: FAQItem[] = [
  {
    q: 'Is GANGU safe to use for real money orders?',
    a: 'Every order passes through six AI safety policies — confidence threshold, stock verification, price sanity, platform reputation, elderly safeguards, and explicit confirmation. You always see and approve the final order before any payment. We never charge until you tap Confirm.',
  },
  {
    q: 'Which platforms can GANGU shop from?',
    a: 'Today we search Swiggy Instamart, Zepto, and Amazon. BigBasket, JioMart, and Dunzo are rolling out through 2026. You can also pin a preferred platform in Settings if you only want to use one.',
  },
  {
    q: 'Will it understand my accent and the way I speak?',
    a: 'Yes. GANGU is trained for natural Hindi, English, and Hinglish — including the way most Indian elders mix them ("doodh khatam ho gaya" works as well as "we are out of milk"). We also handle local item names like atta, dal, kachori, methi.',
  },
  {
    q: 'Can my grandchild manage my account on my behalf?',
    a: 'Absolutely. Invite them under Settings → Family. They can review orders, top up the wallet, and set spending limits — without ever having full control of your account. You stay in charge.',
  },
  {
    q: 'What happens if the order is wrong or doesn\'t arrive?',
    a: 'You can cancel any in-flight order with one tap from the Agent Pipeline panel. After delivery, refunds are handled directly with the platform — and our support team is one tap away on WhatsApp if you need help raising a complaint.',
  },
  {
    q: 'How is my voice data used?',
    a: 'Your voice is transcribed once and immediately discarded — we never store recordings. Only the transcribed text is logged for the agents to work on, and that log is auto-deleted after 30 days. We never sell or share your data.',
  },
]

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section id="faq" className="relative max-w-3xl mx-auto px-6 py-24 scroll-mt-20">
      <div className="text-center mb-12">
        <span className="pill-cyan mb-3 mx-auto inline-flex">Common questions</span>
        <h2 className="text-display text-4xl md:text-5xl mt-2">
          Things <span className="gradient-text">people ask</span>
        </h2>
      </div>

      <div className="space-y-3">
        {FAQS.map((item, i) => {
          const isOpen = openIndex === i
          return (
            <div
              key={i}
              className={`surface-card transition-all ${isOpen ? 'border-amber-500/30' : ''}`}
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : i)}
                className="w-full flex items-center justify-between gap-4 p-5 md:p-6 text-left"
              >
                <span className={`font-semibold text-base ${isOpen ? 'text-white' : 'text-slate-200'}`}>
                  {item.q}
                </span>
                <ChevronDown
                  className={`flex-shrink-0 w-5 h-5 transition-transform duration-300 ${
                    isOpen ? 'rotate-180 text-amber-300' : 'text-slate-500'
                  }`}
                />
              </button>
              <div
                className={`grid transition-all duration-300 ease-out ${
                  isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                }`}
              >
                <div className="overflow-hidden">
                  <p className="px-5 md:px-6 pb-5 md:pb-6 text-slate-400 leading-relaxed text-[15px]">
                    {item.a}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
