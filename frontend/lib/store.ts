import { create } from 'zustand'

export interface AgentStep {
  step: string
  status: 'processing' | 'complete' | 'error'
  message: string
  data?: any
  timestamp: string
}

export interface Product {
  platform: string
  name: string
  price: number
  image?: string
  rating?: number
  delivery_time?: string
  stock_status?: string
}

export interface Comparison {
  products: Product[]
  recommended_index?: number
  reasoning?: string
}

interface GANGUStore {
  // Connection state
  connected: boolean
  sessionId: string | null
  
  // UI state
  isListening: boolean
  isProcessing: boolean
  transcription: string
  
  // Agent pipeline state
  agentSteps: AgentStep[]
  currentStep: string | null
  
  // Results state
  intent: any
  comparison: Comparison | null
  recommendation: any
  
  // Order state
  orderPlaced: boolean
  orderId: string | null
  
  // Cancellation state
  isCancelling: boolean
  isCancelled: boolean
  
  // Actions
  setConnected: (connected: boolean) => void
  setSessionId: (sessionId: string) => void
  setListening: (listening: boolean) => void
  setProcessing: (processing: boolean) => void
  setTranscription: (text: string) => void
  addAgentStep: (step: AgentStep) => void
  setCurrentStep: (step: string | null) => void
  setIntent: (intent: any) => void
  setComparison: (comparison: Comparison) => void
  setRecommendation: (recommendation: any) => void
  setOrderPlaced: (placed: boolean, orderId?: string) => void
  setCancelling: (cancelling: boolean) => void
  setCancelled: (cancelled: boolean) => void
  resetSession: () => void
}

export const useGANGUStore = create<GANGUStore>((set) => ({
  // Initial state
  connected: false,
  sessionId: null,
  isListening: false,
  isProcessing: false,
  transcription: '',
  agentSteps: [],
  currentStep: null,
  intent: null,
  comparison: null,
  recommendation: null,
  orderPlaced: false,
  orderId: null,
  isCancelling: false,
  isCancelled: false,
  
  // Actions
  setConnected: (connected) => set({ connected }),
  
  setSessionId: (sessionId) => set({ sessionId }),
  
  setListening: (listening) => set({ isListening: listening }),
  
  setProcessing: (processing) => set({ isProcessing: processing }),
  
  setTranscription: (text) => set({ transcription: text }),
  
  addAgentStep: (step) => set((state) => {
    // Check if step already exists, update it instead of adding
    const existingIndex = state.agentSteps.findIndex(s => s.step === step.step)
    
    if (existingIndex !== -1) {
      // Update existing step
      const updatedSteps = [...state.agentSteps]
      updatedSteps[existingIndex] = step
      return {
        agentSteps: updatedSteps,
        currentStep: step.step
      }
    } else {
      // Add new step
      return {
        agentSteps: [...state.agentSteps, step],
        currentStep: step.step
      }
    }
  }),
  
  setCurrentStep: (step) => set({ currentStep: step }),
  
  setIntent: (intent) => set({ intent }),
  
  setComparison: (comparison) => set({ comparison }),
  
  setRecommendation: (recommendation) => set({ recommendation }),
  
  setOrderPlaced: (placed, orderId) => set({ 
    orderPlaced: placed,
    orderId: orderId || null
  }),
  
  setCancelling: (cancelling) => set({ isCancelling: cancelling }),
  
  setCancelled: (cancelled) => set({ isCancelled: cancelled }),
  
  resetSession: () => set({
    isListening: false,
    isProcessing: false,
    transcription: '',
    agentSteps: [],
    currentStep: null,
    intent: null,
    comparison: null,
    recommendation: null,
    orderPlaced: false,
    orderId: null,
    isCancelling: false,
    isCancelled: false
  })
}))
