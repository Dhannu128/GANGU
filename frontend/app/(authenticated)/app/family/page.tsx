'use client'

import { useState } from 'react'
import { useGANGUStore, type FamilyMember } from '@/lib/store'
import { Users, UserPlus, Phone, Shield, Trash2, Sparkles, X, Heart } from 'lucide-react'

const PERMISSION_LABEL: Record<FamilyMember['permissions'][number], string> = {
  view: 'Can view',
  order: 'Can order',
  pay: 'Can pay',
}

export default function FamilyPage() {
  const { familyMembers, inviteFamilyMember, removeFamilyMember } = useGANGUStore()

  const [inviting, setInviting] = useState(false)
  const [draftName, setDraftName] = useState('')
  const [draftRel, setDraftRel] = useState('')
  const [draftPhone, setDraftPhone] = useState('')
  const [draftPerms, setDraftPerms] = useState<FamilyMember['permissions']>(['view', 'order'])

  const togglePerm = (p: FamilyMember['permissions'][number]) => {
    setDraftPerms((arr) => (arr.includes(p) ? arr.filter((x) => x !== p) : [...arr, p]))
  }

  const handleInvite = () => {
    if (!draftName.trim() || !draftPhone.trim()) return
    inviteFamilyMember({
      id: `fam-${Date.now()}`,
      name: draftName.trim(),
      relationship: draftRel.trim() || 'Family',
      phone: draftPhone.trim(),
      lastActive: 'Just invited',
      permissions: draftPerms,
    })
    setInviting(false)
    setDraftName('')
    setDraftRel('')
    setDraftPhone('')
    setDraftPerms(['view', 'order'])
  }

  return (
    <main className="min-h-screen pb-12">
      <div className="max-w-4xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <header className="mb-8 flex items-end justify-between gap-4">
          <div>
            <span className="pill-cyan mb-3 inline-flex">
              <Heart className="w-3 h-3" />
              For families
            </span>
            <h1 className="text-display text-3xl md:text-4xl mb-2">Family</h1>
            <p className="text-slate-400 max-w-xl">
              Invite your children or grandchildren to manage orders on your behalf — they can
              review, top-up wallet, and set spending limits without taking control of your account.
            </p>
          </div>
          <button onClick={() => setInviting(true)} className="btn-primary text-sm flex-shrink-0">
            <UserPlus className="w-4 h-4" />
            Invite
          </button>
        </header>

        {inviting && (
          <div className="surface-card p-6 mb-5 animate-rise">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-display text-xl">Invite a family member</h3>
              <button
                onClick={() => setInviting(false)}
                className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 flex items-center justify-center text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="space-y-3 mb-5">
              <input
                type="text"
                value={draftName}
                onChange={(e) => setDraftName(e.target.value)}
                placeholder="Name (e.g. Aarav)"
                className="input-base"
              />
              <input
                type="text"
                value={draftRel}
                onChange={(e) => setDraftRel(e.target.value)}
                placeholder="Relationship (e.g. Grandson)"
                className="input-base"
              />
              <input
                type="tel"
                value={draftPhone}
                onChange={(e) => setDraftPhone(e.target.value)}
                placeholder="+91 phone number"
                className="input-base"
              />
            </div>

            <p className="text-xs uppercase tracking-widest font-bold text-slate-500 mb-3">Permissions</p>
            <div className="flex flex-wrap gap-2 mb-5">
              {(['view', 'order', 'pay'] as const).map((p) => {
                const on = draftPerms.includes(p)
                return (
                  <button
                    key={p}
                    onClick={() => togglePerm(p)}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                      on
                        ? 'bg-amber-500/15 border-amber-500/45 text-amber-200'
                        : 'bg-white/[0.04] border-white/10 text-slate-400 hover:border-white/20'
                    }`}
                  >
                    {PERMISSION_LABEL[p]}
                  </button>
                )
              })}
            </div>

            <button
              onClick={handleInvite}
              disabled={!draftName.trim() || !draftPhone.trim()}
              className="btn-primary w-full"
            >
              <Sparkles className="w-4 h-4" />
              Send invite
            </button>
          </div>
        )}

        {familyMembers.length === 0 && !inviting ? (
          <div className="surface-card p-10 text-center">
            <Users className="w-10 h-10 mx-auto mb-4 text-slate-700" />
            <p className="text-slate-400 mb-5">No family members linked yet.</p>
            <button onClick={() => setInviting(true)} className="btn-primary">
              <UserPlus className="w-4 h-4" />
              Invite your first family member
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {familyMembers.map((m) => (
              <article key={m.id} className="surface-card p-6">
                <div className="flex items-start gap-4 mb-5">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-400 to-fuchsia-600 flex items-center justify-center font-display font-extrabold text-ink-950 text-base flex-shrink-0">
                    {m.name
                      .split(' ')
                      .map((s) => s[0])
                      .filter(Boolean)
                      .slice(0, 2)
                      .join('')
                      .toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white text-base">{m.name}</h3>
                    <p className="text-xs text-slate-400">{m.relationship}</p>
                    <p className="text-xs text-slate-500 mt-1.5 inline-flex items-center gap-1.5">
                      <Phone className="w-3 h-3" />
                      {m.phone}
                    </p>
                  </div>
                  <button
                    onClick={() => removeFamilyMember(m.id)}
                    className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-rose-500/15 hover:border-rose-500/30 hover:text-rose-300 text-slate-500 flex items-center justify-center transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {m.permissions.map((p) => (
                    <span key={p} className="pill-amber">
                      <Shield className="w-3 h-3" />
                      {PERMISSION_LABEL[p]}
                    </span>
                  ))}
                </div>

                <p className="text-xs text-slate-500 pt-4 border-t border-white/5">
                  Last active <span className="text-slate-300 font-semibold">{m.lastActive}</span>
                </p>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
