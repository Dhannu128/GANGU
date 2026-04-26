'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Logo from '@/components/Logo'
import { ShieldCheck, Sparkles } from 'lucide-react'

const QUOTES = [
  {
    text: '"Pehle beta order karta tha. Ab main khud bol deti hoon."',
    author: 'Lata aunty · Indore',
  },
  {
    text: '"मेरे पोते ने डाला था। अब हफ्ते भर का सामान एक बार में बोल देती हूँ।"',
    author: 'Geeta ji · Lucknow',
  },
  {
    text: '"It picks the cheapest option and tells me why. Trustworthy."',
    author: 'Ramesh uncle · Pune',
  },
]

interface AuthShellProps {
  title: string
  subtitle: string
  children: React.ReactNode
}

export default function AuthShell({ title, subtitle, children }: AuthShellProps) {
  const [quoteIndex, setQuoteIndex] = useState(0)

  useEffect(() => {
    const id = setInterval(() => {
      setQuoteIndex((i) => (i + 1) % QUOTES.length)
    }, 5500)
    return () => clearInterval(id)
  }, [])

  const quote = QUOTES[quoteIndex]

  return (
    <main className="min-h-screen relative grid grid-cols-1 lg:grid-cols-2">
      {/* LEFT — brand panel */}
      <aside className="relative hidden lg:flex flex-col justify-between p-12 overflow-hidden border-r border-white/5">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 700px 500px at 30% 30%, rgba(251, 146, 60, 0.18), transparent 60%), radial-gradient(ellipse 600px 500px at 70% 80%, rgba(139, 92, 246, 0.15), transparent 60%)',
          }}
        />
        <div className="relative">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <Logo />
            <div className="flex flex-col leading-none">
              <span className="font-display font-extrabold text-lg tracking-tight">GANGU</span>
              <span className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-0.5">
                grocery · by voice
              </span>
            </div>
          </Link>
        </div>

        <div className="relative max-w-md">
          <span className="pill-amber mb-5 inline-flex">
            <Sparkles className="w-3 h-3" />
            Voice-first grocery
          </span>
          <h1 className="text-display text-4xl xl:text-5xl mb-5 leading-[1.05]">
            Welcome to <span className="gradient-text-warm">GANGU</span>
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed mb-10">
            Speak in Hindi, English, or Hinglish. Six AI agents handle the rest.
          </p>

          <div key={quoteIndex} className="surface-card p-6 animate-fade-in">
            <p className="text-slate-200 leading-relaxed text-[15px] mb-3">{quote.text}</p>
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-widest">{quote.author}</p>
          </div>
        </div>

        <div className="relative flex items-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          End-to-end encrypted · OTP only · Voice never stored
        </div>
      </aside>

      {/* RIGHT — form */}
      <section className="relative flex flex-col items-center justify-center px-6 py-12 md:py-16">
        {/* Mobile logo */}
        <Link href="/" className="lg:hidden inline-flex items-center gap-2.5 mb-10">
          <Logo />
          <span className="font-display font-extrabold text-lg tracking-tight">GANGU</span>
        </Link>

        <div className="w-full max-w-md">
          <div className="text-center mb-7">
            <h2 className="text-display text-3xl md:text-4xl mb-2">{title}</h2>
            <p className="text-slate-400">{subtitle}</p>
          </div>

          <div className="surface-card p-7 md:p-8 animate-rise">{children}</div>

          <p className="text-center text-xs text-slate-500 mt-5">
            <Link href="/" className="hover:text-slate-300">
              ← Back to home
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
