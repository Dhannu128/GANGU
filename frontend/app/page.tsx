'use client'

import Link from 'next/link'
import { useGANGUStore } from '@/lib/store'
import Logo from '@/components/Logo'
import DemoStrip from '@/components/landing/DemoStrip'
import Testimonials from '@/components/landing/Testimonials'
import Pricing from '@/components/landing/Pricing'
import FAQ from '@/components/landing/FAQ'
import {
  Mic,
  Sparkles,
  Zap,
  ShieldCheck,
  Globe2,
  ArrowRight,
  Bot,
  HeartHandshake,
} from 'lucide-react'

const PLATFORMS = ['Zepto', 'Amazon', 'Blinkit', 'BigBasket', 'JioMart', 'Swiggy Instamart', 'Dunzo']

const HOW_IT_WORKS = [
  {
    icon: Mic,
    title: 'Speak naturally',
    desc: 'Tap the mic and say what you need — in Hindi, English, or Hinglish. No menus, no forms.',
  },
  {
    icon: Bot,
    title: 'AI does the work',
    desc: 'Six specialized agents understand your request, search every platform, and pick the best deal in seconds.',
  },
  {
    icon: Zap,
    title: 'Order in one tap',
    desc: 'Review the recommended option, confirm with a tap. GANGU places the order. Delivered in minutes.',
  },
]

const FEATURES = [
  {
    icon: HeartHandshake,
    title: 'Designed for elders',
    desc: 'Calm interface. Big tap targets. Voice-first. Built for the people tech often forgets.',
    tint: 'amber',
  },
  {
    icon: Globe2,
    title: 'हिंदी · English · Hinglish',
    desc: 'Talk the way you talk at home. Our intent agent understands all three, mixed naturally.',
    tint: 'violet',
  },
  {
    icon: ShieldCheck,
    title: 'Safe by default',
    desc: 'Six decision policies protect every order — confidence checks, stock verification, elderly safeguards.',
    tint: 'emerald',
  },
]

