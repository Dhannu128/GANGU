'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useGANGUStore } from '@/lib/store'
import { connectWebSocket, disconnectWebSocket } from '@/lib/api'
import LeftRail from './LeftRail'
import MobileNav from './MobileNav'
import Logo from '@/components/Logo'
import Link from 'next/link'
import { Loader } from 'lucide-react'

interface AppShellProps {
  children: React.ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const router = useRouter()
  const { auth, setSessionId, sessionId } = useGANGUStore()
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    setHydrated(true)
  }, [])

  useEffect(() => {
    if (!hydrated) return
    if (!auth.isAuthenticated) {
      router.replace('/signin')
    }
  }, [hydrated, auth.isAuthenticated, router])

  useEffect(() => {
    if (!hydrated || !auth.isAuthenticated) return
    const id = sessionId || `session_${Date.now()}`
    if (!sessionId) setSessionId(id)
    connectWebSocket(id)
    return () => {
      disconnectWebSocket()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated, auth.isAuthenticated])

  if (!hydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader className="w-6 h-6 text-amber-300 animate-spin" />
      </div>
    )
  }

  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-6 text-center">
        <Logo />
        <p className="text-slate-400">Redirecting to sign in…</p>
        <Link href="/signin" className="btn-primary text-sm">
          Sign in
        </Link>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative">
      <LeftRail />
      <div className="lg:ml-[240px] pb-20 lg:pb-0">{children}</div>
      <MobileNav />
    </div>
  )
}
