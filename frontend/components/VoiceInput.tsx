'use client'

import { useState, useRef } from 'react'
import { Mic, MicOff, Languages } from 'lucide-react'
import { useGANGUStore } from '@/lib/store'

interface VoiceInputProps {
  onTranscription: (text: string) => void
}

interface SpeechRecognitionEventLike {
  resultIndex: number
  results: ArrayLike<{ 0: { transcript: string }; isFinal: boolean }>
}

interface SpeechRecognitionErrorLike { error: string }
interface SpeechRecognitionLike {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  onresult: ((event: SpeechRecognitionEventLike) => void) | null
  onerror: ((event: SpeechRecognitionErrorLike) => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
}
type SpeechRecognitionConstructor = new () => SpeechRecognitionLike

function speechRecognitionConstructor(): SpeechRecognitionConstructor | undefined {
  if (typeof window === 'undefined') return undefined
  const speechWindow = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionConstructor
    webkitSpeechRecognition?: SpeechRecognitionConstructor
  }
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition
}

// Web Speech API runs entirely in the user's browser — no audio upload,
// no API key, no backend round-trip. Chrome/Edge support hi-IN well, which
// covers Hindi, English, and Hinglish mix. Firefox does not implement
// SpeechRecognition; users on Firefox will see "voice not supported" and
// can fall back to the text input.
export default function VoiceInput({ onTranscription }: VoiceInputProps) {
  const { isListening, setListening, transcription, setTranscription, isProcessing, settings } = useGANGUStore()
  const [isSupported] = useState(() => Boolean(speechRecognitionConstructor()))
  const [voiceError, setVoiceError] = useState('')
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const finalTextRef = useRef<string>('')

  const startListening = () => {
    const SR = speechRecognitionConstructor()
    if (!SR) {
      setVoiceError('Voice input is unavailable in this browser. You can type your request below.')
      return
    }

    setVoiceError('')
    finalTextRef.current = ''
    setTranscription('')

    const recognition = new SR()
    // hi-IN handles Hindi + Roman-script English / Hinglish on Chrome.
    recognition.lang = settings.language === 'en' ? 'en-IN' : 'hi-IN'
    recognition.continuous = false
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    recognition.onresult = (event: SpeechRecognitionEventLike) => {
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

    recognition.onerror = (event: SpeechRecognitionErrorLike) => {
      if (event.error === 'no-speech') {
        setVoiceError('We did not hear anything. Tap the microphone and try again, or type below.')
      } else if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        setVoiceError('Microphone access is blocked. Select the site controls beside the address bar, allow Microphone, then try again—or type below.')
      } else if (event.error === 'network') {
        setVoiceError('Voice recognition could not reach the network. Check your connection or type below.')
      } else if (event.error === 'aborted') {
        setVoiceError('Voice input stopped. You can try again or type below.')
      } else {
        setVoiceError('Voice input could not start. Please try again or type your request below.')
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
    } catch {
      setVoiceError('The microphone could not start. Please try again or type below.')
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

      {voiceError && <p className="voice-error" role="alert">{voiceError}</p>}

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
