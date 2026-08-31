import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface AgentStep {
  step: string
  status: 'processing' | 'complete' | 'error'
  message: string
  data?: { platforms?: string[]; [key: string]: unknown }
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
  source?: string
}

export interface Comparison {
  products: Product[]
  recommended_index?: number
  reasoning?: string
}

export interface IntentResult {
  platforms?: string[]
  [key: string]: unknown
}

export interface RecommendationResult {
  selected_index?: number
  reasoning?: string
  [key: string]: unknown
}

export type Language = 'hi' | 'en' | 'hinglish'

export interface User {
  id: string
  name: string
  phone: string
  email?: string
  photoURL?: string
  language: Language
  address: string
}

export interface AuthState {
  isAuthenticated: boolean
  token: string | null
}

export interface PastOrder {
  id: string
  date: string
  itemSummary: string
  platform: string
  total: number
  status: 'delivered' | 'in_transit' | 'cancelled'
  steps?: AgentStep[]
}

export interface SavedList {
  id: string
  name: string
  items: string[]
  lastUsed?: string
}

export interface FamilyMember {
  id: string
  name: string
  relationship: string
  phone: string
  lastActive: string
  permissions: ('view' | 'order' | 'pay')[]
}

export interface Settings {
  language: Language
  address: string
  paymentMethod: 'upi' | 'cod' | 'card'
  voiceSpeed: 'slow' | 'normal' | 'fast'
  largerText: boolean
  higherContrast: boolean
}

export type ToastVariant = 'success' | 'error' | 'info'
export interface Toast {
  id: number
  variant: ToastVariant
  title: string
  description?: string
}

interface GANGUStore {
  // Connection
  connected: boolean
  sessionId: string | null

  // UI
  isListening: boolean
  isProcessing: boolean
  transcription: string

  // Pipeline
  agentSteps: AgentStep[]
  currentStep: string | null

  // Results
  intent: IntentResult | null
  comparison: Comparison | null
  recommendation: RecommendationResult | null

  // Order
  orderPlaced: boolean
  orderId: string | null
  orderSimulated: boolean

  // Cancel
  isCancelling: boolean
  isCancelled: boolean
  abortController: AbortController | null

  // Auth + user
  auth: AuthState
  user: User | null

  // App data (mock)
  pastOrders: PastOrder[]
  savedLists: SavedList[]
  familyMembers: FamilyMember[]
  settings: Settings

  // Toasts
  toasts: Toast[]

  // Actions
  setConnected: (connected: boolean) => void
  setSessionId: (sessionId: string) => void
  setListening: (listening: boolean) => void
  setProcessing: (processing: boolean) => void
  setTranscription: (text: string) => void
  addAgentStep: (step: AgentStep) => void
  setCurrentStep: (step: string | null) => void
  setIntent: (intent: IntentResult) => void
  setComparison: (comparison: Comparison) => void
  setRecommendation: (recommendation: RecommendationResult) => void
  setOrderPlaced: (placed: boolean, orderId?: string, simulated?: boolean) => void
  setCancelling: (cancelling: boolean) => void
  setCancelled: (cancelled: boolean) => void
  setAbortController: (controller: AbortController | null) => void
  resetSession: () => void

  // Auth actions
  signIn: (user: User, token: string) => void
  signOut: () => void
  updateSettings: (patch: Partial<Settings>) => void
  updateUser: (patch: Partial<User>) => void
  addPastOrder: (order: PastOrder) => void
  addSavedList: (list: SavedList) => void
  removeSavedList: (id: string) => void
  inviteFamilyMember: (member: FamilyMember) => void
  removeFamilyMember: (id: string) => void

  // Toasts
  pushToast: (toast: Omit<Toast, 'id'>) => void
  dismissToast: (id: number) => void
}

const DEMO_PAST_ORDERS: PastOrder[] = [
  {
    id: 'ORD-2026-0418',
    date: '2026-04-24',
    itemSummary: 'Aashirvaad Atta 5 kg',
    platform: 'Zepto',
    total: 285,
    status: 'delivered',
  },
  {
    id: 'ORD-2026-0411',
    date: '2026-04-21',
    itemSummary: 'Amul Taaza Milk 1 L · Britannia bread',
    platform: 'Zepto',
    total: 96,
    status: 'delivered',
  },
  {
    id: 'ORD-2026-0402',
    date: '2026-04-19',
    itemSummary: 'Tata Tea Premium 500 g',
    platform: 'Amazon',
    total: 240,
    status: 'delivered',
  },
  {
    id: 'ORD-2026-0394',
    date: '2026-04-15',
    itemSummary: 'Toor Dal 1 kg · Chana 1 kg',
    platform: 'Zepto',
    total: 198,
    status: 'delivered',
  },
]

