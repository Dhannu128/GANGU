'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Loader } from 'lucide-react'
import { signInWithPopup, signInWithPhoneNumber, ConfirmationResult, RecaptchaVerifier as FirebaseRecaptchaVerifier } from 'firebase/auth'
import { auth, googleProvider } from '@/lib/firebase'
import { useGANGUStore } from '@/lib/store'
import OTPModal from '@/components/auth/OTPModal'

export default function SignupPage() {
  const router = useRouter()
  const signIn = useGANGUStore(state => state.signIn)
  
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Phone Auth State
  const [showOTP, setShowOTP] = useState(false)
  const [confirmationResult, setConfirmationResult] = useState<ConfirmationResult | null>(null)

  // Initialize reCAPTCHA on mount
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.recaptchaVerifier) {
      window.recaptchaVerifier = new FirebaseRecaptchaVerifier(auth, 'recaptcha-container', {
        'size': 'invisible',
      })
    }
  }, [])

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    setError('')
    try {
      const result = await signInWithPopup(auth, googleProvider)
      const user = result.user
      
      // Update our global state
      signIn({
        id: user.uid,
        name: user.displayName || 'User',
        phone: user.phoneNumber || '',
        email: user.email || '',
        photoURL: user.photoURL || '',
        language: 'hinglish',
        address: 'Please set your delivery address in settings',
      }, await user.getIdToken())

      router.push('/app')
    } catch (err: unknown) {
      console.error(err)
      setError(err instanceof Error ? err.message : 'Failed to sign in with Google.')
    } finally {
      setIsLoading(false)
    }
  }

  const formatPhoneNumber = (number: string) => {
    // Default to +91 (India) if no country code provided, as per Swiggy demo standard
    let formatted = number.trim()
    if (!formatted.startsWith('+')) {
      formatted = '+91' + formatted
    }
    return formatted
  }

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!phoneNumber) return
    
    setIsLoading(true)
    setError('')
    try {
      const formattedNumber = formatPhoneNumber(phoneNumber)
      const appVerifier = window.recaptchaVerifier
      
      const confirmation = await signInWithPhoneNumber(auth, formattedNumber, appVerifier)
      setConfirmationResult(confirmation)
      setShowOTP(true)
    } catch (err: unknown) {
      console.error(err)
      setError('Failed to send SMS. Please ensure the phone number is correct.')
      // Reset recaptcha if failed
      if (window.recaptchaVerifier) {
        window.recaptchaVerifier.render().then((widgetId: number) => {
          window.grecaptcha?.reset(widgetId)
        });
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOTP = async (otp: string) => {
    if (!confirmationResult) return
    
    try {
      const result = await confirmationResult.confirm(otp)
      const user = result.user
      
      signIn({
        id: user.uid,
        name: 'User', // Prompt for name later or use default
        phone: user.phoneNumber || phoneNumber,
        language: 'hinglish',
        address: 'Please set your delivery address in settings',
      }, await user.getIdToken())

      router.push('/app')
    } catch {
      throw new Error('Invalid OTP. Please try again.')
    }
  }

  const handleResendOTP = async () => {
    setIsLoading(true)
    try {
      const formattedNumber = formatPhoneNumber(phoneNumber)
      const appVerifier = window.recaptchaVerifier
      const confirmation = await signInWithPhoneNumber(auth, formattedNumber, appVerifier)
      setConfirmationResult(confirmation)
    } catch (err: unknown) {
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-ink-950 flex flex-col relative overflow-hidden">
      {/* Background ambient light */}
      <div className="absolute top-0 inset-x-0 h-96 bg-gradient-to-b from-amber-500/10 to-transparent pointer-events-none" />

      {/* Header */}
      <header className="absolute top-0 inset-x-0 p-6 z-10">
        <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
      </header>

      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <div className="surface-card w-full max-w-md p-8 md:p-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-500/10 mb-6">
              <span className="text-2xl font-display font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">
                G
              </span>
            </div>
            <h1 className="text-3xl font-display font-bold text-white mb-2">Welcome to GANGU</h1>
            <p className="text-slate-400">Sign in to start ordering groceries with your voice.</p>
          </div>

          <button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 bg-white hover:bg-slate-50 text-slate-900 font-semibold py-3.5 px-4 rounded-xl transition-colors mb-6 disabled:opacity-50"
          >
            {isLoading ? <Loader className="w-5 h-5 animate-spin" /> : (
              <>
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
                Continue with Google
              </>
            )}
          </button>

          <div className="flex items-center gap-4 mb-6">
            <div className="h-px bg-white/10 flex-1" />
            <span className="text-xs text-slate-500 font-medium uppercase tracking-wider">or</span>
            <div className="h-px bg-white/10 flex-1" />
          </div>

          <form onSubmit={handlePhoneSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Phone Number</label>
              <div className="relative flex items-center">
                <div className="absolute left-3 flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-white/10 text-slate-400 font-medium text-sm">
                  +91
                </div>
                <input
                  type="tel"
                  placeholder="98765 43210"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-14 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all"
                  required
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-rose-400 animate-fade-in">{error}</p>
            )}

            <button
              type="submit"
              disabled={isLoading || phoneNumber.length < 10}
              className="w-full btn-primary py-3.5 disabled:opacity-50 flex justify-center"
            >
              {isLoading && !showOTP ? <Loader className="w-5 h-5 animate-spin" /> : 'Send OTP'}
            </button>
          </form>

          {/* Invisible recaptcha container for Phone Auth */}
          <div id="recaptcha-container"></div>
        </div>
      </div>

      <OTPModal
        isOpen={showOTP}
        onClose={() => setShowOTP(false)}
        phoneNumber={formatPhoneNumber(phoneNumber)}
        onVerify={handleVerifyOTP}
        resendOTP={handleResendOTP}
      />
    </main>
  )
}

// Add types for global window variables
declare global {
  interface Window {
    recaptchaVerifier: FirebaseRecaptchaVerifier
    grecaptcha?: { reset: (widgetId: number) => void }
  }
}
