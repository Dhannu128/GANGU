'use client'

import { useState } from 'react'
import { KeyRound, Loader, ShieldCheck, X } from 'lucide-react'

interface ZeptoOtpDialogProps {
  otpType: 'login' | 'payment'
  onSubmit: (otp: string) => Promise<void>
  onCancel: () => void
}

export default function ZeptoOtpDialog({ otpType, onSubmit, onCancel }: ZeptoOtpDialogProps) {
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (!/^\d{4,8}$/.test(otp)) return
    setLoading(true)
    try {
      await onSubmit(otp)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#21342b]/70" role="dialog" aria-modal="true" aria-labelledby="zepto-otp-title">
      <div className="relative w-full max-w-md surface-card p-7 md:p-8 animate-rise">
        <button onClick={onCancel} aria-label="Cancel Zepto order" className="absolute top-4 right-4 w-9 h-9 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-900 flex items-center justify-center">
          <X className="w-4 h-4" />
        </button>
        <KeyRound className="w-10 h-10 text-teal-700 mb-4" aria-hidden />
        <p className="eyebrow">Zepto secure verification</p>
        <h3 id="zepto-otp-title" className="text-2xl text-display mt-2">Enter the {otpType} OTP</h3>
        <p className="text-sm text-slate-600 mt-2 mb-5">Use the code Zepto sent to your registered mobile number. GANGU does not save this code.</p>
        <input
          className="otp-field"
          value={otp}
          onChange={(event) => setOtp(event.target.value.replace(/\D/g, '').slice(0, 8))}
          inputMode="numeric"
          autoComplete="one-time-code"
          aria-label="Zepto OTP"
          autoFocus
        />
        <button onClick={submit} disabled={loading || !/^\d{4,8}$/.test(otp)} className="btn-primary w-full mt-5 py-3.5">
          {loading ? <><Loader className="w-4 h-4 animate-spin" /> Verifying...</> : 'Verify and continue COD order'}
        </button>
        <p className="text-xs text-slate-500 mt-4 flex gap-2"><ShieldCheck className="w-4 h-4 shrink-0 text-teal-700" />This continues only the product and address you already confirmed.</p>
      </div>
    </div>
  )
}
