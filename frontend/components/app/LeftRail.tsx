'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import Logo from '@/components/Logo'
import { signOut as firebaseSignOut } from 'firebase/auth'
import { auth as firebaseAuth } from '@/lib/firebase'
import {
  Mic,
  Package,
  ListOrdered,
  Users,
  Settings,
  MapPin,
  ChevronDown,
  LogOut,
  Repeat,
} from 'lucide-react'

const NAV = [
  { href: '/app',          label: 'Order',        icon: Mic },
  { href: '/app/orders',   label: 'Past orders',  icon: Package },
  { href: '/app/lists',    label: 'Saved lists',  icon: ListOrdered },
  { href: '/app/family',   label: 'Family',       icon: Users },
  { href: '/app/settings', label: 'Settings',     icon: Settings },
]

export default function LeftRail() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, settings, signOut } = useGANGUStore()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleSignOut = async () => {
    try {
      await firebaseSignOut(firebaseAuth)
    } finally {
      signOut()
      router.push('/')
    }
  }

  const initials = (user?.name || 'U')
    .split(' ')
    .map((s) => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-[248px] lg:fixed lg:inset-y-0 lg:left-0 z-30 border-r border-[#d4dee8] bg-white">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2.5 h-[76px] px-5 border-b border-[#d4dee8]">
        <Logo size={32} />
        <div className="flex flex-col leading-none">
          <span className="font-display font-extrabold text-base tracking-tight">GANGU</span>
          <span className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-0.5">
            grocery · by voice
          </span>
        </div>
      </Link>

      {/* Nav */}
      <nav className="flex-1 px-3 py-5 space-y-0.5">
        {NAV.map((item) => {
          const isActive = item.href === '/app' ? pathname === '/app' : pathname.startsWith(item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                isActive
                  ? 'bg-[#ddf3f0] border border-[#9ed7d0] text-[#0a4f4a]'
                  : 'text-[#4f6072] hover:text-[#0a4f4a] hover:bg-[#eef4f8] border border-transparent'
              }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" strokeWidth={isActive ? 2.5 : 2} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Address pill */}
      <div className="px-3 pb-3">
        <Link
          href="/app/settings"
          className="block px-3 py-3 rounded-xl bg-[#eef4f8] border border-[#d4dee8] hover:border-[#0f766e] transition-all"
        >
          <div className="flex items-start gap-2.5">
            <MapPin className="w-4 h-4 text-[#0f766e] flex-shrink-0 mt-0.5" />
            <div className="min-w-0 flex-1">
              <p className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-0.5">
                Delivering to
              </p>
              <p className="text-xs text-slate-200 font-semibold leading-snug truncate">
                {settings.address || 'Add delivery address'}
              </p>
            </div>
            <Repeat className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
          </div>
        </Link>
      </div>

      {/* User menu */}
      <div className="border-t border-[#d4dee8] p-3 relative">
        {menuOpen && (
          <div className="absolute bottom-full left-3 right-3 mb-2 surface-card p-2 animate-fade-in">
            <button
              onClick={handleSignOut}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-rose-300 hover:bg-rose-500/10 transition-all"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        )}
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-full flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-[#eef4f8] transition-all"
        >
          <div className="w-9 h-9 rounded-full bg-[#ddf3f0] flex items-center justify-center font-display font-extrabold text-[#0a4f4a] text-sm">
            {initials}
          </div>
          <div className="flex-1 min-w-0 text-left">
            <p className="text-sm font-semibold text-white truncate">{user?.name || 'Guest'}</p>
            <p className="text-[10px] text-slate-500 truncate">{user?.phone || 'Read-only'}</p>
          </div>
          <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${menuOpen ? 'rotate-180' : ''}`} />
        </button>
      </div>
    </aside>
  )
}
