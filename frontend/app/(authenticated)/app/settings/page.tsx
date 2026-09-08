'use client'

import { useMemo, useState } from 'react'
import { useGANGUStore, type Language, type Settings } from '@/lib/store'
import {
  Settings as SettingsIcon,
  Globe2,
  MapPin,
  Wallet,
  Volume2,
  Eye,
  ShieldCheck,
  Save,
  RotateCcw,
  Check,
} from 'lucide-react'

export default function SettingsPage() {
  const { settings, updateSettings, user, updateUser, pushToast } = useGANGUStore()

  const [draft, setDraft] = useState<Settings>(settings)
  const [draftName, setDraftName] = useState(user?.name ?? '')

  const isDirty = useMemo(() => {
    return (
      JSON.stringify(draft) !== JSON.stringify(settings) ||
      draftName !== (user?.name ?? '')
    )
  }, [draft, settings, draftName, user?.name])

  const patch = (p: Partial<Settings>) => setDraft((d) => ({ ...d, ...p }))

  const handleSave = () => {
    updateSettings(draft)
    updateUser({ language: draft.language, address: draft.address, name: draftName })
    pushToast({
      variant: 'success',
      title: 'Settings saved',
      description: 'Your preferences were saved in this browser.',
    })
  }

  const handleDiscard = () => {
    setDraft(settings)
    setDraftName(user?.name ?? '')
    pushToast({ variant: 'info', title: 'Changes discarded' })
  }

  return (
    <main className="min-h-screen pb-32">
      <div className="max-w-3xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <header className="mb-8">
          <span className="pill-slate mb-3 inline-flex">
            <SettingsIcon className="w-3 h-3" />
            Preferences
          </span>
          <h1 className="text-display text-3xl md:text-4xl mb-2">Settings</h1>
          <p className="text-slate-400">Adjust this browser for the way you use GANGU.</p>
        </header>

        <div className="space-y-5">
          <Section icon={Globe2} title="Preferred language" subtitle="The greeting and confirmations adapt.">
            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  { v: 'hi', label: 'हिंदी' },
                  { v: 'en', label: 'English' },
                  { v: 'hinglish', label: 'Hinglish' },
                ] as { v: Language; label: string }[]
              ).map((opt) => (
                <Choice
                  key={opt.v}
                  label={opt.label}
                  active={draft.language === opt.v}
                  onClick={() => patch({ language: opt.v })}
                />
              ))}
            </div>
          </Section>

          <Section icon={MapPin} title="Default delivery address" subtitle="Required before you confirm an option.">
            <input
              type="text"
              value={draft.address}
              onChange={(e) => patch({ address: e.target.value })}
              placeholder="House, street, city and postcode"
              className="input-base"
            />
          </Section>

          <Section icon={Wallet} title="Payment preference" subtitle="Saved as a preference; the provider checkout controls available payment methods.">
            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  { v: 'upi', label: 'UPI' },
                  { v: 'cod', label: 'Cash on delivery' },
                  { v: 'card', label: 'Card' },
                ] as const
              ).map((opt) => (
                <Choice
                  key={opt.v}
                  label={opt.label}
                  active={draft.paymentMethod === opt.v}
                  onClick={() => patch({ paymentMethod: opt.v })}
                />
              ))}
            </div>
          </Section>

          <Section icon={Volume2} title="Voice speed" subtitle="How fast GANGU should reply when speaking.">
            <div className="grid grid-cols-3 gap-2">
              {(['slow', 'normal', 'fast'] as const).map((v) => (
                <Choice
                  key={v}
                  label={v.charAt(0).toUpperCase() + v.slice(1)}
                  active={draft.voiceSpeed === v}
                  onClick={() => patch({ voiceSpeed: v })}
                />
              ))}
            </div>
          </Section>

          <Section icon={Eye} title="Accessibility" subtitle="Make text and contrast easier on the eyes.">
            <div className="space-y-3">
              <Toggle
                label="Larger text"
                value={draft.largerText}
                onChange={(v) => patch({ largerText: v })}
              />
              <Toggle
                label="Higher contrast"
                value={draft.higherContrast}
                onChange={(v) => patch({ higherContrast: v })}
              />
            </div>
          </Section>

          <Section icon={ShieldCheck} title="Data & privacy" subtitle="Lists, contacts, order summaries and preferences on these screens are currently stored in this browser.">
            <p className="text-sm text-slate-500 leading-relaxed">
              Account export and account deletion are not available in this version. Contact support
              before using GANGU with personal or payment-sensitive information.
            </p>
          </Section>

          {user && (
            <Section icon={SettingsIcon} title="Account" subtitle="Your basic details.">
              <div className="space-y-3">
                <div>
                  <label className="block text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1.5">
                    Name
                  </label>
                  <input
                    type="text"
                    value={draftName}
                    onChange={(e) => setDraftName(e.target.value)}
                    className="input-base"
                  />
                </div>
                <Field label="Phone" value={user.phone} />
              </div>
            </Section>
          )}
        </div>
      </div>

      {/* Sticky save bar */}
      <div
        className={`fixed bottom-4 inset-x-0 z-40 px-4 transition-all duration-300 ${
          isDirty ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6 pointer-events-none'
        }`}
      >
        <div className="max-w-3xl mx-auto glass-strong rounded-2xl shadow-card border border-amber-500/30 px-5 py-3.5 flex items-center justify-between gap-4 animate-rise">
          <div className="flex items-center gap-3 min-w-0">
            <span className="w-9 h-9 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center flex-shrink-0">
              <Check className="w-4 h-4 text-amber-300" />
            </span>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-white">Unsaved changes</p>
              <p className="text-xs text-slate-400 truncate">Tap save to keep them in this browser.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button onClick={handleDiscard} className="btn-secondary text-sm">
              <RotateCcw className="w-4 h-4" />
              Discard
            </button>
            <button onClick={handleSave} className="btn-primary text-sm">
              <Save className="w-4 h-4" />
              Save changes
            </button>
          </div>
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

function Choice({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-2.5 rounded-xl text-sm font-semibold border transition-all ${
        active
          ? 'bg-amber-500/15 border-amber-500/50 text-amber-200'
          : 'bg-white/[0.04] border-white/10 text-slate-300 hover:border-white/20'
      }`}
    >
      {label}
    </button>
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
