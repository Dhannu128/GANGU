'use client'

import { useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { ArrowUp } from 'lucide-react'

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
        <div className="request-suggestions">
          <span>
            Try saying
          </span>
          {SUGGESTIONS.map((suggestion, i) => (
            <button
              key={i}
              onClick={() => handleSuggestionClick(suggestion)}
              className="suggestion-chip"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="request-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your request, e.g. '2 kg atta order karo'"
          disabled={isProcessing}
          className="request-field"
        />
        <button
          type="submit"
          disabled={!message.trim() || isProcessing}
          aria-label="Send"
          className="request-send"
        >
          <ArrowUp className="w-5 h-5" strokeWidth={2.5} />
        </button>
      </form>
    </div>
  )
}
