'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Loader, ShieldCheck } from 'lucide-react'

interface OTPModalProps {
  isOpen: boolean
  onClose: () => void
  onVerify: (otp: string) => Promise<void>
  phoneNumber: string
  resendOTP: () => Promise<void>
}

export default function OTPModal({ isOpen, onClose, onVerify, phoneNumber, resendOTP }: OTPModalProps) {
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState('')
  const [countdown, setCountdown] = useState(30)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  // Reset state when opened
  useEffect(() => {
    if (isOpen) {
      setOtp(['', '', '', '', '', ''])
      setError('')
      setCountdown(30)
      setIsVerifying(false)
      // Focus first input
      setTimeout(() => {
        if (inputRefs.current[0]) inputRefs.current[0].focus()
      }, 100)
    }
  }, [isOpen])

  // Countdown timer
  useEffect(() => {
    if (!isOpen || countdown <= 0) return
    const timer = setInterval(() => setCountdown(c => c - 1), 1000)
    return () => clearInterval(timer)
  }, [isOpen, countdown])

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return // Only numbers

    const newOtp = [...otp]
    newOtp[index] = value
    setOtp(newOtp)
    setError('')

    // Auto focus next input
    if (value && index < 5 && inputRefs.current[index + 1]) {
      inputRefs.current[index + 1]?.focus()
    }

    // Auto submit if all filled
    if (index === 5 && value && newOtp.every(v => v !== '')) {
      handleVerify(newOtp.join(''))
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      // Focus previous input on backspace if current is empty
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handleVerify = async (fullOtp?: string) => {
    const code = fullOtp || otp.join('')
    if (code.length !== 6) {
      setError('Please enter all 6 digits')
      return
    }

    setIsVerifying(true)
    setError('')
    try {
      await onVerify(code)
    } catch (err: any) {
      setError(err.message || 'Invalid code. Please try again.')
    } finally {
      setIsVerifying(false)
    }
  }

  const handleResend = async () => {
    if (countdown > 0) return
    
    setError('')
    setCountdown(30)
    setOtp(['', '', '', '', '', ''])
    
    try {
      await resendOTP()
    } catch (err: any) {
      setError('Failed to resend. Please try again.')
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-ink-950/80 backdrop-blur-sm"
            onClick={onClose}
          />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              className="surface-card w-full max-w-md p-8 relative pointer-events-auto"
            >
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white bg-white/5 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              <div className="text-center mb-8">
                <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
                  <ShieldCheck className="w-8 h-8 text-amber-500" />
                </div>
                <h2 className="text-2xl font-display font-bold text-white mb-2">Check your phone</h2>
                <p className="text-slate-400 text-sm">
                  We sent a 6-digit verification code to<br />
                  <span className="font-semibold text-white tracking-wider">{phoneNumber}</span>
                </p>
              </div>

              <div className="flex justify-center gap-2 mb-6" dir="ltr">
                {otp.map((digit, i) => (
                  <input
                    key={i}
                    ref={el => { inputRefs.current[i] = el }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(i, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(i, e)}
                    className="w-12 h-14 text-center text-2xl font-bold bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all"
                  />
                ))}
              </div>

              {error && (
                <p className="text-rose-400 text-sm text-center mb-4 animate-shake">
                  {error}
                </p>
              )}

              <button
                onClick={() => handleVerify()}
                disabled={isVerifying || otp.join('').length !== 6}
                className="w-full btn-primary py-3.5 mb-6 disabled:opacity-50"
              >
                {isVerifying ? (
                  <Loader className="w-5 h-5 animate-spin mx-auto" />
                ) : (
                  'Verify Code'
                )}
              </button>

              <div className="text-center text-sm text-slate-400">
                Didn't receive the code?{' '}
                <button
                  onClick={handleResend}
                  disabled={countdown > 0}
                  className={`font-medium transition-colors ${
                    countdown > 0 ? 'text-slate-500 cursor-not-allowed' : 'text-amber-400 hover:text-amber-300'
                  }`}
                >
                  {countdown > 0 ? `Resend in ${countdown}s` : 'Resend now'}
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
