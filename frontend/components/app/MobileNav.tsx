'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Mic, Package, ListOrdered, Users, Settings } from 'lucide-react'

const NAV = [
  { href: '/app',          label: 'Order',  icon: Mic },
  { href: '/app/orders',   label: 'Orders', icon: Package },
  { href: '/app/lists',    label: 'Lists',  icon: ListOrdered },
  { href: '/app/family',   label: 'Family', icon: Users },
  { href: '/app/settings', label: 'You',    icon: Settings },
]

export default function MobileNav() {
  const pathname = usePathname()

  return (
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-30 border-t border-white/10 bg-ink-950/95 backdrop-blur-xl">
      <div className="grid grid-cols-5">
        {NAV.map((item) => {
          const isActive = item.href === '/app' ? pathname === '/app' : pathname.startsWith(item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex flex-col items-center gap-1 py-2.5 transition-colors"
            >
              <Icon
                className={`w-5 h-5 ${isActive ? 'text-amber-300' : 'text-slate-500'}`}
                strokeWidth={isActive ? 2.5 : 2}
              />
              <span
                className={`text-[10px] font-semibold ${
                  isActive ? 'text-amber-200' : 'text-slate-500'
                }`}
              >
                {item.label}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
