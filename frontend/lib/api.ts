import axios from 'axios'
import { useGANGUStore } from './store'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for agent processing
})

// WebSocket connection
let ws: WebSocket | null = null

export const connectWebSocket = (sessionId: string) => {
  const store = useGANGUStore.getState()
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    return ws
  }
  
  ws = new WebSocket(`${WS_BASE_URL}/ws/${sessionId}`)
  
  ws.onopen = () => {
    console.log('✅ WebSocket connected')
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
        timestamp: data.timestamp
      })
      
      // If cancelled, stop processing
      if (data.step === 'cancelled') {
        store.setProcessing(false)
        store.setCancelled(true)
      }
    }
  }
  
  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error)
    store.setConnected(false)
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected')
    store.setConnected(false)
  }
  
  return ws
}

export const disconnectWebSocket = () => {
  if (ws) {
    ws.close()
    ws = null
  }
}

// API Functions
export const processUserInput = async (message: string, sessionId?: string) => {
  const response = await api.post('/api/chat/process', {
    message,
    session_id: sessionId
  })
  return response.data
}

export const confirmOrder = async (sessionId: string, productIndex: number) => {
  const response = await api.post('/api/order/confirm', {
    session_id: sessionId,
    selected_product_index: productIndex
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
  const response = await api.post('/api/cancel', {
    session_id: sessionId
  })
  return response.data
}

export default api
