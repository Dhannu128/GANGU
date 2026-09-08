'use client'

import { useEffect, useSyncExternalStore } from 'react'
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
  const { auth, setSessionId, sessionId, settings } = useGANGUStore()
  const hydrated = useSyncExternalStore(
    () => () => undefined,
    () => true,
    () => false,
  )

  useEffect(() => {
    document.documentElement.classList.toggle('gangu-large-text', settings.largerText)
    document.documentElement.classList.toggle('gangu-high-contrast', settings.higherContrast)
    return () => {
      document.documentElement.classList.remove('gangu-large-text', 'gangu-high-contrast')
    }
  }, [settings.largerText, settings.higherContrast])

  useEffect(() => {
    if (!hydrated || !auth.initialized) return
    if (!auth.isAuthenticated) {
      router.replace('/signin')
    }
  }, [hydrated, auth.initialized, auth.isAuthenticated, router])

  useEffect(() => {
    if (!hydrated || !auth.initialized || !auth.isAuthenticated) return
    const id = sessionId || `session_${Date.now()}`
    if (!sessionId) setSessionId(id)
    void connectWebSocket(id)
    return () => {
      disconnectWebSocket()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated, auth.initialized, auth.isAuthenticated])

  if (!hydrated || !auth.initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader className="w-6 h-6 text-[#0f766e] animate-spin" />
      </div>
    )
  }

  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 p-6 text-center">
        <Logo />
        <p className="text-[#4f6072]">Redirecting to sign in…</p>
        <Link href="/signin" className="btn-primary text-sm">
          Sign in
        </Link>
      </div>
    )
  }

  return (
    <div className="gangu-app min-h-screen relative">
      <LeftRail />
      <div className="lg:ml-[248px] pb-20 lg:pb-0">{children}</div>
      <MobileNav />
    </div>
  )
}
