import { useState, useEffect } from 'react'

export default function SubscribeSaveCalculator({ product }) {
  const [frequency, setFrequency] = useState('monthly')
  const [subscriptions, setSubscriptions] = useState(1)
  const [calculations, setCalculations] = useState(null)

  const frequencies = [
    { value: 'biweekly', label: 'Every 2 Weeks', perYear: 26 },
    { value: 'monthly', label: 'Monthly', perYear: 12 },
    { value: 'bimonthly', label: 'Every 2 Months', perYear: 6 },
    { value: 'quarterly', label: 'Every 3 Months', perYear: 4 },
  ]

  useEffect(() => {
    calculateSavings()
  }, [frequency, subscriptions, product])

  const calculateSavings = () => {
    if (!product || !product.current_price) {
      setCalculations(null)
      return
    }

    const basePrice = Number(product.current_price)
    const subscribeSavePct = product.subscribe_save_pct ? Number(product.subscribe_save_pct) : 5 // Default 5%
    const selectedFreq = frequencies.find(f => f.value === frequency)

    // Calculate prices
    const oneTimePurchasePrice = basePrice
    const subscribePrice = basePrice * (1 - subscribeSavePct / 100)
    const savingsPerOrder = oneTimePurchasePrice - subscribePrice

    // Calculate yearly costs
    const ordersPerYear = selectedFreq.perYear * subscriptions
    const yearlyOneTimeCost = oneTimePurchasePrice * ordersPerYear
    const yearlySubscribeCost = subscribePrice * ordersPerYear
    const yearlySavings = yearlyOneTimeCost - yearlySubscribeCost

    // Calculate 5-year savings
    const fiveYearSavings = yearlySavings * 5

    // Additional Amazon benefits simulation
    const estimatedShippingSavings = ordersPerYear * 5.99 // Assume $5.99 shipping per order if not Prime
    const totalYearlySavings = yearlySavings + (product.is_prime ? 0 : estimatedShippingSavings)

    setCalculations({
      basePrice,
      subscribeSavePct,
      oneTimePurchasePrice,
      subscribePrice,
      savingsPerOrder,
      ordersPerYear,
      yearlyOneTimeCost,
      yearlySubscribeCost,
      yearlySavings,
      fiveYearSavings,
      estimatedShippingSavings: product.is_prime ? 0 : estimatedShippingSavings,
      totalYearlySavings,
      recommendSubscribe: yearlySavings > 20 // Recommend if saving more than $20/year
    })
  }

  if (!product) {
    return null
  }

  if (!calculations) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const formatPrice = (price) => {
    return `$${Number(price).toFixed(2)}`
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="text-3xl" aria-hidden="true">📦</div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Subscribe & Save Calculator</h3>
          <p className="text-sm text-gray-600">Calculate your savings with auto-delivery</p>
        </div>
      </div>

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label htmlFor="frequency" className="block text-sm font-medium text-gray-700 mb-2">
            Delivery Frequency
          </label>
          <select
            id="frequency"
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {frequencies.map(freq => (
              <option key={freq.value} value={freq.value}>
                {freq.label} ({freq.perYear} times/year)
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="subscriptions" className="block text-sm font-medium text-gray-700 mb-2">
            Number of Subscriptions
          </label>
          <input
            id="subscriptions"
            type="number"
            min="1"
            max="10"
            value={subscriptions}
            onChange={(e) => setSubscriptions(Math.max(1, Math.min(10, parseInt(e.target.value) || 1)))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Stack up to 10 items for maximum discount</p>
        </div>
      </div>

      {/* Price Comparison */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-100 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">One-Time Purchase</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatPrice(calculations.oneTimePurchasePrice)}
          </div>
          <div className="text-xs text-gray-500 mt-1">per order</div>
        </div>

        <div className="bg-orange-100 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Subscribe & Save</div>
          <div className="text-2xl font-bold text-orange-600">
            {formatPrice(calculations.subscribePrice)}
          </div>
          <div className="text-xs text-orange-700 font-semibold mt-1">
            Save {formatPrice(calculations.savingsPerOrder)} per order
          </div>
        </div>
      </div>

      {/* Yearly Savings */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-2">Your Yearly Savings</div>
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {formatPrice(calculations.yearlySavings)}
          </div>
          <div className="text-sm text-gray-700">
            Based on {calculations.ordersPerYear} orders per year
            {subscriptions > 1 && ` (${subscriptions} items per order)`}
          </div>
          {calculations.estimatedShippingSavings > 0 && (
            <div className="mt-3 text-sm text-gray-600">
              + {formatPrice(calculations.estimatedShippingSavings)} estimated shipping savings
              <div className="text-xs text-gray-500">(Consider Amazon Prime for free shipping)</div>
            </div>
          )}
        </div>
      </div>

      {/* 5-Year Projection */}
      <div className="border-t pt-4 mb-6">
        <h4 className="font-semibold text-gray-900 mb-3">Long-Term Savings Projection</h4>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-600 mb-1">1 Year</div>
            <div className="text-lg font-bold text-green-600">
              {formatPrice(calculations.yearlySavings)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 mb-1">3 Years</div>
            <div className="text-lg font-bold text-green-600">
              {formatPrice(calculations.yearlySavings * 3)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 mb-1">5 Years</div>
            <div className="text-lg font-bold text-green-600">
              {formatPrice(calculations.fiveYearSavings)}
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div className={`rounded-lg p-4 ${
        calculations.recommendSubscribe
          ? 'bg-green-100 border border-green-300'
          : 'bg-yellow-100 border border-yellow-300'
      }`}>
        <div className="flex items-start gap-3">
          <div className="text-2xl" aria-hidden="true">
            {calculations.recommendSubscribe ? '✅' : 'ℹ️'}
          </div>
          <div>
            <h4 className={`font-semibold mb-1 ${
              calculations.recommendSubscribe ? 'text-green-900' : 'text-yellow-900'
            }`}>
              {calculations.recommendSubscribe ? 'Highly Recommended!' : 'Consider Your Usage'}
            </h4>
            <p className={`text-sm ${
              calculations.recommendSubscribe ? 'text-green-800' : 'text-yellow-800'
            }`}>
              {calculations.recommendSubscribe ? (
                <>
                  You'll save <strong>{formatPrice(calculations.yearlySavings)}</strong> per year with Subscribe & Save.
                  That's {formatPrice(calculations.fiveYearSavings)} over 5 years!
                </>
              ) : (
                <>
                  Subscribe & Save will save you money, but the savings are modest.
                  Consider if the convenience is worth it for your usage frequency.
                </>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Additional Benefits */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">📋 Additional Benefits</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Never run out - automatic delivery</li>
          <li>✓ Free delivery on orders over $35 (or with Prime)</li>
          <li>✓ Skip or cancel anytime - no commitment</li>
          <li>✓ 5% discount (up to 15% with 5+ subscriptions)</li>
          <li>✓ Flexible delivery schedule</li>
        </ul>
      </div>

      {/* Action Button */}
      <div className="mt-6">
        <a
          href={product.amazon_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full py-3 bg-orange-500 hover:bg-orange-600 text-white text-center font-bold rounded-lg transition-colors"
        >
          Set Up Subscribe & Save on Amazon →
        </a>
      </div>
    </div>
  )
}
