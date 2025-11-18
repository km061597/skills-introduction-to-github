import { useState, useEffect } from 'react'

export default function PriceHistoryChart({ productId, asin }) {
  const [historyData, setHistoryData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [timeRange, setTimeRange] = useState(30) // days

  useEffect(() => {
    if (!productId) return

    fetchPriceHistory()
  }, [productId, timeRange])

  const fetchPriceHistory = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/product/${productId}/price-history?days=${timeRange}`
      )

      if (!response.ok) {
        throw new Error('Failed to fetch price history')
      }

      const data = await response.json()
      setHistoryData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-red-600">
          <p className="font-semibold">Error loading price history</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (!historyData || !historyData.history || historyData.history.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold mb-4">Price History</h3>
        <p className="text-gray-600">No price history data available yet.</p>
      </div>
    )
  }

  const { history, statistics, best_price_time } = historyData

  // Calculate chart dimensions
  const chartHeight = 200
  const chartPadding = 40
  const prices = history.map(h => h.price)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice || 1

  // Generate SVG path for price line
  const generatePath = () => {
    const width = 600
    const points = history.map((point, index) => {
      const x = (index / (history.length - 1)) * (width - chartPadding * 2) + chartPadding
      const y = chartHeight - ((point.price - minPrice) / priceRange * (chartHeight - chartPadding * 2)) - chartPadding
      return `${x},${y}`
    })

    return `M ${points.join(' L ')}`
  }

  // Format price for display
  const formatPrice = (price) => {
    return price != null ? `$${Number(price).toFixed(2)}` : 'N/A'
  }

  // Format date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  // Get trend color and icon
  const getTrendDisplay = () => {
    const trend = statistics.trend
    const change = statistics.price_change_pct

    if (trend === 'down') {
      return {
        color: 'text-green-600',
        bgColor: 'bg-green-100',
        icon: '↓',
        text: `${Math.abs(change).toFixed(1)}% decrease`
      }
    } else if (trend === 'up') {
      return {
        color: 'text-red-600',
        bgColor: 'bg-red-100',
        icon: '↑',
        text: `${Math.abs(change).toFixed(1)}% increase`
      }
    } else {
      return {
        color: 'text-gray-600',
        bgColor: 'bg-gray-100',
        icon: '→',
        text: 'Stable'
      }
    }
  }

  const trendDisplay = getTrendDisplay()

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-gray-900">Price History</h3>

        {/* Time Range Selector */}
        <div className="flex gap-2">
          {[7, 30, 60, 90].map((days) => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-3 py-1 text-sm rounded ${
                timeRange === days
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              aria-label={`Show ${days} days of price history`}
            >
              {days}d
            </button>
          ))}
        </div>
      </div>

      {/* Price Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Current</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatPrice(statistics.current_price)}
          </div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Lowest</div>
          <div className="text-2xl font-bold text-green-600">
            {formatPrice(statistics.min_price)}
          </div>
          {statistics.is_lowest && (
            <span className="text-xs text-green-600 font-semibold">Current is lowest!</span>
          )}
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Average</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatPrice(statistics.avg_price)}
          </div>
        </div>

        <div className={`${trendDisplay.bgColor} rounded-lg p-4`}>
          <div className="text-sm text-gray-600 mb-1">Trend</div>
          <div className={`text-lg font-bold ${trendDisplay.color} flex items-center gap-1`}>
            <span className="text-2xl" aria-hidden="true">{trendDisplay.icon}</span>
            <span className="text-sm">{trendDisplay.text}</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-6">
        <svg
          width="100%"
          height={chartHeight}
          viewBox={`0 0 600 ${chartHeight}`}
          className="w-full"
          role="img"
          aria-label={`Price history chart showing ${history.length} data points`}
        >
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
            const y = chartHeight - (ratio * (chartHeight - chartPadding * 2)) - chartPadding
            const price = minPrice + (ratio * priceRange)

            return (
              <g key={i}>
                <line
                  x1={chartPadding}
                  y1={y}
                  x2={600 - chartPadding}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={chartPadding - 10}
                  y={y + 5}
                  textAnchor="end"
                  fontSize="12"
                  fill="#6b7280"
                >
                  ${price.toFixed(0)}
                </text>
              </g>
            )
          })}

          {/* Price line */}
          <path
            d={generatePath()}
            fill="none"
            stroke="#2563eb"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data points */}
          {history.map((point, index) => {
            const x = (index / (history.length - 1)) * (600 - chartPadding * 2) + chartPadding
            const y = chartHeight - ((point.price - minPrice) / priceRange * (chartHeight - chartPadding * 2)) - chartPadding

            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="4"
                fill={point.price === statistics.min_price ? '#10b981' : point.price === statistics.max_price ? '#ef4444' : '#2563eb'}
                stroke="white"
                strokeWidth="2"
              />
            )
          })}

          {/* Date labels */}
          {history.filter((_, i) => i % Math.ceil(history.length / 5) === 0 || i === history.length - 1).map((point, index, filtered) => {
            const origIndex = history.indexOf(point)
            const x = (origIndex / (history.length - 1)) * (600 - chartPadding * 2) + chartPadding

            return (
              <text
                key={origIndex}
                x={x}
                y={chartHeight - 10}
                textAnchor="middle"
                fontSize="11"
                fill="#6b7280"
              >
                {formatDate(point.date)}
              </text>
            )
          })}
        </svg>
      </div>

      {/* Best Price Recommendation */}
      {best_price_time && best_price_time.best_price && (
        <div className="border-t pt-4">
          <div className="flex items-start gap-3">
            <div className="text-3xl" aria-hidden="true">💡</div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-1">Buying Recommendation</h4>
              <p className="text-sm text-gray-700 mb-2">
                Lowest price was <span className="font-bold text-green-600">{formatPrice(best_price_time.best_price)}</span> about {best_price_time.days_ago} days ago.
                {best_price_time.savings_from_current > 0 && (
                  <span className="text-gray-600">
                    {' '}(${best_price_time.savings_from_current} less than current price)
                  </span>
                )}
              </p>
              <div className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
                best_price_time.recommendation === 'Buy now!'
                  ? 'bg-green-100 text-green-800'
                  : best_price_time.recommendation === 'Wait for better price'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {best_price_time.recommendation}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
