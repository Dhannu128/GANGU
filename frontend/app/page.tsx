'use client'

import { useEffect, useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { connectWebSocket, disconnectWebSocket, processUserInput, confirmOrder } from '@/lib/api'
import VoiceInput from '@/components/VoiceInput'
import TextInput from '@/components/TextInput'
import AgentTimeline from '@/components/AgentTimeline'
import ProductComparison from '@/components/ProductComparison'
import OrderConfirmation from '@/components/OrderConfirmation'
import SuccessScreen from '@/components/SuccessScreen'

export default function Home() {
  const {
    sessionId,
    setSessionId,
    setProcessing,
    setComparison,
    setRecommendation,
    setOrderPlaced,
    resetSession,
    orderPlaced
  } = useGANGUStore()

  const [showConfirmation, setShowConfirmation] = useState(false)
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)

  // Initialize WebSocket connection
  useEffect(() => {
    const newSessionId = `session_${Date.now()}`
    setSessionId(newSessionId)
    connectWebSocket(newSessionId)

    return () => {
      disconnectWebSocket()
    }
  }, [])

  // Handle user input (voice or text)
  const handleUserInput = async (message: string) => {
    try {
      setProcessing(true)

      const result = await processUserInput(message, sessionId || undefined)

      if (result.success) {
        setComparison(result.comparison)
        setRecommendation(result.recommendation)

        // Auto-show confirmation if recommendation exists
        if (result.recommendation && result.recommendation.selected_index !== undefined) {
          setShowConfirmation(true)
          setSelectedProductIndex(result.recommendation.selected_index)
        } else if (result.comparison && result.comparison.recommended_index !== undefined) {
          setShowConfirmation(true)
          setSelectedProductIndex(result.comparison.recommended_index)
        }
      }
    } catch (error) {
      console.error('Error processing input:', error)
      alert('Sorry, something went wrong. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  // Handle order confirmation
  const handleConfirmOrder = async () => {
    try {
      if (!sessionId) return

      const result = await confirmOrder(sessionId, selectedProductIndex)

      if (result.success) {
        setOrderPlaced(true, result.order_id)
        setShowConfirmation(false)
      }
    } catch (error) {
      console.error('Error confirming order:', error)
      alert('Failed to place order. Please try again.')
    }
  }

  // Handle new order (reset)
  const handleNewOrder = () => {
    resetSession()
    const newSessionId = `session_${Date.now()}`
    setSessionId(newSessionId)
    connectWebSocket(newSessionId)
  }

  return (
    <main className="min-h-screen relative">
      {/* Professional Header with Gradient */}
      <header className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900 via-blue-800 to-purple-900"></div>
        <div className="absolute inset-0 backdrop-blur-sm"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 py-16 text-center">
          <div className="animate-float">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-2xl mb-6">
              <span className="text-4xl">🛒</span>
            </div>
            <h1 className="text-6xl font-bold text-white mb-4 tracking-tight">
              GANGU
            </h1>
            <p className="text-xl text-blue-200 font-semibold mb-3">
              AI-Powered Grocery Assistant
            </p>
            <p className="text-blue-300/80 text-sm max-w-2xl mx-auto leading-relaxed">
              Simply speak or type what you need • Our AI agents search multiple platforms • Get the best deals instantly
            </p>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 left-0 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"></div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Side - Input Section (Larger) */}
          <div className="lg:col-span-2">
            <section className="gangu-card">
              <div className="text-center mb-10">
                <h2 className="text-4xl font-bold text-white mb-4">
                  What do you need today?
                </h2>
                <p className="text-slate-400 text-lg">Speak naturally or type your request below</p>
              </div>

              {/* Voice Input */}
              <div className="mb-10">
                <VoiceInput onTranscription={handleUserInput} />
              </div>

              {/* Divider */}
              <div className="flex items-center justify-center my-10">
                <div className="border-t border-slate-600 flex-grow max-w-md"></div>
                <span className="px-8 text-slate-400 text-base font-medium bg-slate-800/50 rounded-full py-2 border border-slate-600">or type</span>
                <div className="border-t border-slate-600 flex-grow max-w-md"></div>
              </div>

              {/* Text Input */}
              <TextInput onSend={handleUserInput} />
            </section>

            {/* Product Comparison */}
            <section className="mt-8">
              <ProductComparison
                onSelectProduct={(index) => {
                  setSelectedProductIndex(index)
                  setShowConfirmation(true)
                }}
              />
            </section>
          </div>

          {/* Right Side - Agent Workflow Status (Smaller, Sticky) */}
          <div className="lg:col-span-1">
            <section className="sticky top-4">
              <AgentTimeline />
            </section>
          </div>
        </div>
      </div>

      {/* Order Confirmation Modal */}
      {showConfirmation && (
        <OrderConfirmation
          onConfirm={handleConfirmOrder}
          onCancel={() => setShowConfirmation(false)}
          onChangeSelection={() => setShowConfirmation(false)}
        />
      )}

      {/* Success Screen */}
      {orderPlaced && (
        <SuccessScreen onNewOrder={handleNewOrder} />
      )}

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-white/10">
        <div className="text-center">
          <p className="text-slate-300 font-medium mb-2">GANGU - AI-Powered Grocery Shopping 🛒</p>
          <p className="text-slate-500 text-xs">Powered by Advanced AI • Built with ❤️ in India</p>
        </div>
      </footer>
    </main>
  )
}
