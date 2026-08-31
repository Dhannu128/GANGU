'use client'

import { useEffect, useState, useSyncExternalStore } from 'react'
import { useRouter } from 'next/navigation'
import { useGANGUStore } from '@/lib/store'
import { connectWebSocket, disconnectWebSocket } from '@/lib/api'
import LeftRail from './LeftRail'
import MobileNav from './MobileNav'
import Logo from '@/components/Logo'
import Link from 'next/link'
import { Loader } from 'lucide-react'
import { onIdTokenChanged } from 'firebase/auth'
import { auth as firebaseAuth } from '@/lib/firebase'

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
  const [authReady, setAuthReady] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('gangu-large-text', settings.largerText)
    document.documentElement.classList.toggle('gangu-high-contrast', settings.higherContrast)
    return () => {
      document.documentElement.classList.remove('gangu-large-text', 'gangu-high-contrast')
    }
  }, [settings.largerText, settings.higherContrast])

  useEffect(() => onIdTokenChanged(firebaseAuth, async (firebaseUser) => {
    const store = useGANGUStore.getState()
    if (!firebaseUser) {
      store.signOut()
      setAuthReady(true)
      return
    }
    const existing = store.user
    store.signIn({
      id: firebaseUser.uid,
      name: firebaseUser.displayName || existing?.name || 'User',
      phone: firebaseUser.phoneNumber || existing?.phone || '',
      email: firebaseUser.email || existing?.email,
      photoURL: firebaseUser.photoURL || existing?.photoURL,
      language: existing?.language || 'hinglish',
      address: existing?.address || 'Please set your delivery address in settings',
    }, await firebaseUser.getIdToken())
    setAuthReady(true)
  }, () => {
    useGANGUStore.getState().signOut()
    setAuthReady(true)
  }), [])

  useEffect(() => {
    if (!hydrated || !authReady) return
    if (!auth.isAuthenticated) {
      router.replace('/signin')
    }
  }, [hydrated, authReady, auth.isAuthenticated, router])

  useEffect(() => {
    if (!hydrated || !authReady || !auth.isAuthenticated) return
    const id = sessionId || `session_${Date.now()}`
    if (!sessionId) setSessionId(id)
    void connectWebSocket(id)
    return () => {
      disconnectWebSocket()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hydrated, authReady, auth.isAuthenticated])

  if (!hydrated || !authReady) {
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