const DEMO_LISTS: SavedList[] = [
  { id: 'list-1', name: 'Weekly basics', items: ['Atta 5 kg', 'Milk 1 L', 'Bread'], lastUsed: '2026-04-21' },
  { id: 'list-2', name: 'Morning chai', items: ['Tata Tea 500 g', 'Sugar 1 kg', 'Elaichi 50 g'] },
  { id: 'list-3', name: 'Festival cooking', items: ['Ghee 1 L', 'Kaju 250 g', 'Kishmish 200 g', 'Cardamom'] },
]

const DEMO_FAMILY: FamilyMember[] = [
  {
    id: 'fam-1',
    name: 'Aarav (Grandson)',
    relationship: 'Grandson',
    phone: '+91 98xxxxxx21',
    lastActive: '2 hours ago',
    permissions: ['view', 'order', 'pay'],
  },
]

const DEFAULT_SETTINGS: Settings = {
  language: 'hinglish',
  address: 'Home · 12, Rose Apt, Indore 452001',
  paymentMethod: 'upi',
  voiceSpeed: 'normal',
  largerText: false,
  higherContrast: false,
}

export const useGANGUStore = create<GANGUStore>()(
  persist(
    (set) => ({
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
      orderSimulated: false,
      isCancelling: false,
      isCancelled: false,
      abortController: null,

      auth: { isAuthenticated: false, token: null },
      user: null,

      pastOrders: [],
      savedLists: [],
      familyMembers: [],
      settings: DEFAULT_SETTINGS,

      toasts: [],

      setConnected: (connected) => set({ connected }),
      setSessionId: (sessionId) => set({ sessionId }),
      setListening: (listening) => set({ isListening: listening }),
      setProcessing: (processing) => set({ isProcessing: processing }),
      setTranscription: (text) => set({ transcription: text }),

      addAgentStep: (step) =>
        set((state) => {
          const i = state.agentSteps.findIndex((s) => s.step === step.step)
          if (i !== -1) {
            const updated = [...state.agentSteps]
            updated[i] = step
            return { agentSteps: updated, currentStep: step.step }
          }
          return { agentSteps: [...state.agentSteps, step], currentStep: step.step }
        }),

      setCurrentStep: (step) => set({ currentStep: step }),
      setIntent: (intent) => set({ intent }),
      setComparison: (comparison) => set({ comparison }),
      setRecommendation: (recommendation) => set({ recommendation }),
      setOrderPlaced: (placed, orderId, simulated = false) =>
        set({ orderPlaced: placed, orderId: orderId || null, orderSimulated: simulated }),
      setCancelling: (cancelling) => set({ isCancelling: cancelling }),
      setCancelled: (cancelled) =>
        set(
          cancelled
            ? { isCancelled: true, isCancelling: false, isProcessing: false }
            : { isCancelled: false }
        ),
      setAbortController: (controller) => set({ abortController: controller }),

      resetSession: () =>
        set({
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
          orderSimulated: false,
          isCancelling: false,
          isCancelled: false,
        }),

      signIn: (user, token) =>
        set((state) => {
          const returningUser = state.user?.id === user.id
          return {
            auth: { isAuthenticated: true, token },
            user,
            settings: returningUser
              ? state.settings
              : { ...DEFAULT_SETTINGS, language: user.language, address: user.address },
            pastOrders: state.pastOrders.length ? state.pastOrders : DEMO_PAST_ORDERS,
            savedLists: state.savedLists.length ? state.savedLists : DEMO_LISTS,
            familyMembers: state.familyMembers.length ? state.familyMembers : DEMO_FAMILY,
          }
        }),

      signOut: () =>
        set({
          auth: { isAuthenticated: false, token: null },
          user: null,
          pastOrders: [],
          savedLists: [],
          familyMembers: [],
          settings: DEFAULT_SETTINGS,
          isListening: false,
          isProcessing: false,
          transcription: '',
          agentSteps: [],
          comparison: null,
          recommendation: null,
          orderPlaced: false,
          orderId: null,
          orderSimulated: false,
        }),

      updateSettings: (patch) => set((s) => ({ settings: { ...s.settings, ...patch } })),
      updateUser: (patch) => set((s) => ({ user: s.user ? { ...s.user, ...patch } : s.user })),
      addPastOrder: (order) => set((s) => ({ pastOrders: [order, ...s.pastOrders] })),
      addSavedList: (list) => set((s) => ({ savedLists: [list, ...s.savedLists] })),
      removeSavedList: (id) => set((s) => ({ savedLists: s.savedLists.filter((l) => l.id !== id) })),
      inviteFamilyMember: (member) => set((s) => ({ familyMembers: [...s.familyMembers, member] })),
      removeFamilyMember: (id) =>
        set((s) => ({ familyMembers: s.familyMembers.filter((m) => m.id !== id) })),

      pushToast: (toast) =>
        set((s) => ({ toasts: [...s.toasts, { ...toast, id: Date.now() + Math.random() }] })),
      dismissToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
    }),
    {
      name: 'gangu-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        pastOrders: state.pastOrders,
        savedLists: state.savedLists,
        familyMembers: state.familyMembers,
        settings: state.settings,
      }),
    }
  )
)
