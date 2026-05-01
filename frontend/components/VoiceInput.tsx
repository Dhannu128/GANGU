'use client'

import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Languages } from 'lucide-react'
import { useGANGUStore } from '@/lib/store'

interface VoiceInputProps {
  onTranscription: (text: string) => void
}

export default function VoiceInput({ onTranscription }: VoiceInputProps) {
  const { isListening, setListening, transcription, setTranscription, isProcessing } = useGANGUStore()
  const [isSupported, setIsSupported] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  useEffect(() => {
    setIsSupported(typeof window !== 'undefined' && 'MediaRecorder' in window)
  }, [])

  const startListening = async () => {
    if (!isSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome or Edge.')
      return
    }

    try {
      setListening(true)
      audioChunksRef.current = []

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)
        stream.getTracks().forEach((t) => t.stop())
      }

      mediaRecorder.start()
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access microphone. Please check permissions.')
      setListening(false)
    }
  }

  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    setListening(false)
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')

      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBase}/api/voice/whisper`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success && data.text) {
        setTranscription(data.text)
        onTranscription(data.text)
      } else {
        alert('Could not transcribe audio. Please try again.')
      }
    } catch (error) {
      console.error('Transcription error:', error)
      alert('Error transcribing audio. Please try again.')
    }
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
              {isSupported ? 'Tap to speak' : 'Voice not supported in this browser'}
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
