'use client'

import { useEffect } from 'react'
import { onIdTokenChanged } from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { useGANGUStore, type User } from '@/lib/store'

function userFromFirebase(firebaseUser: NonNullable<typeof auth.currentUser>, existing: User | null): User {
  const sameUser = existing?.id === firebaseUser.uid ? existing : null
  return {
    id: firebaseUser.uid,
    name: firebaseUser.displayName || sameUser?.name || 'GANGU user',
    phone: firebaseUser.phoneNumber || sameUser?.phone || '',
    email: firebaseUser.email || sameUser?.email,
    photoURL: firebaseUser.photoURL || sameUser?.photoURL,
    language: sameUser?.language || 'hinglish',
    address: sameUser?.address || '',
  }
}

export default function AuthSessionProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => onIdTokenChanged(
    auth,
    async (firebaseUser) => {
      const store = useGANGUStore.getState()
      if (!firebaseUser) {
        store.signOut()
        return
      }

      try {
        const token = await firebaseUser.getIdToken()
        store.signIn(userFromFirebase(firebaseUser, store.user), token)
      } catch {
        store.signOut()
      }
    },
    () => useGANGUStore.getState().signOut(),
  ), [])

  return children
}
