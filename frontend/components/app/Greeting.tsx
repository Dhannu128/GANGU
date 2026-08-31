'use client'

import { useMemo } from 'react'
import { useGANGUStore } from '@/lib/store'

interface GreetingProps {
  onReorder?: () => void
}

const HINDI_GREETINGS = (h: number) => {
  if (h < 12) return 'सुप्रभात'
  if (h < 17) return 'नमस्ते'
  return 'शुभ संध्या'
}

const EN_GREETINGS = (h: number) => {
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function Greeting({ onReorder }: GreetingProps) {
  const { user, pastOrders, settings } = useGANGUStore()
  const hour = new Date().getHours()
  const lang = settings.language

  const firstName = (user?.name || 'friend').split(' ')[0]
  const greetingHi = HINDI_GREETINGS(hour)
  const greetingEn = EN_GREETINGS(hour)

  const lastOrder = pastOrders[0]
  const daysAgo = useMemo(() => lastOrder
    ? Math.max(0, Math.floor((new Date().getTime() - new Date(lastOrder.date).getTime()) / 86400000))
    : null, [lastOrder])

  let salutation: string
  if (lang === 'hi') {
    salutation = `${greetingHi}, ${firstName} जी`
  } else if (lang === 'en') {
    salutation = `${greetingEn}, ${firstName}`
  } else {
    salutation = `${greetingHi}, ${firstName}`
  }

  return (
    <div className="mb-8 animate-fade-in">
      <h1 className="text-display text-3xl md:text-4xl mb-2">
        {salutation} <span className="text-amber-300">·</span>{' '}
        <span className="text-slate-500 font-medium">What do you need?</span>
      </h1>
      {lastOrder && (
        <p className="text-sm text-slate-400">
          Last order{' '}
          <span className="text-slate-300 font-medium">
            {daysAgo === 0 ? 'today' : daysAgo === 1 ? 'yesterday' : `${daysAgo} days ago`}
          </span>
          : <span className="text-slate-200">{lastOrder.itemSummary}</span> from{' '}
          <span className="text-slate-200">{lastOrder.platform}</span>
          {onReorder && (
            <>
              {' — '}
              <button
                onClick={onReorder}
                className="text-amber-300 font-semibold hover:text-amber-200 underline underline-offset-2"
              >
                order again?
              </button>
            </>
          )}
        </p>
      )}
    </div>
  )
}
