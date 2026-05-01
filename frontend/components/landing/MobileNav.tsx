'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Menu, X, ArrowRight } from 'lucide-react'

const LINKS = [
  { href: '#demo',         label: 'Try it' },
  { href: '#how-it-works', label: 'How it works' },
  { href: '#why-gangu',    label: 'Why GANGU' },
  { href: '#pricing',      label: 'Pricing' },
]

interface Props {
  isAuthenticated: boolean
}

export default function MobileNav({ isAuthenticated }: Props) {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [open])

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        aria-label="Open menu"
        className="md:hidden btn-ghost px-3 py-2"
      >
        <Menu className="w-5 h-5" />
      </button>

      {open && (
        <div
          className="md:hidden fixed inset-0 z-50 bg-ink-950/80 backdrop-blur-md animate-fade-in"
          onClick={() => setOpen(false)}
        >
          <div
            className="absolute right-0 top-0 h-full w-[82%] max-w-sm glass-strong border-l border-white/10 p-6 animate-rise"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-10">
              <span className="font-display font-extrabold text-lg">Menu</span>
              <button
                onClick={() => setOpen(false)}
                aria-label="Close menu"
                className="btn-ghost px-3 py-2"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="flex flex-col gap-1 mb-8">
              {LINKS.map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="text-lg font-display font-semibold text-slate-200 hover:text-amber-300 px-3 py-3 rounded-xl hover:bg-white/5 transition-colors"
                >
                  {l.label}
                </a>
              ))}
            </nav>

            <div className="flex flex-col gap-2">
              {isAuthenticated ? (
                <Link href="/app" onClick={() => setOpen(false)} className="btn-primary justify-center">
                  Open app
                  <ArrowRight className="w-4 h-4" />
                </Link>
              ) : (
                <>
                  <Link href="/signup" onClick={() => setOpen(false)} className="btn-primary justify-center">
                    Get started free
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link href="/signin" onClick={() => setOpen(false)} className="btn-secondary justify-center">
                    Sign in
                  </Link>
                </>
              )}
            </div>

            <p className="mt-10 text-xs text-slate-500 uppercase tracking-[0.2em] font-bold">
              हिंदी · English · Hinglish
            </p>
          </div>
        </div>
      )}
    </>
  )
}
