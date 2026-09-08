import axios, { type AxiosRequestConfig } from 'axios'
import { signOut as firebaseSignOut } from 'firebase/auth'
import { auth } from './firebase'
import { useGANGUStore } from './store'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || API_BASE_URL.replace(/^http/, 'ws').replace(/\/$/, '')

export const requestErrorMessage = (error: unknown): string => {
  if (!axios.isAxiosError(error)) return 'GANGU could not process your request. Please try again.'
  if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
    return 'The request took too long. Please wait a moment before trying again.'
  }
  if (!error.response) return 'Cannot reach GANGU. Please check your connection or try again when the service is available.'
  switch (error.response.status) {
    case 401: return 'Please sign in again to continue.'
    case 403: return 'This request is not available for your account. Please start a new session.'
    case 409: return 'Your previous request is still processing. Please wait for it to finish.'
    case 429: return 'The service is busy. Please wait a moment and try again.'
    case 503: return 'GANGU is temporarily unavailable. Please try again shortly.'
    default: return 'GANGU could not process your request. Please try again.'
  }
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { 'ngrok-skip-browser-warning': 'true' },
})

api.interceptors.request.use(async (config) => {
  const firebaseUser = auth.currentUser
  if (firebaseUser) config.headers.Authorization = `Bearer ${await firebaseUser.getIdToken()}`
  return config
})

type RetryableRequest = AxiosRequestConfig & { _authRetried?: boolean }

const expireLocalSession = () => {
  const store = useGANGUStore.getState()
  store.signOut()
  if (!store.toasts.some((toast) => toast.title === 'Your session has expired')) {
    store.pushToast({
      variant: 'error',
      title: 'Your session has expired',
      description: 'Please sign in again to continue safely.',
    })
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error) || error.response?.status !== 401 || !error.config) {
      return Promise.reject(error)
    }
    const original = error.config as RetryableRequest
    if (original._authRetried || !auth.currentUser) {
      await firebaseSignOut(auth).catch(() => undefined)
      expireLocalSession()
      return Promise.reject(error)
    }
    original._authRetried = true
    try {
      const token = await auth.currentUser.getIdToken(true)
      original.headers = { ...original.headers, Authorization: `Bearer ${token}` }
      return api.request(original)
    } catch {
      await firebaseSignOut(auth).catch(() => undefined)
      expireLocalSession()
      return Promise.reject(error)
    }
  },
)

let ws: WebSocket | null = null
let wsGeneration = 0

export const connectWebSocket = async (sessionId: string) => {
  const store = useGANGUStore.getState()
  const generation = wsGeneration
  if (ws && ws.readyState === WebSocket.OPEN) return ws
  try {
    const ticketResponse = await api.post('/api/auth/ws-ticket')
    if (generation !== wsGeneration) return null
    const ticket = encodeURIComponent(ticketResponse.data.ticket)
    ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}?ticket=${ticket}`)
  } catch {
    store.setConnected(false)
    return null
  }

  ws.onopen = () => store.setConnected(true)
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type !== 'agent_update') return
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
  ws.onerror = () => store.setConnected(false)
  ws.onclose = () => store.setConnected(false)
  return ws
}

export const disconnectWebSocket = () => {
  wsGeneration += 1
  ws?.close()
  ws = null
}

export const processUserInput = async (message: string, sessionId?: string, signal?: AbortSignal) =>
  (await api.post('/api/chat/process', { message, session_id: sessionId }, { signal })).data

export const confirmOrder = async (
  sessionId: string,
  quoteId: string,
  productIndex: number,
  deliveryAddress: string,
  paymentMethod: 'upi' | 'cod' | 'card',
) => (await api.post('/api/order/confirm', {
  session_id: sessionId,
  quote_id: quoteId,
  selected_product_index: productIndex,
  delivery_address: deliveryAddress,
  payment_method: paymentMethod,
})).data

export const getSessionData = async (sessionId: string) =>
  (await api.get(`/api/session/${sessionId}`)).data

export const getOrderHistory = async () => (await api.get('/api/history')).data

export const cancelProcessing = async (sessionId: string) =>
  (await api.post('/api/cancel', { session_id: sessionId })).data

export default api
