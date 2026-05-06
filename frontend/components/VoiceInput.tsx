'use client'

import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Languages } from 'lucide-react'
import { useGANGUStore } from '@/lib/store'

interface VoiceInputProps {
  onTranscription: (text: string) => void
}

// Web Speech API runs entirely in the user's browser — no audio upload,
// no API key, no backend round-trip. Chrome/Edge support hi-IN well, which
// covers Hindi, English, and Hinglish mix. Firefox does not implement
// SpeechRecognition; users on Firefox will see "voice not supported" and
// can fall back to the text input.
export default function VoiceInput({ onTranscription }: VoiceInputProps) {
  const { isListening, setListening, transcription, setTranscription, isProcessing } = useGANGUStore()
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<any>(null)
  const finalTextRef = useRef<string>('')

  useEffect(() => {
    if (typeof window === 'undefined') return
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    setIsSupported(!!SR)
  }, [])

  const startListening = () => {
    if (typeof window === 'undefined') return
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition
    if (!SR) {
      alert('Voice input is not supported in this browser. Please use Chrome or Edge.')
      return
    }

    finalTextRef.current = ''
    setTranscription('')

    const recognition = new SR()
    // hi-IN handles Hindi + Roman-script English / Hinglish on Chrome.
    recognition.lang = 'hi-IN'
    recognition.continuous = false
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onresult = (event: any) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript
        if (event.results[i].isFinal) final += t
        else interim += t
      }
      if (final) {
        finalTextRef.current = (finalTextRef.current + ' ' + final).trim()
        setTranscription(finalTextRef.current)
      } else if (interim) {
        setTranscription((finalTextRef.current + ' ' + interim).trim())
      }
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      if (event.error === 'no-speech') {
        // benign — user tapped mic but didn't speak
      } else if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        alert('Microphone permission denied. Allow it in browser settings.')
      } else if (event.error === 'network') {
        alert('Voice service network error. Check your internet and try again.')
      }
      setListening(false)
    }

    recognition.onend = () => {
      setListening(false)
      const finalText = finalTextRef.current.trim()
      if (finalText) onTranscription(finalText)
    }

    recognitionRef.current = recognition
    try {
      recognition.start()
      setListening(true)
    } catch (e) {
      console.error('Failed to start recognition:', e)
      setListening(false)
    }
  }

  const stopListening = () => {
    try {
      recognitionRef.current?.stop()
    } catch {}
    setListening(false)
  }

  const disabled = !isSupported || isProcessing

  return (
    <div className="flex flex-col items-center gap-7">
      {/* Mic button with concentric rings */}
      <div className="relative">
        {isListening && (
          <>
            <span className="absolute inset-0 rounded-full bg-rose-500/30 animate-ping" />
            <span className="absolute -inset-3 rounded-full border border-rose-400/30" />
            <span className="absolute -inset-6 rounded-full border border-rose-400/15" />
          </>
        )}

        <button
          onClick={isListening ? stopListening : startListening}
          className={`mic-button ${isListening ? 'active' : disabled ? '' : 'idle'}`}
          disabled={disabled}
          aria-label={isListening ? 'Stop recording' : 'Start recording'}
        >
          {isListening ? <MicOff className="w-12 h-12" strokeWidth={2} /> : <Mic className="w-12 h-12" strokeWidth={2} />}
        </button>
      </div>

      {/* Status */}
      <div className="text-center min-h-[68px]">
        {isListening ? (
          <div className="flex flex-col items-center gap-3 animate-fade-in">
            <p className="text-lg font-bold text-rose-300">
              सुन रहा हूँ <span className="text-slate-500 font-normal">·</span> Listening
            </p>
            <div className="flex items-end gap-1 h-4">
              {[0, 1, 2, 3, 4].map((i) => (
                <span
                  key={i}
                  className="w-1 rounded-full bg-gradient-to-t from-rose-500 to-rose-300"
                  style={{
                    height: '100%',
                    animation: `voicewave 0.9s ease-in-out ${i * 0.12}s infinite`,
                  }}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="animate-fade-in">
            <p className="text-base font-semibold text-slate-200 mb-1.5">
              {isSupported ? 'Tap to speak' : 'Voice not supported · use Chrome or Edge'}
            </p>
            <p className="text-sm text-slate-500 inline-flex items-center gap-1.5">
              <Languages className="w-3.5 h-3.5" />
              हिंदी · English · Hinglish
            </p>
          </div>
        )}
      </div>

      {/* Live transcription */}
      {transcription && (
        <div className="w-full max-w-xl glass rounded-2xl p-5 animate-rise">
          <p className="text-[10px] text-amber-300 mb-2 uppercase tracking-widest font-bold">You said</p>
          <p className="text-base text-white font-medium leading-relaxed">{transcription}</p>
        </div>
      )}

      <style jsx global>{`
        @keyframes voicewave {
          0%, 100% { transform: scaleY(0.4); }
          50%      { transform: scaleY(1); }
        }
      `}</style>
    </div>
  )
}
