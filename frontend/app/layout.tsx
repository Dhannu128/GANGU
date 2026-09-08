import type { Metadata, Viewport } from 'next'
import { Inter, Plus_Jakarta_Sans } from 'next/font/google'
import '@/styles/globals.css'
import ToastViewport from '@/components/Toast'
import AuthSessionProvider from '@/components/auth/AuthSessionProvider'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-jakarta',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'GANGU — Voice-first grocery help',
  description:
    'Ask for groceries in Hindi, English, or Hinglish, compare available options, and review every detail before confirming.',
  keywords: ['grocery', 'voice assistant', 'Hindi', 'Hinglish', 'India', 'GANGU', 'accessibility'],
  authors: [{ name: 'GANGU Labs' }],
  openGraph: {
    title: 'GANGU — Voice-first grocery help',
    description: 'Speak or type, compare available options, and confirm only when you are ready.',
    type: 'website',
    siteName: 'GANGU',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GANGU — Voice-first grocery help',
    description: 'Speak or type, compare available options, and confirm only when you are ready.',
  },
}

export const viewport: Viewport = {
  themeColor: '#f3f7fb',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jakarta.variable}`}>
      <body className={inter.className}>
        <AuthSessionProvider>
          <div className="relative z-10">{children}</div>
          <ToastViewport />
        </AuthSessionProvider>
      </body>
    </html>
  )
}
