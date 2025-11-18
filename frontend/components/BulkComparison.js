import { useState } from 'react'

export default function BulkComparison() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [asins, setAsins] = useState('')

  const handleCompare = async () => {
    const asinList = asins.split(/[,\s]+/).filter(a => a.trim())

    if (asinList.length < 2) {
      setError('Please enter at least 2 ASINs to compare')
      return
    }

    if (asinList.length > 10) {
      setError('Maximum 10 products can be compared at once')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/compare`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ asins: asinList }),
        }
      )

      if (!response.ok) {
        throw new Error('Failed to compare products')
      }

      const data = await response.json()
      setProducts(data.products)
    } catch (err) {
      setError(err.message)
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  const handleAddToCompare = (asin) => {
    const currentAsins = asins.split(/[,\s]+/).filter(a => a.trim())
    if (!currentAsins.includes(asin)) {
      setAsins(prev => prev ? `${prev}, ${asin}` : asin)
    }
  }

  const handleRemoveProduct = (index) => {
    setProducts(prev => prev.filter((_, i) => i !== index))
  }

  const getBestValueIndicator = (product, allProducts, metric) => {
    if (!allProducts.length) return false

    const values = allProducts
      .map(p => {
        const val = Number(p[metric])
        return isNaN(val) ? null : val
      })
      .filter(v => v !== null)

    if (!values.length) return false

    const productValue = Number(product[metric])
    if (isNaN(productValue)) return false

    // For unit_price, lower is better
    if (metric === 'unit_price') {
      return productValue === Math.min(...values)
    }

    // For rating, higher is better
    if (metric === 'rating') {
      return productValue === Math.max(...values)
    }

    // For current_price, lower is better
    return productValue === Math.min(...values)
  }

  const formatPrice = (price) => {
    return price != null ? `$${Number(price).toFixed(2)}` : 'N/A'
  }

  const formatUnitPrice = (unitPrice, unitType) => {
    if (!unitPrice) return 'N/A'
    return `$${Number(unitPrice).toFixed(4)}/${unitType || 'unit'}`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Bulk Product Comparison
        </h2>
        <p className="text-gray-600 mb-6">
          Compare up to 10 products side-by-side. Enter ASINs (Amazon Standard Identification Numbers) separated by commas.
        </p>

        {/* Input Section */}
        <div className="flex gap-4">
          <input
            type="text"
            value={asins}
            onChange={(e) => setAsins(e.target.value)}
            placeholder="e.g., B000001, B000002, B000003"
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            aria-label="Enter ASINs to compare"
          />
          <button
            onClick={handleCompare}
            disabled={loading}
            className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Loading...' : 'Compare'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Quick Tips */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">💡 How to find ASINs:</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>On Amazon product pages, look in the URL (e.g., /dp/<strong>B000001</strong>/)</li>
            <li>Scroll to "Product Information" section on any Amazon listing</li>
            <li>ASINs are always 10 characters (letters and numbers)</li>
          </ul>
        </div>
      </div>

      {/* Comparison Table */}
      {products.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 sticky left-0 bg-gray-50 z-10">
                    Attribute
                  </th>
                  {products.map((product, index) => (
                    <th key={product.asin} className="px-6 py-4 text-left min-w-[250px]">
                      <div className="flex justify-between items-start">
                        <span className="text-sm font-semibold text-gray-900">Product {index + 1}</span>
                        <button
                          onClick={() => handleRemoveProduct(index)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          aria-label={`Remove ${product.title} from comparison`}
                        >
                          ✕
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {/* Product Image */}
                <tr>
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-white">
                    Image
                  </td>
                  {products.map(product => (
                    <td key={product.asin} className="px-6 py-4">
                      <img
                        src={product.image_url || '/placeholder.png'}
                        alt={product.title}
                        className="w-32 h-32 object-contain mx-auto"
                      />
                    </td>
                  ))}
                </tr>

                {/* Product Title */}
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-gray-50">
                    Product
                  </td>
                  {products.map(product => (
                    <td key={product.asin} className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900 line-clamp-3">
                        {product.title}
                      </p>
                      {product.brand && (
                        <p className="text-xs text-gray-500 mt-1">{product.brand}</p>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Current Price */}
                <tr>
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-white">
                    Price
                  </td>
                  {products.map(product => {
                    const isBest = getBestValueIndicator(product, products, 'current_price')
                    return (
                      <td key={product.asin} className="px-6 py-4">
                        <div className={`text-2xl font-bold ${isBest ? 'text-green-600' : 'text-gray-900'}`}>
                          {formatPrice(product.current_price)}
                          {isBest && <span className="ml-2 text-xs">👑 Best</span>}
                        </div>
                        {product.list_price && Number(product.list_price) > Number(product.current_price) && (
                          <div className="text-sm text-gray-500 line-through">
                            {formatPrice(product.list_price)}
                          </div>
                        )}
                      </td>
                    )
                  })}
                </tr>

                {/* Unit Price */}
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-gray-50">
                    Unit Price
                  </td>
                  {products.map(product => {
                    const isBest = getBestValueIndicator(product, products, 'unit_price')
                    return (
                      <td key={product.asin} className="px-6 py-4">
                        <div className={`text-lg font-bold ${isBest ? 'text-green-600' : 'text-blue-600'}`}>
                          {formatUnitPrice(product.unit_price, product.unit_type)}
                          {isBest && <span className="ml-2 text-xs">👑 Best Value</span>}
                        </div>
                      </td>
                    )
                  })}
                </tr>

                {/* Rating */}
                <tr>
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-white">
                    Rating
                  </td>
                  {products.map(product => {
                    const isBest = getBestValueIndicator(product, products, 'rating')
                    return (
                      <td key={product.asin} className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${isBest ? 'text-yellow-600' : 'text-gray-900'}`}>
                            ★ {product.rating ? Number(product.rating).toFixed(1) : 'N/A'}
                            {isBest && <span className="ml-2 text-xs">👑 Top Rated</span>}
                          </span>
                        </div>
                        {product.review_count && (
                          <p className="text-sm text-gray-500">
                            {product.review_count.toLocaleString()} reviews
                          </p>
                        )}
                      </td>
                    )
                  })}
                </tr>

                {/* Discount */}
                <tr className="bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-gray-50">
                    Discount
                  </td>
                  {products.map(product => (
                    <td key={product.asin} className="px-6 py-4">
                      {product.discount_pct && Number(product.discount_pct) > 0 ? (
                        <span className="px-3 py-1 bg-red-100 text-red-800 rounded font-semibold">
                          -{Number(product.discount_pct).toFixed(0)}% OFF
                        </span>
                      ) : (
                        <span className="text-gray-500">None</span>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Prime */}
                <tr>
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-white">
                    Prime Eligible
                  </td>
                  {products.map(product => (
                    <td key={product.asin} className="px-6 py-4">
                      {product.is_prime ? (
                        <span className="text-blue-600 font-semibold">✓ Yes</span>
                      ) : (
                        <span className="text-gray-500">✗ No</span>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Subscribe & Save */}
                {products.some(p => p.subscribe_save_pct) && (
                  <tr className="bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-gray-50">
                      Subscribe & Save
                    </td>
                    {products.map(product => (
                      <td key={product.asin} className="px-6 py-4">
                        {product.subscribe_save_pct ? (
                          <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded font-semibold">
                            -{Number(product.subscribe_save_pct).toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-gray-500">Not available</span>
                        )}
                      </td>
                    ))}
                  </tr>
                )}

                {/* View on Amazon */}
                <tr>
                  <td className="px-6 py-4 font-medium text-gray-900 sticky left-0 bg-white">
                    Actions
                  </td>
                  {products.map(product => (
                    <td key={product.asin} className="px-6 py-4">
                      <a
                        href={product.amazon_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white text-center font-medium rounded-lg transition-colors"
                      >
                        View on Amazon
                      </a>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* Winner Summary */}
          <div className="border-t p-6 bg-gray-50">
            <h3 className="font-bold text-lg mb-4">🏆 Comparison Winner</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-100 rounded-lg p-4">
                <div className="text-sm text-gray-700 mb-1">Best Price</div>
                <div className="font-bold text-green-800">
                  {(() => {
                    const best = products.reduce((min, p) =>
                      (!min || (p.current_price && Number(p.current_price) < Number(min.current_price))) ? p : min
                    , null)
                    return best ? best.title.substring(0, 50) + '...' : 'N/A'
                  })()}
                </div>
              </div>
              <div className="bg-blue-100 rounded-lg p-4">
                <div className="text-sm text-gray-700 mb-1">Best Unit Price</div>
                <div className="font-bold text-blue-800">
                  {(() => {
                    const best = products.reduce((min, p) =>
                      (!min || (p.unit_price && Number(p.unit_price) < Number(min.unit_price))) ? p : min
                    , null)
                    return best ? best.title.substring(0, 50) + '...' : 'N/A'
                  })()}
                </div>
              </div>
              <div className="bg-yellow-100 rounded-lg p-4">
                <div className="text-sm text-gray-700 mb-1">Highest Rated</div>
                <div className="font-bold text-yellow-800">
                  {(() => {
                    const best = products.reduce((max, p) =>
                      (!max || (p.rating && Number(p.rating) > Number(max.rating))) ? p : max
                    , null)
                    return best ? best.title.substring(0, 50) + '...' : 'N/A'
                  })()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
