import { useState, useEffect } from 'react'

export default function FilterSidebar({ filters, onFilterChange }) {
  const [localFilters, setLocalFilters] = useState(filters)

  useEffect(() => {
    setLocalFilters(filters)
  }, [filters])

  const handleChange = (key, value) => {
    const newFilters = { ...localFilters, [key]: value }
    setLocalFilters(newFilters)
  }

  const applyFilters = () => {
    onFilterChange(localFilters)
  }

  const clearFilters = () => {
    const resetFilters = {
      minPrice: null,
      maxPrice: null,
      minRating: null,
      primeOnly: false,
      hideSponsored: true,
      minDiscount: null,
      brands: [],
      excludeBrands: []
    }
    setLocalFilters(resetFilters)
    onFilterChange(resetFilters)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">Filters</h2>
        <button
          onClick={clearFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Clear All
        </button>
      </div>

      <div className="space-y-6">
        {/* Price Filter */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            💰 Price
          </h3>
          <div className="space-y-2">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Min Price</label>
              <input
                type="number"
                value={localFilters.minPrice || ''}
                onChange={(e) => handleChange('minPrice', e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="$0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Max Price</label>
              <input
                type="number"
                value={localFilters.maxPrice || ''}
                onChange={(e) => handleChange('maxPrice', e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="$500"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Discount Filter */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            📉 Discount
          </h3>
          <div className="space-y-2">
            {[
              { value: null, label: 'Any' },
              { value: 20, label: '20% or more' },
              { value: 50, label: '50% or more' },
              { value: 75, label: '75% or more' }
            ].map((option) => (
              <label key={option.label} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="discount"
                  checked={localFilters.minDiscount === option.value}
                  onChange={() => handleChange('minDiscount', option.value)}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Rating Filter */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            ⭐ Rating
          </h3>
          <div className="space-y-2">
            {[
              { value: null, label: 'Any' },
              { value: 3.0, label: '3+ Stars' },
              { value: 4.0, label: '4+ Stars' },
              { value: 4.5, label: '4.5+ Stars' }
            ].map((option) => (
              <label key={option.label} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="rating"
                  checked={localFilters.minRating === option.value}
                  onChange={() => handleChange('minRating', option.value)}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Prime Filter */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            📦 Shipping
          </h3>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.primeOnly}
              onChange={(e) => handleChange('primeOnly', e.target.checked)}
              className="text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700">Prime eligible only</span>
          </label>
        </div>

        {/* Sponsored Filter */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            🔍 Advanced
          </h3>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={localFilters.hideSponsored}
              onChange={(e) => handleChange('hideSponsored', e.target.checked)}
              className="text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700">Hide sponsored ads</span>
          </label>
        </div>

        {/* Apply Button */}
        <button
          onClick={applyFilters}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
        >
          Apply Filters
        </button>
      </div>
    </div>
  )
}
