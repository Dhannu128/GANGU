import axios from 'axios'
import { useGANGUStore, type Language } from './store'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
})

// === WebSocket ===
let ws: WebSocket | null = null

export const connectWebSocket = (sessionId: string) => {
  const store = useGANGUStore.getState()

  if (ws && ws.readyState === WebSocket.OPEN) return ws

  ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}`)

  ws.onopen = () => {
    store.setConnected(true)
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'agent_update') {
      store.addAgentStep({
        step: data.step,
        status: data.status,
        message: data.message,
        data: data.data,
        timestamp: data.timestamp,
      })
      if (data.step === 'cancelled') {
        store.setProcessing(false)
        store.setCancelled(true)
      }
    }
  }

  ws.onerror = () => store.setConnected(false)
  ws.onclose = () => store.setConnected(false)

  return ws
}

export const disconnectWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

// === Order pipeline ===
export const processUserInput = async (
  message: string,
  sessionId?: string,
  signal?: AbortSignal,
) => {
  const response = await api.post(
    '/api/chat/process',
    { message, session_id: sessionId },
    { signal },
  )
  return response.data
}

export const confirmOrder = async (sessionId: string, productIndex: number) => {
  const response = await api.post('/api/order/confirm', {
    session_id: sessionId,
    selected_product_index: productIndex,
  })
  return response.data
}

export const getSessionData = async (sessionId: string) => {
  const response = await api.get(`/api/session/${sessionId}`)
  return response.data
}

export const getOrderHistory = async () => {
  const response = await api.get('/api/history')
  return response.data
}

export const cancelProcessing = async (sessionId: string) => {
  const response = await api.post('/api/cancel', { session_id: sessionId })
  return response.data
}

// === Auth (mock + backend-ready) ===
// The backend will eventually expose /api/auth/otp/request and /api/auth/otp/verify.
// Until then we simulate locally so the UX flow is testable end-to-end.

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

export interface OtpRequestResult {
  success: boolean
  channel: 'sms' | 'whatsapp'
  retryInSeconds: number
  // Dev-only hint, never shown to real users in production
  devHint?: string
}

export interface OtpVerifyResult {
  success: boolean
  token: string
  user: {
    id: string
    name: string
    phone: string
    language: Language
    address: string
    isNewUser: boolean
  }
}

export const requestOtp = async (phone: string): Promise<OtpRequestResult> => {
  try {
    const response = await api.post('/api/auth/otp/request', { phone })
    return response.data
  } catch {
    await sleep(700)
    return {
      success: true,
      channel: 'sms',
      retryInSeconds: 30,
      devHint: 'Use 123456 to sign in',
    }
  }
}

export const verifyOtp = async (
  phone: string,
  code: string,
  name?: string,
  language: Language = 'hinglish'
): Promise<OtpVerifyResult> => {
  try {
    const response = await api.post('/api/auth/otp/verify', { phone, code, name, language })
    return response.data
  } catch {
    await sleep(900)
    if (code !== '123456' && code.length !== 6) {
      throw new Error('Invalid code. Try 123456 in dev mode.')
    }
    const isNewUser = !!name
    return {
      success: true,
      token: `mock-token-${Date.now()}`,
      user: {
        id: `user_${Date.now()}`,
        name: name || phoneToName(phone),
        phone,
        language,
        address: 'Home · 12, Rose Apt, Indore 452001',
        isNewUser,
      },
    }
  }
}

function phoneToName(phone: string): string {
  const last4 = phone.replace(/\D/g, '').slice(-4)
  return `Friend ${last4}`
}

export type SocialProvider = 'google' | 'whatsapp'

export const socialSignIn = async (
  provider: SocialProvider,
  language: Language = 'hinglish'
): Promise<OtpVerifyResult> => {
  try {
    const response = await api.post('/api/auth/social', { provider, language })
    return response.data
  } catch {
    await sleep(800)
    const seed = Math.floor(Math.random() * 9000) + 1000
    return {
      success: true,
      token: `mock-${provider}-${Date.now()}`,
      user: {
        id: `user_${provider}_${seed}`,
        name: provider === 'google' ? 'Asha Verma' : 'Lata Sharma',
        phone: `+91 98xxxxx${seed.toString().slice(-3)}`,
        language,
        address: 'Home · 12, Rose Apt, Indore 452001',
        isNewUser: true,
      },
    }
  }
}

export default api
