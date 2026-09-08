import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, RecaptchaVerifier } from 'firebase/auth';

// Firebase configuration — loaded from environment variables.
// Set these in your .env.local file and in Vercel's Environment Variables dashboard.
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyCL1sZJUe_8GGm_V_aRC08clTr1bTZkkCM",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "gangu-adffd.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "gangu-adffd",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "gangu-adffd.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "312067199230",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:312067199230:web:7766e60e3a957e3fad55af",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-1XQZ1PNZCZ"
};

// Prevent duplicate Firebase app instances (causes crashes in Next.js dev/prod)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();

// Initialize Firebase Auth
const auth = getAuth(app);
auth.useDeviceLanguage(); // Set language to device default for SMS

// Initialize Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

export { app, auth, googleProvider, RecaptchaVerifier };
