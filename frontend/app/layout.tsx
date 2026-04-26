import type { Metadata, Viewport } from 'next'
import { Inter, Plus_Jakarta_Sans } from 'next/font/google'
import '@/styles/globals.css'

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
  title: 'GANGU — Voice-First Grocery, for Everyone',
  description:
    'GANGU is a voice-first AI assistant that orders your groceries in Hindi, English, or Hinglish. Six AI agents search every platform, pick the best deal, deliver in minutes.',
  keywords: ['grocery', 'voice assistant', 'AI', 'Hindi', 'Hinglish', 'India', 'Zepto', 'GANGU', 'elderly'],
  authors: [{ name: 'GANGU Labs' }],
  openGraph: {
    title: 'GANGU — Voice-First Grocery Assistant',
    description: 'Speak. We shop. Groceries delivered in minutes.',
    type: 'website',
    siteName: 'GANGU',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GANGU — Voice-First Grocery Assistant',
    description: 'Speak. We shop. Groceries delivered in minutes.',
  },
}

export const viewport: Viewport = {
  themeColor: '#07090F',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jakarta.variable}`}>
      <body className={inter.className}>
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  )
}
