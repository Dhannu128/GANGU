'use client'

import { useGANGUStore } from '@/lib/store'
import { CheckCircle, Package, Clock } from 'lucide-react'

interface SuccessScreenProps {
  onNewOrder: () => void
}

export default function SuccessScreen({ onNewOrder }: SuccessScreenProps) {
  const { orderId, comparison, recommendation } = useGANGUStore()

  if (!orderId) {
    return null
  }

  const selectedProduct = comparison?.products[recommendation?.selected_index || 0]

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center z-50 p-4">
      <div className="gangu-card max-w-lg w-full text-center animate-fade-in">
        {/* Success Icon */}
        <div className="mb-6">
          <div className="w-24 h-24 bg-gangu-success rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-16 h-16 text-white" />
          </div>
        </div>

        {/* Success Message */}
        <h2 className="text-3xl font-bold text-gangu-dark mb-2">
          🎉 Order Placed!
        </h2>
        <p className="text-lg text-gray-600 mb-6">
          Your order has been confirmed
        </p>

        {/* Order Details */}
        <div className="bg-white/50 p-6 rounded-lg mb-6 text-left">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-600">Order ID:</span>
            <span className="font-mono font-semibold">{orderId}</span>
          </div>

          {selectedProduct && (
            <>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-600">Product:</span>
                <span className="font-medium text-right max-w-xs">
                  {selectedProduct.name}
                </span>
              </div>

              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-600">Platform:</span>
                <span className="font-medium">{selectedProduct.platform}</span>
              </div>

              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-gray-600">Price:</span>
                <span className="text-xl font-bold text-gangu-primary">
                  ₹{selectedProduct.price}
                </span>
              </div>

              {selectedProduct.delivery_time && (
                <div className="flex items-center justify-center space-x-2 pt-4 border-t border-gray-200">
                  <Clock className="w-5 h-5 text-gangu-primary" />
                  <span className="font-medium text-gangu-primary">
                    Delivery: {selectedProduct.delivery_time}
                  </span>
                </div>
              )}
            </>
          )}
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={onNewOrder}
            className="gangu-btn-primary w-full"
          >
            Order Something Else
          </button>

          <button className="gangu-btn-secondary w-full">
            <Package className="w-5 h-5 inline mr-2" />
            Track Order
          </button>
        </div>

        {/* Thank You Message */}
        <p className="mt-6 text-sm text-gray-600">
          Thank you for using GANGU! 🙏
        </p>
      </div>
    </div>
  )
}
