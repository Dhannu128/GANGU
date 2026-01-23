'use client'

import { useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { Send } from 'lucide-react'

interface TextInputProps {
  onSend: (message: string) => void
}

const SUGGESTIONS = [
  "Order groceries",
  "Compare prices",
  "White chane le aao",
  "Doodh khatam ho gaya",
  "Atta mangwao"
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

  const handleSuggestionClick = (suggestion: string) => {
    if (!isProcessing) {
      onSend(suggestion)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Suggestions */}
      {!isProcessing && message === '' && (
        <div className="mb-4 flex flex-wrap gap-2 justify-center">
          {SUGGESTIONS.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-4 py-2 bg-slate-700/50 text-slate-200 rounded-full text-sm 
                       hover:bg-blue-600 hover:text-white transition-colors
                       border border-slate-600 shadow-lg"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Text Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message... (e.g., White chane le aao)"
          disabled={isProcessing}
          className="w-full px-6 py-4 pr-14 rounded-full border-2 border-slate-600 
                   focus:border-blue-500 focus:outline-none text-lg
                   disabled:bg-slate-800 disabled:cursor-not-allowed
                   shadow-lg bg-slate-800/50 text-white placeholder-slate-400"
        />
        <button
          type="submit"
          disabled={!message.trim() || isProcessing}
          className="absolute right-2 top-1/2 transform -translate-y-1/2
                   w-10 h-10 rounded-full bg-blue-600 text-white
                   flex items-center justify-center
                   disabled:bg-slate-600 disabled:cursor-not-allowed
                   hover:bg-blue-500 transition-colors shadow-lg"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  )
}
