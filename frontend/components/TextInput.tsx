'use client'

import { useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { ArrowUp, Sparkles } from 'lucide-react'

interface TextInputProps {
  onSend: (message: string) => void
}

const SUGGESTIONS = [
  '2 kg atta order karo',
  'Doodh khatam ho gaya',
  'White chane le aao',
  'Order milk and bread',
  'Chai patti chahiye',
]

export default function TextInput({ onSend }: TextInputProps) {
  const [message, setMessage] = useState('')
  const { isProcessing } = useGANGUStore()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isProcessing) {
      onSend(message.trim())
      setMessage('')
    }
  }

  const handleSuggestionClick = (s: string) => {
    if (!isProcessing) onSend(s)
  }

  return (
    <div className="w-full">
      {/* Suggestions */}
      {!isProcessing && message === '' && (
        <div className="mb-4 flex flex-wrap gap-2 justify-center animate-fade-in">
          <span className="inline-flex items-center gap-1.5 text-xs text-slate-500 font-semibold uppercase tracking-widest mr-1 self-center">
            <Sparkles className="w-3 h-3" /> Try
          </span>
          {SUGGESTIONS.map((suggestion, i) => (
            <button
              key={i}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-3.5 py-1.5 rounded-full text-sm text-slate-300 bg-white/[0.04]
                         border border-white/10 hover:border-amber-500/40 hover:text-white
                         hover:bg-amber-500/[0.06] transition-all duration-200"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your request, e.g. '2 kg atta order karo'"
          disabled={isProcessing}
          className="input-base pr-16 text-base"
        />
        <button
          type="submit"
          disabled={!message.trim() || isProcessing}
          aria-label="Send"
          className="absolute right-2 top-1/2 -translate-y-1/2 w-11 h-11 rounded-xl
                     flex items-center justify-center text-white
                     bg-gradient-to-br from-amber-400 to-orange-600
                     shadow-glow-sm hover:shadow-glow disabled:opacity-40
                     disabled:cursor-not-allowed disabled:from-slate-600 disabled:to-slate-700
                     disabled:shadow-none transition-all"
        >
          <ArrowUp className="w-5 h-5" strokeWidth={2.5} />
        </button>
      </form>
    </div>
  )
}
