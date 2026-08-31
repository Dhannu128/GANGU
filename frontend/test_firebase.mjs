import { initializeApp } from 'firebase/app'
import { getAuth, signInAnonymously } from 'firebase/auth'

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
}

if (!firebaseConfig.apiKey || !firebaseConfig.authDomain || !firebaseConfig.projectId) {
  console.error('Set the NEXT_PUBLIC_FIREBASE_* environment variables before running this check.')
  process.exit(1)
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

signInAnonymously(auth)
  .then(() => {
    console.log('Firebase anonymous authentication succeeded.')
    process.exit(0)
  })
  .catch((error) => {
    console.error('Firebase authentication failed:', error.code, error.message)
    process.exit(1)
  })
