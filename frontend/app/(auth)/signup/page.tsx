import AuthShell from '@/components/auth/AuthShell'
import PhoneOtpForm from '@/components/auth/PhoneOtpForm'

export const metadata = {
  title: 'Create account · GANGU',
}

export default function SignUpPage() {
  return (
    <AuthShell
      title="Create your account"
      subtitle="Just a phone number — no passwords, no forms."
    >
      <PhoneOtpForm mode="signup" />
    </AuthShell>
  )
}