export default function Home() {
  const { connected, auth } = useGANGUStore()

  return (
    <main className="min-h-screen relative">
      {/* TOP NAV */}
      <nav className="sticky top-0 z-40 backdrop-blur-xl bg-ink-950/70 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <Logo />
            <div className="flex flex-col leading-none">
              <span className="font-display font-extrabold text-lg tracking-tight">GANGU</span>
              <span className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-0.5">
                grocery · by voice
              </span>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#demo" className="hover:text-white transition-colors">Try it</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How it works</a>
            <a href="#why-gangu" className="hover:text-white transition-colors">Why GANGU</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
          </div>

          <div className="flex items-center gap-2">
            <span className={connected ? 'pill-emerald hidden sm:inline-flex' : 'pill-slate hidden sm:inline-flex'}>
              <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
              {connected ? 'Live' : 'Offline'}
            </span>
            {auth.isAuthenticated ? (
              <Link href="/app" className="btn-primary text-sm">
                Open app
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link href="/signin" className="btn-ghost text-sm">Sign in</Link>
                <Link href="/signup" className="btn-primary text-sm">Get started</Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative max-w-7xl mx-auto px-6 pt-20 md:pt-24 pb-12">
        <div className="text-center max-w-4xl mx-auto animate-fade-in">
          <span className="pill-amber mb-7 mx-auto inline-flex">
            <Sparkles className="w-3.5 h-3.5" />
            India's first voice-first grocery assistant
          </span>

          <h1 className="text-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl mb-7 leading-[0.95]">
            Your voice.
            <br />
            <span className="gradient-text-warm">Your groceries.</span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Speak naturally. Six AI agents search every Indian grocery platform, pick the best deal, and order it for you in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href={auth.isAuthenticated ? '/app' : '/signup'} className="btn-primary text-base px-7 py-3.5">
              <Mic className="w-4 h-4" />
              {auth.isAuthenticated ? 'Open app' : 'Get started free'}
            </Link>
            <a href="#how-it-works" className="btn-secondary text-base px-7 py-3.5">
              See how it works
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>

          <div className="mt-12 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-xs text-slate-500 uppercase tracking-widest font-semibold">
            <span className="inline-flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Safe purchases
            </span>
            <span className="hidden sm:inline text-slate-700">·</span>
            <span className="inline-flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5 text-amber-400" /> 6 AI agents
            </span>
            <span className="hidden sm:inline text-slate-700">·</span>
            <span className="inline-flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-violet-400" /> 10-min delivery
            </span>
          </div>
        </div>
      </section>

      {/* LIVE DEMO STRIP */}
      <div id="demo">
        <DemoStrip />
      </div>

      {/* PLATFORMS MARQUEE */}
      <section className="relative border-y border-white/5 bg-white/[0.012] py-7 overflow-hidden">
        <p className="text-center text-[11px] text-slate-500 uppercase tracking-[0.25em] font-bold mb-5">
          Searches across India's top grocery platforms
        </p>
        <div className="relative">
          <div className="flex marquee-track gap-14 whitespace-nowrap font-display text-2xl md:text-3xl font-bold text-slate-700">
            {[...PLATFORMS, ...PLATFORMS, ...PLATFORMS].map((p, i) => (
              <span key={i} className="flex items-center gap-3">
                {p}
                <span className="text-amber-500/30">●</span>
              </span>
            ))}
          </div>
          <div className="pointer-events-none absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-ink-950 to-transparent" />
          <div className="pointer-events-none absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-ink-950 to-transparent" />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="relative max-w-7xl mx-auto px-6 py-24 scroll-mt-20">
        <div className="text-center mb-14 max-w-2xl mx-auto">
          <span className="pill-cyan mb-3 mx-auto inline-flex">How it works</span>
          <h2 className="text-display text-4xl md:text-5xl mt-2 mb-3">
            From voice to delivered, <br className="hidden md:block" />
            <span className="gradient-text-cool">in three steps</span>
          </h2>
          <p className="text-slate-400 text-lg">No app to learn. No forms to fill. Just talk.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {HOW_IT_WORKS.map((step, i) => (
            <div key={i} className="surface-card p-7 group transition-transform hover:-translate-y-1.5">
              <div className="flex items-start justify-between mb-7">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/30 flex items-center justify-center">
                  <step.icon className="w-6 h-6 text-amber-300" strokeWidth={2} />
                </div>
                <span className="text-5xl font-display font-extrabold text-slate-800 group-hover:text-amber-500/40 transition-colors">
                  0{i + 1}
                </span>
              </div>
              <h3 className="text-xl font-display font-bold mb-2.5 tracking-tight">{step.title}</h3>
              <p className="text-slate-400 leading-relaxed text-sm">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* WHY GANGU */}
      <section id="why-gangu" className="relative max-w-7xl mx-auto px-6 py-24 scroll-mt-20">
        <div className="text-center mb-14 max-w-2xl mx-auto">
          <span className="pill-violet mb-3 mx-auto inline-flex">Why GANGU</span>
          <h2 className="text-display text-4xl md:text-5xl mt-2 mb-3">
            Designed for the people <br className="hidden md:block" />
            <span className="gradient-text">tech often forgets</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {FEATURES.map((feature, i) => {
            const Icon = feature.icon
            const tintMap: Record<string, string> = {
              amber: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-300',
              violet: 'from-violet-500/20 to-fuchsia-500/10 border-violet-500/30 text-violet-300',
              emerald: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-300',
            }
            return (
              <div key={i} className="surface-card p-7">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br border flex items-center justify-center mb-6 ${tintMap[feature.tint]}`}>
                  <Icon className="w-7 h-7" strokeWidth={2} />
                </div>
                <h3 className="text-xl font-display font-bold mb-2.5 tracking-tight">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm">{feature.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* TESTIMONIALS */}
      <Testimonials />

      {/* PRICING */}
      <Pricing />

      {/* FAQ */}
      <FAQ />

      {/* CTA STRIP */}
      <section className="relative max-w-7xl mx-auto px-6 py-12 md:py-16">
        <div className="surface-card relative overflow-hidden p-10 md:p-14 text-center">
          <div
            className="absolute inset-0 pointer-events-none opacity-60"
            style={{
              background:
                'radial-gradient(ellipse 600px 300px at 30% 20%, rgba(251, 146, 60, 0.18), transparent 60%), radial-gradient(ellipse 600px 300px at 70% 80%, rgba(139, 92, 246, 0.15), transparent 60%)',
            }}
          />
          <div className="relative">
            <h2 className="text-display text-3xl md:text-5xl mb-4">
              Start ordering with your <span className="gradient-text-warm">voice today</span>
            </h2>
            <p className="text-slate-400 text-lg mb-8 max-w-xl mx-auto">
              No signup forms. No credit card. Just your phone number and OTP.
            </p>
            <Link href={auth.isAuthenticated ? '/app' : '/signup'} className="btn-primary text-base px-8 py-3.5 inline-flex">
              {auth.isAuthenticated ? 'Open app' : 'Get started free'}
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
            <div className="col-span-2">
              <div className="flex items-center gap-2.5 mb-3">
                <Logo size={30} />
                <span className="font-display font-bold text-lg">GANGU</span>
              </div>
              <p className="text-sm text-slate-400 max-w-xs leading-relaxed">
                Voice-first grocery shopping for everyone. Built in India, for India.
              </p>
            </div>
            {[
              { title: 'Product', links: ['Try it', 'How it works', 'Pricing', 'What\'s new'] },
              { title: 'Company', links: ['About', 'Careers', 'Press', 'Contact'] },
              { title: 'Trust', links: ['Privacy', 'Terms', 'Refund policy', 'Security'] },
              { title: 'Reach us', links: ['help@gangu.in', 'WhatsApp support', 'Twitter', 'Instagram'] },
            ].map((col, i) => (
              <div key={i}>
                <p className="text-xs uppercase tracking-widest font-bold text-slate-500 mb-4">
                  {col.title}
                </p>
                <ul className="space-y-2.5">
                  {col.links.map((l, j) => (
                    <li key={j}>
                      <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors">
                        {l}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="pt-7 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-500">
              © 2026 GANGU Labs <span className="text-slate-700 mx-2">·</span> Built with{' '}
              <span className="text-amber-400">♥</span> in India
            </p>
            <p className="text-xs text-slate-500">
              हिंदी <span className="text-slate-700 mx-1.5">·</span> English{' '}
              <span className="text-slate-700 mx-1.5">·</span> Hinglish
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}
