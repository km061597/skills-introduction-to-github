import Image from 'next/image'
import { formatPriceForScreenReader, formatRatingForScreenReader } from '../utils/accessibility'

export default function ProductCard({ product, index = 0 }) {
  const {
    asin,
    title,
    brand,
    current_price,
    list_price,
    unit_price,
    unit_type,
    discount_pct,
    rating,
    review_count,
    image_url,
    amazon_url,
    is_prime,
    is_sponsored,
    subscribe_save_pct,
    savings_vs_category,
    is_best_value
  } = product

  const priceScreenReader = formatPriceForScreenReader(current_price)
  const ratingScreenReader = formatRatingForScreenReader(rating, review_count)
  const unitPriceScreenReader = unit_price
    ? `Unit price: ${formatPriceForScreenReader(unit_price)} per ${unit_type}`
    : ''

  return (
    <article
      className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-4 flex flex-col h-full focus-within:ring-2 focus-within:ring-blue-500"
      aria-label={`${title}${is_sponsored ? ' - Sponsored' : ''}${is_best_value ? ' - Best unit price' : ''}`}
    >
      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-3" role="list" aria-label="Product badges">
        {is_best_value && (
          <span
            className="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded"
            role="status"
            aria-label="Best unit price in category"
          >
            <span aria-hidden="true">🏆</span> BEST UNIT PRICE
          </span>
        )}
        {is_sponsored && (
          <span
            className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded"
            role="status"
            aria-label="This is a sponsored product"
          >
            SPONSORED
          </span>
        )}
        {savings_vs_category && savings_vs_category > 20 && (
          <span
            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded"
            role="status"
            aria-label={`Hidden gem: ${Number(savings_vs_category).toFixed(0)}% below category average`}
          >
            <span aria-hidden="true">💎</span> Hidden Gem
          </span>
        )}
      </div>

      {/* Image */}
      <div className="relative w-full h-48 mb-4">
        <img
          src={image_url || 'https://via.placeholder.com/300x300?text=No+Image'}
          alt={`${title}${brand ? ` by ${brand}` : ''}`}
          className="w-full h-full object-contain"
          loading="lazy"
        />
      </div>

      {/* Title */}
      <h3 className="text-sm font-medium text-gray-900 mb-2 line-clamp-2 flex-grow">
        <span className="sr-only">Product: </span>
        {title}
      </h3>

      {/* Brand */}
      {brand && (
        <p className="text-xs text-gray-500 mb-2">{brand}</p>
      )}

      {/* Price Section */}
      <div className="mb-3">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-2xl font-bold text-gray-900" aria-label={`Current price: ${priceScreenReader}`}>
            <span aria-hidden="true">${current_price ? Number(current_price).toFixed(2) : 'N/A'}</span>
          </span>
          {list_price && Number(list_price) > Number(current_price) && (
            <span
              className="text-sm text-gray-500 line-through"
              aria-label={`Original price: ${formatPriceForScreenReader(list_price)}`}
            >
              <span aria-hidden="true">${Number(list_price).toFixed(2)}</span>
            </span>
          )}
        </div>

        {/* Unit Price - PRIMARY METRIC */}
        {unit_price && (
          <div className="mb-2">
            <span className="text-lg font-bold text-blue-600" aria-label={unitPriceScreenReader}>
              <span aria-hidden="true">${Number(unit_price).toFixed(4)}/{unit_type}</span>
            </span>
          </div>
        )}

        {/* Discount */}
        {discount_pct && discount_pct > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <span
              className="px-2 py-1 bg-red-100 text-red-800 rounded"
              role="status"
              aria-label={`${Number(discount_pct).toFixed(0)} percent discount`}
            >
              <span aria-hidden="true">-{Number(discount_pct).toFixed(0)}% OFF</span>
            </span>
          </div>
        )}

        {/* Savings vs Category */}
        {savings_vs_category && savings_vs_category > 0 && (
          <p className="text-sm text-green-600 font-medium mt-1" role="status">
            <span aria-hidden="true">📉</span> {Number(savings_vs_category).toFixed(0)}% below category average
          </p>
        )}
      </div>

      {/* Rating */}
      {rating && (
        <div className="flex items-center gap-2 mb-3" aria-label={ratingScreenReader}>
          <div className="flex items-center">
            <span className="text-yellow-400" aria-hidden="true">★</span>
            <span className="ml-1 text-sm font-medium text-gray-700" aria-hidden="true">
              {Number(rating).toFixed(1)}
            </span>
          </div>
          {review_count && (
            <span className="text-sm text-gray-500" aria-hidden="true">
              ({review_count.toLocaleString()} reviews)
            </span>
          )}
        </div>
      )}

      {/* Features */}
      <div className="flex flex-wrap gap-2 mb-4">
        {is_prime && (
          <span className="flex items-center text-xs text-blue-600 font-medium" role="status" aria-label="Prime eligible shipping">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
            </svg>
            <span aria-hidden="true">Prime</span>
          </span>
        )}
        {subscribe_save_pct && (
          <span
            className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded"
            role="status"
            aria-label={`Subscribe and save ${Number(subscribe_save_pct).toFixed(0)} percent`}
          >
            <span aria-hidden="true">📦 S&S -{Number(subscribe_save_pct).toFixed(0)}%</span>
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="mt-auto">
        <a
          href={amazon_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-white text-center font-medium rounded-lg transition-colors"
          aria-label={`View ${title} on Amazon (opens in new tab)`}
        >
          View on Amazon
        </a>
      </div>
    </article>
  )
}
