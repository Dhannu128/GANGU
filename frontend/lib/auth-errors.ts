import { FirebaseError } from 'firebase/app'

const AUTH_MESSAGES: Record<string, string> = {
  'auth/invalid-phone-number': 'Enter a valid 10-digit Indian mobile number.',
  'auth/missing-phone-number': 'Enter your mobile number first.',
  'auth/invalid-verification-code': 'That code is incorrect. Check the SMS and try again.',
  'auth/code-expired': 'That code has expired. Request a new one.',
  'auth/too-many-requests': 'Too many attempts. Please wait a while before trying again.',
  'auth/quota-exceeded': 'SMS sign-in is temporarily unavailable. Try Google sign-in instead.',
  'auth/popup-closed-by-user': 'Google sign-in was cancelled.',
  'auth/popup-blocked': 'Your browser blocked the sign-in window. Allow pop-ups and try again.',
  'auth/cancelled-popup-request': 'Another sign-in window is already open.',
  'auth/unauthorized-domain': 'This website has not been authorized in Firebase yet.',
  'auth/operation-not-allowed': 'This sign-in method is not enabled in Firebase yet.',
  'auth/network-request-failed': 'Could not reach Firebase. Check your internet connection.',
  'auth/captcha-check-failed': 'The security check expired. Please try again.',
  'auth/missing-app-credential': 'The phone security check could not start. Refresh and try again.',
}

export function authErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof FirebaseError) return AUTH_MESSAGES[error.code] || fallback
  return error instanceof Error ? error.message : fallback
}
