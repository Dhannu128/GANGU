'use client'

import { CheckCircle2, Clock, Package, RotateCcw } from 'lucide-react'
import { useGANGUStore } from '@/lib/store'

export default function SuccessScreen({ onNewOrder }: { onNewOrder: () => void }) {
  const { orderId, orderSimulated, comparison, recommendation } = useGANGUStore()
  if (!orderId) return null
  const selectedProduct = comparison?.products[recommendation?.selected_index || 0]

  return (
    <div className="result-overlay" role="dialog" aria-modal="true" aria-labelledby="result-heading">
      <div className="result-dialog">
        <CheckCircle2 className="result-icon" aria-hidden />
        <p className="eyebrow">{orderSimulated ? 'Safe demonstration complete' : 'Order confirmed'}</p>
        <h2 id="result-heading">{orderSimulated ? 'No real order was placed' : 'Your order is confirmed'}</h2>
        <p className="result-summary">
          {orderSimulated
            ? 'GANGU tested the confirmation flow using estimated or demo product data. You were not charged.'
            : 'The shopping platform accepted your confirmed order.'}
        </p>

        <dl className="result-details">
          <div><dt>Reference</dt><dd>{orderId}</dd></div>
          {selectedProduct && <>
            <div><dt>Item</dt><dd>{selectedProduct.name}</dd></div>
            <div><dt>Platform</dt><dd>{selectedProduct.platform}</dd></div>
            <div><dt>{orderSimulated ? 'Estimated total' : 'Total'}</dt><dd>₹{selectedProduct.price}</dd></div>
            {selectedProduct.delivery_time && <div><dt><Clock aria-hidden /> Delivery estimate</dt><dd>{selectedProduct.delivery_time}</dd></div>}
          </>}
        </dl>

        <button onClick={onNewOrder} className="primary-action result-action"><RotateCcw aria-hidden /> Start another request</button>
        {!orderSimulated && <button className="secondary-action result-action"><Package aria-hidden /> Track this order</button>}
      </div>
    </div>
  )
}
