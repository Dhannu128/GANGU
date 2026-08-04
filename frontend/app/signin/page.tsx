import { redirect } from 'next/navigation'

export default function SignInRedirect() {
  // We use the same page for Sign Up and Sign In since it's passwordless (Google & OTP)
  redirect('/signup')
}
