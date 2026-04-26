import AuthShell from '@/components/auth/AuthShell'
import PhoneOtpForm from '@/components/auth/PhoneOtpForm'

export const metadata = {
  title: 'Sign in · GANGU',
}

export default function SignInPage() {
  return (
    <AuthShell title="Welcome back" subtitle="Sign in with your phone number to continue.">
      <PhoneOtpForm mode="signin" />
    </AuthShell>
  )
}
