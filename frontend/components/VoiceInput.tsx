'use client'

import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff } from 'lucide-react'
import { useGANGUStore } from '@/lib/store'

interface VoiceInputProps {
  onTranscription: (text: string) => void
}

export default function VoiceInput({ onTranscription }: VoiceInputProps) {
  const { isListening, setListening, transcription, setTranscription } = useGANGUStore()
  const [isSupported, setIsSupported] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  useEffect(() => {
    // Check if browser supports MediaRecorder
    setIsSupported('MediaRecorder' in window)
  }, [])

  const startListening = async () => {
    if (!isSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome or Edge.')
      return
    }

    try {
      setListening(true)
      audioChunksRef.current = []

      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        // Send to Whisper API
        await transcribeAudio(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
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

      const response = await fetch('http://localhost:8000/api/voice/whisper', {
        method: 'POST',
        body: formData
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

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* Main Mic Button with enhanced styling */}
      <div className="relative">
        {/* Pulsing ring effect when listening */}
        {isListening && (
          <>
            <div className="absolute inset-0 rounded-full bg-blue-500 opacity-20 animate-ping"></div>
            <div className="absolute inset-0 rounded-full bg-blue-500 opacity-30 pulse-glow"></div>
          </>
        )}
        
        <button
          onClick={isListening ? stopListening : startListening}
          className={`relative mic-button ${isListening ? 'active' : ''} transition-all duration-300 hover:scale-105`}
          disabled={!isSupported}
        >
          {isListening ? (
            <MicOff className="w-10 h-10" />
          ) : (
            <Mic className="w-10 h-10" />
          )}
        </button>
      </div>

      {/* Status Text */}
      <div className="text-center">
        {isListening ? (
          <div className="space-y-3">
            <p className="text-xl font-bold text-blue-400 animate-pulse">
              सुन रहा हूँ... / Listening...
            </p>
            <div className="flex justify-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0s' }}></div>
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        ) : (
          <div>
            <p className="text-slate-300 font-medium text-lg">
              {isSupported ? '🎤 Tap to speak' : '❌ Voice not supported'}
            </p>
            <p className="text-slate-500 text-sm mt-1">Hindi, English, or Hinglish</p>
          </div>
        )}
      </div>

      {/* Live Transcription */}
      {transcription && (
        <div className="mt-2 p-5 bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-2xl max-w-md animate-fade-in shadow-xl border border-blue-500/30">
          <p className="text-xs text-blue-300 mb-2 uppercase tracking-wide font-semibold">You said:</p>
          <p className="text-lg text-white font-medium">{transcription}</p>
        </div>
      )}
    </div>
  )
}
