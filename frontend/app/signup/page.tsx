'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  type ConfirmationResult,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  signInWithPopup,
} from 'firebase/auth'
import { ArrowLeft, Check, LoaderCircle, Mic, Phone, ShieldCheck } from 'lucide-react'
import Logo from '@/components/Logo'
import { auth, googleProvider } from '@/lib/firebase'
import { authErrorMessage } from '@/lib/auth-errors'
import { useGANGUStore } from '@/lib/store'

const PHONE_RETRY_SECONDS = 30

export default function SignupPage() {
  const router = useRouter()
  const { auth: authState, signIn } = useGANGUStore()
  const verifierRef = useRef<RecaptchaVerifier | null>(null)
  const confirmationRef = useRef<ConfirmationResult | null>(null)
  const [step, setStep] = useState<'phone' | 'code'>('phone')
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState<'google' | 'phone' | 'verify' | null>(null)
  const [error, setError] = useState('')
  const [resendIn, setResendIn] = useState(0)

  useEffect(() => {
    if (authState.initialized && authState.isAuthenticated) router.replace('/app')
  }, [authState.initialized, authState.isAuthenticated, router])

  useEffect(() => {
    if (resendIn <= 0) return
    const timer = window.setTimeout(() => setResendIn((seconds) => seconds - 1), 1000)
    return () => window.clearTimeout(timer)
  }, [resendIn])

  useEffect(() => () => verifierRef.current?.clear(), [])

  const getVerifier = () => {
    if (!verifierRef.current) {
      verifierRef.current = new RecaptchaVerifier(auth, 'recaptcha-container', {
        size: 'invisible',
      })
    }
    return verifierRef.current
  }

  const clearVerifier = () => {
    verifierRef.current?.clear()
    verifierRef.current = null
  }

  const completeSignIn = async () => {
    const firebaseUser = auth.currentUser
    if (!firebaseUser) throw new Error('Firebase did not return a signed-in user.')
    signIn({
      id: firebaseUser.uid,
      name: firebaseUser.displayName || 'GANGU user',
      phone: firebaseUser.phoneNumber || '',
      email: firebaseUser.email || undefined,
      photoURL: firebaseUser.photoURL || undefined,
      language: 'hinglish',
      address: '',
    }, await firebaseUser.getIdToken())
    router.replace('/app')
  }

  const handleGoogle = async () => {
    setBusy('google')
    setError('')
    try {
      await signInWithPopup(auth, googleProvider)
      await completeSignIn()
    } catch (authError) {
      setError(authErrorMessage(authError, 'Google sign-in could not be completed.'))
    } finally {
      setBusy(null)
    }
  }

  const sendCode = async (event?: React.FormEvent) => {
    event?.preventDefault()
    if (phone.length !== 10) {
      setError('Enter a valid 10-digit Indian mobile number.')
      return
    }
    setBusy('phone')
    setError('')
    try {
      confirmationRef.current = await signInWithPhoneNumber(auth, `+91${phone}`, getVerifier())
      setStep('code')
      setCode('')
      setResendIn(PHONE_RETRY_SECONDS)
    } catch (authError) {
      clearVerifier()
      setError(authErrorMessage(authError, 'We could not send the SMS code.'))
    } finally {
      setBusy(null)
    }
  }

  const verifyCode = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!confirmationRef.current || code.length !== 6) {
      setError('Enter the complete 6-digit code from the SMS.')
      return
    }
    setBusy('verify')
    setError('')
    try {
      await confirmationRef.current.confirm(code)
      await completeSignIn()
    } catch (authError) {
      setError(authErrorMessage(authError, 'The verification code could not be confirmed.'))
    } finally {
      setBusy(null)
    }
  }

  return (
    <main className="auth-page">
      <header className="auth-header">
        <Link href="/" className="brand-lockup" aria-label="GANGU home">
          <Logo size={38} />
          <span>GANGU</span>
        </Link>
        <Link href="/" className="quiet-link"><ArrowLeft aria-hidden /> Back to home</Link>
      </header>

      <div className="auth-layout">
        <section className="auth-intro" aria-labelledby="auth-heading">
          <p className="eyebrow">Grocery help that listens</p>
          <h1 id="auth-heading">Welcome. Let&apos;s get your groceries sorted.</h1>
          <p className="auth-lede">
            Sign in securely, then speak or type what you need. You always review the result before anything happens.
          </p>
          <ul className="trust-list">
            <li><Mic aria-hidden /><span><strong>Voice first</strong>Hindi, English, or Hinglish</span></li>
            <li><ShieldCheck aria-hidden /><span><strong>You stay in control</strong>Every order needs confirmation</span></li>
            <li><Check aria-hidden /><span><strong>Honest results</strong>Estimates and live data are clearly labelled</span></li>
          </ul>
        </section>

        <section className="auth-card" aria-label="Sign in to GANGU">
          <div className="auth-card-heading">
            <p className="eyebrow">Secure sign in</p>
            <h2>{step === 'phone' ? 'Continue to GANGU' : 'Check your messages'}</h2>
            <p>{step === 'phone' ? 'Use Google or your Indian mobile number.' : `We sent a code to +91 ${phone}.`}</p>
          </div>

          {step === 'phone' ? (
            <>
              <button className="google-button" onClick={handleGoogle} disabled={busy !== null}>
                {busy === 'google' ? <LoaderCircle className="spin" aria-hidden /> : <GoogleMark />}
                Continue with Google
              </button>
              <div className="or-divider"><span>or use your mobile</span></div>
              <form onSubmit={sendCode} className="auth-form">
                <label htmlFor="phone">Mobile number</label>
                <div className="phone-field">
                  <span><Phone aria-hidden /> +91</span>
                  <input
                    id="phone"
                    value={phone}
                    onChange={(event) => setPhone(event.target.value.replace(/\D/g, '').slice(0, 10))}
                    inputMode="numeric"
                    autoComplete="tel-national"
                    placeholder="98765 43210"
                    aria-describedby="phone-help"
                  />
                </div>
                <p id="phone-help" className="field-help">We will send a one-time code by SMS.</p>
                <button className="primary-action" disabled={busy !== null || phone.length !== 10}>
                  {busy === 'phone' ? <><LoaderCircle className="spin" aria-hidden /> Sending code</> : 'Send secure code'}
                </button>
              </form>
            </>
          ) : (
            <form onSubmit={verifyCode} className="auth-form">
              <label htmlFor="otp">6-digit verification code</label>
              <input
                id="otp"
                className="otp-field"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="• • • • • •"
                autoFocus
              />
              <button className="primary-action" disabled={busy !== null || code.length !== 6}>
                {busy === 'verify' ? <><LoaderCircle className="spin" aria-hidden /> Checking code</> : 'Verify and continue'}
              </button>
              <div className="code-actions">
                <button type="button" className="quiet-link" onClick={() => { setStep('phone'); setError('') }}>Change number</button>
                <button type="button" className="quiet-link" disabled={resendIn > 0 || busy !== null} onClick={() => void sendCode()}>
                  {resendIn > 0 ? `Resend in ${resendIn}s` : 'Resend code'}
                </button>
              </div>
            </form>
          )}

          {error && <div className="auth-error" role="alert">{error}</div>}
          <div id="recaptcha-container" />
          <p className="auth-footnote">Protected by Firebase Authentication. GANGU never asks for your OTP by phone or chat.</p>
        </section>
      </div>
    </main>
  )
}

function GoogleMark() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden>
      <path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.4-.2-2H12v3.9h5.4a4.6 4.6 0 0 1-2 3v2.5h3.2c1.9-1.8 3-4.4 3-7.4Z" />
      <path fill="#34A853" d="M12 22c2.7 0 5-.9 6.7-2.4l-3.2-2.5c-.9.6-2 1-3.5 1a5.9 5.9 0 0 1-5.5-4.1H3.2v2.6A10 10 0 0 0 12 22Z" />
      <path fill="#FBBC05" d="M6.5 14a6 6 0 0 1 0-3.9V7.5H3.2a10 10 0 0 0 0 9.1L6.5 14Z" />
      <path fill="#EA4335" d="M12 5.9c1.6 0 3 .5 4.1 1.6L19 4.6A9.7 9.7 0 0 0 3.2 7.5l3.3 2.6A5.9 5.9 0 0 1 12 5.9Z" />
    </svg>
  )
}
