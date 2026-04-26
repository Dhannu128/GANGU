'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useGANGUStore, type Language } from '@/lib/store'
import { requestOtp, verifyOtp } from '@/lib/api'
import { ArrowRight, Phone, Loader, ShieldCheck, ChevronLeft, AlertCircle, KeyRound } from 'lucide-react'

interface PhoneOtpFormProps {
  mode: 'signin' | 'signup'
}

export default function PhoneOtpForm({ mode }: PhoneOtpFormProps) {
  const router = useRouter()
  const { signIn } = useGANGUStore()

  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phone, setPhone] = useState('')
  const [name, setName] = useState('')
  const [language, setLanguage] = useState<Language>('hinglish')
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [devHint, setDevHint] = useState('')
  const [resendIn, setResendIn] = useState(0)

  const otpRefs = useRef<Array<HTMLInputElement | null>>([])

  useEffect(() => {
    if (resendIn <= 0) return
    const id = setTimeout(() => setResendIn((s) => s - 1), 1000)
    return () => clearTimeout(id)
  }, [resendIn])

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (phone.replace(/\D/g, '').length < 10) {
      setError('Please enter a valid 10-digit Indian phone number.')
      return
    }
    if (mode === 'signup' && name.trim().length < 2) {
      setError('Please enter your name.')
      return
    }

    setLoading(true)
    try {
      const res = await requestOtp(phone)
      if (res.success) {
        setStep('otp')
        setResendIn(res.retryInSeconds)
        setDevHint(res.devHint || '')
        setTimeout(() => otpRefs.current[0]?.focus(), 60)
      }
    } catch (err: any) {
      setError(err.message || 'Could not send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      // Pasted code
      const digits = value.replace(/\D/g, '').slice(0, 6).split('')
      const next = [...otp]
      digits.forEach((d, i) => {
        if (index + i < 6) next[index + i] = d
      })
      setOtp(next)
      const nextEmpty = next.findIndex((d) => !d)
      otpRefs.current[nextEmpty === -1 ? 5 : nextEmpty]?.focus()
      return
    }
    if (!/^\d?$/.test(value)) return
    const next = [...otp]
    next[index] = value
    setOtp(next)
    if (value && index < 5) otpRefs.current[index + 1]?.focus()
  }

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus()
    }
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    const code = otp.join('')
    if (code.length !== 6) {
      setError('Please enter the 6-digit code.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await verifyOtp(phone, code, mode === 'signup' ? name : undefined, language)
      if (res.success) {
        signIn(
          {
            id: res.user.id,
            name: res.user.name,
            phone: res.user.phone,
            language: res.user.language,
            address: res.user.address,
          },
          res.token
        )
        router.push('/app')
      }
    } catch (err: any) {
      setError(err.message || 'Invalid code. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resendOtp = async () => {
    if (resendIn > 0) return
    setOtp(['', '', '', '', '', ''])
    setError('')
    setLoading(true)
    try {
      const res = await requestOtp(phone)
      if (res.success) setResendIn(res.retryInSeconds)
    } finally {
      setLoading(false)
    }
  }

  if (step === 'phone') {
    return (
      <form onSubmit={handleRequest} className="space-y-5">
        {mode === 'signup' && (
          <div>
            <label className="block text-xs uppercase tracking-widest font-bold text-slate-500 mb-2">
              Your name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Lata Sharma"
              className="input-base"
              autoComplete="name"
            />
          </div>
        )}

        <div>
          <label className="block text-xs uppercase tracking-widest font-bold text-slate-500 mb-2">
            Phone number
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 inline-flex items-center gap-2 text-slate-400 font-medium pointer-events-none">
              <Phone className="w-4 h-4" />
              +91
            </span>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
              placeholder="98xxxxxxxx"
              className="input-base pl-20 tracking-wider font-medium"
              autoComplete="tel"
              inputMode="numeric"
            />
          </div>
        </div>

        {mode === 'signup' && (
          <div>
            <label className="block text-xs uppercase tracking-widest font-bold text-slate-500 mb-2">
              Preferred language
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  { v: 'hi', label: 'हिंदी' },
                  { v: 'en', label: 'English' },
                  { v: 'hinglish', label: 'Hinglish' },
                ] as { v: Language; label: string }[]
              ).map((opt) => (
                <button
                  key={opt.v}
                  type="button"
                  onClick={() => setLanguage(opt.v)}
                  className={`px-3 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                    language === opt.v
                      ? 'bg-amber-500/15 border-amber-500/50 text-amber-200 shadow-glow-sm'
                      : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-sm text-rose-300">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full text-base py-3.5">
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Sending OTP…
            </>
          ) : (
            <>
              Send OTP
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>

        <p className="text-center text-xs text-slate-500 leading-relaxed">
          By continuing, you agree to our{' '}
          <a href="#" className="text-slate-400 hover:text-amber-300 underline underline-offset-2">
            Terms
          </a>{' '}
          and{' '}
          <a href="#" className="text-slate-400 hover:text-amber-300 underline underline-offset-2">
            Privacy Policy
          </a>
          . You'll receive a one-time SMS — standard rates may apply.
        </p>

        <div className="flex items-center gap-3">
          <div className="divider-line flex-1" />
          <span className="text-[10px] text-slate-600 uppercase tracking-widest font-bold">or</span>
          <div className="divider-line flex-1" />
        </div>

        <button type="button" disabled className="btn-secondary w-full opacity-60 cursor-not-allowed" title="Coming soon">
          <GoogleIcon />
          Continue with Google
        </button>

        <p className="text-center text-sm text-slate-400">
          {mode === 'signin' ? "Don't have an account? " : 'Already have an account? '}
          <Link
            href={mode === 'signin' ? '/signup' : '/signin'}
            className="text-amber-300 font-semibold hover:text-amber-200"
          >
            {mode === 'signin' ? 'Create one' : 'Sign in'}
          </Link>
        </p>

        <p className="text-center">
          <Link href="/app" className="text-xs text-slate-500 hover:text-slate-300 inline-flex items-center gap-1">
            Continue as guest (read-only)
          </Link>
        </p>
      </form>
    )
  }

  return (
    <form onSubmit={handleVerify} className="space-y-5">
      <button
        type="button"
        onClick={() => {
          setStep('phone')
          setOtp(['', '', '', '', '', ''])
          setError('')
        }}
        className="inline-flex items-center gap-1 text-sm text-slate-400 hover:text-white"
      >
        <ChevronLeft className="w-4 h-4" />
        Back
      </button>

      <div>
        <p className="text-sm text-slate-400 mb-1">Code sent to</p>
        <p className="text-base font-semibold text-white inline-flex items-center gap-2">
          <Phone className="w-4 h-4 text-amber-300" />
          +91 {phone}
        </p>
      </div>

      <div>
        <label className="block text-xs uppercase tracking-widest font-bold text-slate-500 mb-3 inline-flex items-center gap-1.5">
          <KeyRound className="w-3 h-3" />
          Enter the 6-digit code
        </label>
        <div className="flex gap-2 justify-between">
          {otp.map((digit, i) => (
            <input
              key={i}
              ref={(el) => { otpRefs.current[i] = el }}
              type="text"
              inputMode="numeric"
              maxLength={i === 0 ? 6 : 1}
              value={digit}
              onChange={(e) => handleOtpChange(i, e.target.value)}
              onKeyDown={(e) => handleOtpKeyDown(i, e)}
              className="w-12 h-14 md:w-13 md:h-15 text-center text-2xl font-display font-extrabold rounded-xl bg-white/[0.04] border-2 border-white/10 text-white focus:outline-none focus:border-amber-500/60 focus:bg-white/[0.08] transition-all"
            />
          ))}
        </div>
        {devHint && (
          <p className="text-xs text-slate-500 mt-3 text-center">
            <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 font-semibold">
              Dev
            </span>{' '}
            {devHint}
          </p>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-sm text-rose-300">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <button type="submit" disabled={loading} className="btn-primary w-full text-base py-3.5">
        {loading ? (
          <>
            <Loader className="w-4 h-4 animate-spin" />
            Verifying…
          </>
        ) : (
          <>
            <ShieldCheck className="w-5 h-5" />
            Verify & continue
          </>
        )}
      </button>

      <div className="text-center text-sm">
        {resendIn > 0 ? (
          <p className="text-slate-500">
            Didn't get the code? Resend in <span className="text-slate-300 font-semibold">{resendIn}s</span>
          </p>
        ) : (
          <button
            type="button"
            onClick={resendOtp}
            className="text-amber-300 font-semibold hover:text-amber-200"
          >
            Resend code
          </button>
        )}
      </div>
    </form>
  )
}

function GoogleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden>
      <path
        fill="#EA4335"
        d="M12 5.5c1.7 0 3.2.6 4.4 1.7L20 3.6C17.9 1.7 15.2.5 12 .5 7.3.5 3.3 3.2 1.4 7.2l4.2 3.3C6.6 7.5 9 5.5 12 5.5z"
      />
      <path
        fill="#34A853"
        d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.7-2.4 3.6l3.9 3c2.3-2.1 3.5-5.2 3.5-8.8z"
      />
      <path
        fill="#FBBC05"
        d="M5.6 14.6c-.3-.8-.5-1.7-.5-2.6s.2-1.8.5-2.6L1.4 6.1C.5 7.9 0 9.9 0 12s.5 4.1 1.4 5.9l4.2-3.3z"
      />
      <path
        fill="#4285F4"
        d="M12 23.5c3.2 0 5.9-1.1 7.9-2.9l-3.9-3c-1.1.7-2.4 1.2-4 1.2-3 0-5.6-2-6.5-4.7L1.4 17.4C3.3 21.4 7.3 23.5 12 23.5z"
      />
    </svg>
  )
}

