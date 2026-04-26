'use client'

import { useGANGUStore, type Language } from '@/lib/store'
import { Settings as SettingsIcon, Globe2, MapPin, Wallet, Volume2, Eye, ShieldCheck } from 'lucide-react'

export default function SettingsPage() {
  const { settings, updateSettings, user, updateUser } = useGANGUStore()

  return (
    <main className="min-h-screen pb-12">
      <div className="max-w-3xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <header className="mb-8">
          <span className="pill-slate mb-3 inline-flex">
            <SettingsIcon className="w-3 h-3" />
            Preferences
          </span>
          <h1 className="text-display text-3xl md:text-4xl mb-2">Settings</h1>
          <p className="text-slate-400">Make GANGU feel like yours.</p>
        </header>

        <div className="space-y-5">
          {/* Language */}
          <Section icon={Globe2} title="Preferred language" subtitle="The greeting and confirmations adapt.">
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
                  onClick={() => {
                    updateSettings({ language: opt.v })
                    updateUser({ language: opt.v })
                  }}
                  className={`px-3 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                    settings.language === opt.v
                      ? 'bg-amber-500/15 border-amber-500/50 text-amber-200'
                      : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </Section>

          {/* Address */}
          <Section icon={MapPin} title="Default delivery address" subtitle="Where your orders should arrive.">
            <input
              type="text"
              value={settings.address}
              onChange={(e) => {
                updateSettings({ address: e.target.value })
                updateUser({ address: e.target.value })
              }}
              className="input-base"
            />
          </Section>

          {/* Payment */}
          <Section icon={Wallet} title="Payment method" subtitle="Default for confirmed orders.">
            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  { v: 'upi', label: 'UPI' },
                  { v: 'cod', label: 'Cash on delivery' },
                  { v: 'card', label: 'Card' },
                ] as const
              ).map((opt) => (
                <button
                  key={opt.v}
                  onClick={() => updateSettings({ paymentMethod: opt.v })}
                  className={`px-3 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
                    settings.paymentMethod === opt.v
                      ? 'bg-amber-500/15 border-amber-500/50 text-amber-200'
                      : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </Section>

          {/* Voice speed */}
          <Section icon={Volume2} title="Voice speed" subtitle="How fast GANGU should reply when speaking.">
            <div className="grid grid-cols-3 gap-2">
              {(['slow', 'normal', 'fast'] as const).map((v) => (
                <button
                  key={v}
                  onClick={() => updateSettings({ voiceSpeed: v })}
                  className={`px-3 py-2.5 rounded-xl text-sm font-semibold border transition-all capitalize ${
                    settings.voiceSpeed === v
                      ? 'bg-amber-500/15 border-amber-500/50 text-amber-200'
                      : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </Section>

          {/* Accessibility */}
          <Section icon={Eye} title="Accessibility" subtitle="Make text and contrast easier on the eyes.">
            <div className="space-y-3">
              <Toggle
                label="Larger text"
                value={settings.largerText}
                onChange={(v) => updateSettings({ largerText: v })}
              />
              <Toggle
                label="Higher contrast"
                value={settings.higherContrast}
                onChange={(v) => updateSettings({ higherContrast: v })}
              />
            </div>
          </Section>

          {/* Privacy */}
          <Section icon={ShieldCheck} title="Data & privacy" subtitle="Your voice is transcribed once and discarded — never stored.">
            <div className="flex flex-wrap gap-2">
              <button className="btn-secondary text-sm">Download my data</button>
              <button className="btn-secondary text-sm">Delete order history</button>
              <button className="btn-danger text-sm">Delete my account</button>
            </div>
          </Section>

          {/* Account */}
          {user && (
            <Section icon={SettingsIcon} title="Account" subtitle="Your basic details.">
              <div className="space-y-3">
                <Field label="Name" value={user.name} />
                <Field label="Phone" value={user.phone} />
              </div>
            </Section>
          )}
        </div>
      </div>
    </main>
  )
}

function Section({
  icon: Icon,
  title,
  subtitle,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  subtitle?: string
  children: React.ReactNode
}) {
  return (
    <article className="surface-card p-6">
      <div className="flex items-start gap-3 mb-5">
        <div className="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4 text-amber-300" />
        </div>
        <div>
          <h3 className="font-semibold text-white text-base">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{subtitle}</p>}
        </div>
      </div>
      {children}
    </article>
  )
}

function Toggle({
  label,
  value,
  onChange,
}: {
  label: string
  value: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <label className="flex items-center justify-between gap-4 cursor-pointer">
      <span className="text-sm text-slate-200 font-medium">{label}</span>
      <button
        onClick={() => onChange(!value)}
        className={`relative w-11 h-6 rounded-full transition-all ${
          value ? 'bg-amber-500' : 'bg-white/10 border border-white/10'
        }`}
        aria-pressed={value}
      >
        <span
          className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-all ${
            value ? 'left-[22px]' : 'left-0.5'
          }`}
        />
      </button>
    </label>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/10">
      <span className="text-xs uppercase tracking-widest font-bold text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-200">{value}</span>
    </div>
  )
}
