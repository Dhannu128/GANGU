'use client'

import { useGANGUStore } from '@/lib/store'
import { Star, Truck, ShieldCheck, Sparkles, Package } from 'lucide-react'

interface ProductComparisonProps {
  onSelectProduct: (productIndex: number) => void
}

export default function ProductComparison({ onSelectProduct }: ProductComparisonProps) {
  const { comparison, recommendation } = useGANGUStore()

  if (!comparison || !comparison.products || comparison.products.length === 0) {
    return null
  }

  const recommendedIndex = recommendation?.selected_index ?? comparison.recommended_index ?? 0

  return (
    <section className="mt-10 animate-rise">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-7">
        <div>
          <span className="pill-amber mb-3">
            <Sparkles className="w-3 h-3" />
            Best matches
          </span>
          <h2 className="text-display text-3xl md:text-4xl mt-2">
            We found <span className="gradient-text-warm">{comparison.products.length} options</span>
          </h2>
          <p className="text-slate-400 mt-2">Tap any card to order. Our pick is highlighted.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {comparison.products.map((product, index) => {
          const isRecommended = index === recommendedIndex
          return (
            <article
              key={index}
              onClick={() => onSelectProduct(index)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  onSelectProduct(index)
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`Choose ${product.name} from ${product.platform} for ₹${product.price}`}
              className={`product-card ${isRecommended ? 'recommended' : ''}`}
            >
              {/* Recommended badge */}
              {isRecommended && (
                <div className="absolute -top-3 left-5 z-10">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold text-ink-950 bg-gradient-to-r from-amber-300 to-orange-400 shadow-glow-sm">
                    <Sparkles className="w-3 h-3" strokeWidth={3} />
                    AI Recommended
                  </span>
                </div>
              )}

              {/* Platform + stock */}
              <div className="flex items-center justify-between mb-4 mt-2">
                <span className="inline-flex items-center gap-2 text-sm font-bold text-slate-200">
                  <span className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                    {product.platform === 'Amazon' ? (
                      <Package className="w-4 h-4 text-amber-300" />
                    ) : product.platform === 'Swiggy' ? (
                      <Truck className="w-4 h-4 text-orange-400" />
                    ) : (
                      <Truck className="w-4 h-4 text-cyan-300" />
                    )}
                  </span>
                  {product.platform}
                </span>
                {product.stock_status === 'in_stock' && (
                  <span className="pill-emerald">
                    <ShieldCheck className="w-3 h-3" />
                    In stock
                  </span>
                )}
              </div>

              {/* Image */}
              {product.image && (
                <div className="mb-5 rounded-xl bg-gradient-to-br from-white/[0.04] to-white/[0.01] border border-white/5 p-4 aspect-square flex items-center justify-center overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-contain transition-transform duration-300 hover:scale-105"
                    onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
                  />
                </div>
              )}

              {/* Name */}
              <h3 className="font-semibold text-white text-base mb-3 line-clamp-2 leading-snug min-h-[3rem]">
                {product.name}
              </h3>

              {/* Price */}
              <div className="flex items-baseline gap-2 mb-4">
                <p className="text-3xl font-display font-extrabold text-white tracking-tight">
                  ₹{product.price}
                </p>
                <span className="text-xs text-slate-500 font-medium">best price</span>
              </div>

              {/* Meta row */}
              <div className="flex flex-wrap gap-2 mb-4">
                {product.rating != null && (
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-amber-200 bg-amber-500/10 border border-amber-500/25 px-2.5 py-1 rounded-lg">
                    <Star className="w-3.5 h-3.5 fill-amber-300 text-amber-300" />
                    {product.rating}
                  </span>
                )}
                {product.delivery_time && (
                  <span className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-200 bg-cyan-500/10 border border-cyan-500/25 px-2.5 py-1 rounded-lg">
                    <Truck className="w-3.5 h-3.5" />
                    {product.delivery_time}
                  </span>
                )}
              </div>

              {/* Reasoning for recommended */}
              {isRecommended && recommendation?.reasoning && (
                <div className="mt-4 pt-4 border-t border-white/5">
                  <p className="text-xs text-slate-300 leading-relaxed italic">
                    <span className="text-amber-300 font-bold not-italic">Why this:</span>{' '}
                    {recommendation.reasoning}
                  </p>
                </div>
              )}

              {/* CTA */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onSelectProduct(index)
                }}
                className={`mt-4 w-full ${isRecommended ? 'btn-primary' : 'btn-secondary'} text-sm`}
              >
                {isRecommended ? 'Order this →' : 'Choose this'}
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}
