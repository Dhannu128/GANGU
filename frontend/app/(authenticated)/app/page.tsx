'use client'

import { useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { processUserInput, confirmOrder } from '@/lib/api'
import VoiceInput from '@/components/VoiceInput'
import TextInput from '@/components/TextInput'
import AgentTimeline from '@/components/AgentTimeline'
import ProductComparison from '@/components/ProductComparison'
import OrderConfirmation from '@/components/OrderConfirmation'
import SuccessScreen from '@/components/SuccessScreen'
import Greeting from '@/components/app/Greeting'
import TodayPanel from '@/components/app/TodayPanel'
import QuickReorder from '@/components/app/QuickReorder'
import EmptyState from '@/components/app/EmptyState'

export default function AppHome() {
  const {
    sessionId,
    setProcessing,
    setComparison,
    setRecommendation,
    setOrderPlaced,
    resetSession,
    orderPlaced,
    pastOrders,
    isProcessing,
    agentSteps,
  } = useGANGUStore()

  const [showConfirmation, setShowConfirmation] = useState(false)
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)

  const handleUserInput = async (message: string) => {
    try {
      setProcessing(true)
      const result = await processUserInput(message, sessionId || undefined)
      if (result.success) {
        setComparison(result.comparison)
        setRecommendation(result.recommendation)
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

  const handleNewOrder = () => {
    resetSession()
  }

  const handleReorderLast = () => {
    const last = pastOrders[0]
    if (!last) return
    handleUserInput(`Order ${last.itemSummary.split('·')[0].trim()}`)
  }

  const isFirstUse = pastOrders.length === 0 && agentSteps.length === 0 && !isProcessing

  return (
    <main className="min-h-screen pb-12">
      <div className="max-w-7xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* CENTER */}
          <div className="lg:col-span-2 order-2 lg:order-1">
            <Greeting onReorder={pastOrders[0] ? handleReorderLast : undefined} />

            <div className="surface-card p-6 md:p-9">
              <VoiceInput onTranscription={handleUserInput} />

              <div className="flex items-center gap-4 my-7">
                <div className="divider-line flex-1" />
                <span className="text-[10px] text-slate-500 uppercase tracking-[0.25em] font-bold">
                  or type
                </span>
                <div className="divider-line flex-1" />
              </div>

              <TextInput onSend={handleUserInput} />
            </div>

            {isFirstUse && <EmptyState onTry={handleUserInput} />}

            <ProductComparison
              onSelectProduct={(index) => {
                setSelectedProductIndex(index)
                setShowConfirmation(true)
              }}
            />
          </div>

          {/* RIGHT */}
          <div className="lg:col-span-1 order-1 lg:order-2">
            <div className="lg:sticky lg:top-5 space-y-0">
              <TodayPanel />
              <AgentTimeline />
              <QuickReorder onPick={handleUserInput} />
            </div>
          </div>
        </div>
      </div>

      {showConfirmation && (
        <OrderConfirmation
          onConfirm={handleConfirmOrder}
          onCancel={() => setShowConfirmation(false)}
          onChangeSelection={() => setShowConfirmation(false)}
        />
      )}
      {orderPlaced && <SuccessScreen onNewOrder={handleNewOrder} />}
    </main>
  )
}
