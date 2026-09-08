'use client'

import { useEffect, useRef, useState } from 'react'
import { useGANGUStore } from '@/lib/store'
import { processUserInput, confirmOrder, requestErrorMessage } from '@/lib/api'
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
import { AlertCircle, WifiOff } from 'lucide-react'

interface RawProduct {
  name?: string
  brand?: string
  platform: string
  price?: number
  delivery_time?: string
  rating?: number
  stock_status?: string
  image?: string
  url?: string
  product_identity?: { canonical_name?: string; original_name?: string; brand?: string }
  normalized_attributes?: {
    price?: number
    delivery_time_label?: string
    rating?: number
    availability?: boolean
  }
  [key: string]: unknown
}

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
    settings,
  } = useGANGUStore()

  const [showConfirmation, setShowConfirmation] = useState(false)
  const [selectedProductIndex, setSelectedProductIndex] = useState(0)
  const [quoteId, setQuoteId] = useState<string | null>(null)
  const [requestError, setRequestError] = useState('')
  const [isOnline, setIsOnline] = useState(() => typeof navigator === 'undefined' || navigator.onLine)

  // Abort controller for the in-flight chat/process request, so cancel can
  // tear down the HTTP request immediately instead of waiting for the
  // backend to finish the current agent.
  const abortRef = useRef<AbortController | null>(null)
  const { setAbortController } = useGANGUStore()

  useEffect(() => {
    const online = () => setIsOnline(true)
    const offline = () => setIsOnline(false)
    window.addEventListener('online', online)
    window.addEventListener('offline', offline)
    return () => {
      abortRef.current?.abort()
      window.removeEventListener('online', online)
      window.removeEventListener('offline', offline)
    }
  }, [])

  const handleUserInput = async (message: string) => {
    if (!navigator.onLine) {
      setRequestError('You are offline. Reconnect to the internet and try again.')
      return
    }
    setRequestError('')
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setAbortController(controller)

    try {
      setProcessing(true)
      const result = await processUserInput(message, sessionId || undefined, controller.signal)
      if (result.success) {
        // Backend now returns `ranked_products` and `requires_confirmation`,
        // not `products` / `recommended_index` / `selected_index`. Normalise
        // the shape here so every downstream component reads the same fields.
        // ranked_products from comparison_agent nests under product_identity
        // and normalized_attributes; the UI expects flat fields. Flatten.
        const rawProducts =
          result.comparison?.ranked_products ||
          result.comparison?.products ||
          []
        const products = rawProducts.map((p: RawProduct) => ({
          ...p,
          name:
            p.name ||
            p.product_identity?.canonical_name ||
            p.product_identity?.original_name ||
            'Unknown product',
          brand: p.brand || p.product_identity?.brand,
          platform: p.platform,
          price: p.price ?? p.normalized_attributes?.price ?? 0,
          delivery_time:
            p.delivery_time || p.normalized_attributes?.delivery_time_label,
          rating: p.rating ?? p.normalized_attributes?.rating,
          stock_status:
            p.stock_status ||
            (p.normalized_attributes?.availability ? 'in_stock' : undefined),
          image: p.image,
          url: p.url,
        }))
        const recommendedIndex =
          result.comparison?.recommended_index ??
          result.recommendation?.selected_index ??
          0
        const normalizedComparison = {
          ...result.comparison,
          products,
          recommended_index: recommendedIndex,
        }
        const normalizedRecommendation = {
          ...result.recommendation,
          selected_index: recommendedIndex,
        }
        setComparison(normalizedComparison)
        setRecommendation(normalizedRecommendation)
        setQuoteId(result.quote_id || null)

        if (result.requires_confirmation && products.length > 0) {
          setSelectedProductIndex(recommendedIndex)
          setShowConfirmation(true)
        }
      }
    } catch (error: unknown) {
      const cancellation = error as { name?: string; code?: string }
      if (cancellation?.name === 'CanceledError' || cancellation?.code === 'ERR_CANCELED' || controller.signal.aborted) {
        // Cancelled by user — silent, store already updated by handleCancel.
      } else {
        console.error('Error processing input:', error)
        setRequestError(requestErrorMessage(error))
      }
    } finally {
      setProcessing(false)
      if (abortRef.current === controller) {
        abortRef.current = null
        setAbortController(null)
      }
    }
  }

  const handleConfirmOrder = async () => {
    try {
      if (!sessionId || !quoteId) return
      if (!settings.address.trim()) {
        setRequestError('Add a delivery address in Settings before confirming.')
        return
      }
      setRequestError('')
      const result = await confirmOrder(
        sessionId,
        quoteId,
        selectedProductIndex,
        settings.address,
        settings.paymentMethod,
      )
      if (result.success) {
        setOrderPlaced(true, result.order_id, result.simulated === true)
        setShowConfirmation(false)
      }
    } catch (error) {
      console.error('Error confirming order:', error)
      setRequestError('We could not verify the order result. Check your provider order history before trying again.')
    }
  }

  const handleNewOrder = () => {
    resetSession()
    setQuoteId(null)
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
        {!isOnline && (
          <div className="status-notice offline" role="status"><WifiOff aria-hidden /><span><strong>You are offline.</strong> Voice and product search will work again after you reconnect.</span></div>
        )}
        {requestError && (
          <div className="status-notice error" role="alert"><AlertCircle aria-hidden /><span>{requestError}</span><button onClick={() => setRequestError('')} aria-label="Dismiss error">Dismiss</button></div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* CENTER */}
          <div className="lg:col-span-2 order-1">
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
                setRecommendation({
                  ...(useGANGUStore.getState().recommendation ?? {}),
                  selected_index: index,
                })
                setShowConfirmation(true)
              }}
            />
          </div>

          {/* RIGHT */}
          <div className="lg:col-span-1 order-2">
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
          selectedProductIndex={selectedProductIndex}
          onConfirm={handleConfirmOrder}
          onCancel={() => setShowConfirmation(false)}
          onChangeSelection={() => setShowConfirmation(false)}
        />
      )}
      {orderPlaced && <SuccessScreen onNewOrder={handleNewOrder} />}
    </main>
  )
}
