'use client'

import { useGANGUStore, Product } from '@/lib/store'
import { Star, Truck, Package } from 'lucide-react'
import Image from 'next/image'

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
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-3">
          🛒 Best Options Found
        </h2>
        <p className="text-slate-400 text-lg">Compare and choose the perfect product for you</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{comparison.products.map((product, index) => {
          const isRecommended = index === recommendedIndex

          return (
            <div
              key={index}
              className={`product-card ${isRecommended ? 'recommended' : ''} cursor-pointer hover:shadow-2xl transition-all duration-300`}
              onClick={() => onSelectProduct(index)}
            >
              {/* Recommendation Badge */}
              {isRecommended && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10 animate-float">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-5 py-2 rounded-full text-sm font-bold shadow-2xl border border-blue-400">
                    ⭐ AI Recommended
                  </span>
                </div>
              )}

              {/* Platform Logo */}
              <div className="flex items-center justify-between mb-4">
                <span className="font-bold text-xl text-white flex items-center">
                  {product.platform === 'Amazon' ? '📦' : '⚡'} {product.platform}
                </span>
                {product.stock_status === 'in_stock' && (
                  <span className="text-xs bg-green-500/20 text-green-300 px-3 py-1 rounded-full font-semibold border border-green-500/30">
                    ✓ In Stock
                  </span>
                )}
              </div>

              {/* Product Image */}
              {product.image && (
                <div className="mb-4 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-xl p-4 hover:scale-105 transition-transform duration-300">
                  <Image
                    src={product.image}
                    alt={product.name}
                    width={200}
                    height={200}
                    className="w-full h-48 object-contain"
                  />
                </div>
              )}

              {/* Product Name */}
              <h3 className="font-semibold text-white mb-3 line-clamp-2 text-lg">
                {product.name}
              </h3>

              {/* Price */}
              <div className="mb-4">
                <p className="text-4xl font-bold text-blue-400 mb-1">
                  ₹{product.price}
                </p>
                <p className="text-xs text-slate-500">Best price available</p>
              </div>

              {/* Rating */}
              {product.rating && (
                <div className="flex items-center mb-3 bg-yellow-500/10 px-3 py-2 rounded-lg w-fit border border-yellow-500/20">
                  <Star className="w-5 h-5 text-yellow-400 fill-current" />
                  <span className="ml-2 text-sm font-bold text-yellow-300">
                    {product.rating}
                  </span>
                </div>
              )}

              {/* Delivery Time */}
              {product.delivery_time && (
                <div className="flex items-center text-sm text-cyan-300 bg-cyan-500/10 px-3 py-2 rounded-lg mb-3 border border-cyan-500/20">
                  <Truck className="w-5 h-5 mr-2 text-cyan-400" />
                  <span className="font-medium">{product.delivery_time}</span>
                </div>
              )}

              {/* Reasoning (for recommended) */}
              {isRecommended && recommendation?.reasoning && (
                <div className="mt-4 pt-4 border-t border-gangu-primary/20">
                  <p className="text-sm text-gray-700 italic">
                    💡 {recommendation.reasoning}
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
