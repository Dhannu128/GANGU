'use client'

import { useGANGUStore } from '@/lib/store'
import { confirmOrder } from '@/lib/api'
import { useState } from 'react'
import { Check, X, Edit } from 'lucide-react'

interface OrderConfirmationProps {
  onConfirm: () => void
  onCancel: () => void
  onChangeSelection: () => void
}

export default function OrderConfirmation({
  onConfirm,
  onCancel,
  onChangeSelection
}: OrderConfirmationProps) {
  const { comparison, recommendation, sessionId } = useGANGUStore()
  const [loading, setLoading] = useState(false)

  if (!comparison || !recommendation || !comparison.products || comparison.products.length === 0) {
    return null
  }

  const selectedIndex = recommendation.selected_index ?? comparison.recommended_index ?? 0
  const selectedProduct = comparison.products[selectedIndex]
  
  if (!selectedProduct) {
    return null
  }

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="gangu-card max-w-lg w-full animate-fade-in">
        {/* Header */}
        <h3 className="text-2xl font-bold mb-4 text-gangu-dark">
          🛒 Confirm Your Order
        </h3>

        {/* Selected Product Summary */}
        <div className="bg-gangu-light p-4 rounded-lg mb-6">
          <p className="text-sm text-gray-600 mb-2">Selected Product:</p>
          <p className="font-semibold text-lg">{selectedProduct.name}</p>
          <p className="text-2xl font-bold text-gangu-primary mt-2">
            ₹{selectedProduct.price}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Platform: <span className="font-medium">{selectedProduct.platform}</span>
          </p>
          {selectedProduct.delivery_time && (
            <p className="text-sm text-gray-600">
              Delivery: <span className="font-medium">{selectedProduct.delivery_time}</span>
            </p>
          )}
        </div>

        {/* Reasoning */}
        {recommendation.reasoning && (
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <p className="text-sm font-semibold text-gray-700 mb-1">
              💡 Why GANGU recommends this:
            </p>
            <p className="text-sm text-gray-600">
              {recommendation.reasoning}
            </p>
          </div>
        )}

        {/* Confirmation Message */}
        <p className="text-center text-gray-700 mb-6">
          I'll place this order on <strong>{selectedProduct.platform}</strong>. 
          Should I proceed?
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col space-y-3">
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="gangu-btn-primary w-full flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Processing...
              </>
            ) : (
              <>
                <Check className="w-5 h-5 mr-2" />
                ✅ Confirm Purchase
              </>
            )}
          </button>

          <button
            onClick={onChangeSelection}
            disabled={loading}
            className="gangu-btn-secondary w-full flex items-center justify-center"
          >
            <Edit className="w-5 h-5 mr-2" />
            🔁 Change Option
          </button>

          <button
            onClick={onCancel}
            disabled={loading}
            className="text-gray-600 hover:text-gray-800 transition-colors"
          >
            <X className="w-5 h-5 inline mr-1" />
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
