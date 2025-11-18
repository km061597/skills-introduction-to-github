import { useState, useEffect } from 'react'
import { announceToScreenReader } from '../utils/accessibility'

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
    const activeFiltersCount = Object.values(localFilters).filter(v => v !== null && v !== false && (!Array.isArray(v) || v.length > 0)).length
    announceToScreenReader(`Filters applied. ${activeFiltersCount} active filters`, 'assertive')
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
    announceToScreenReader('All filters cleared', 'polite')
  }

  return (
    <aside
      className="bg-white rounded-lg shadow-md p-4"
      id="filters"
      aria-label="Product filters"
      role="complementary"
    >
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
        <fieldset>
          <legend className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span aria-hidden="true">💰</span> Price
          </legend>
          <div className="space-y-2">
            <div>
              <label htmlFor="filter-min-price" className="block text-sm text-gray-600 mb-1">
                Minimum Price
              </label>
              <input
                id="filter-min-price"
                type="number"
                min="0"
                step="0.01"
                value={localFilters.minPrice || ''}
                onChange={(e) => handleChange('minPrice', e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="$0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Minimum price filter"
              />
            </div>
            <div>
              <label htmlFor="filter-max-price" className="block text-sm text-gray-600 mb-1">
                Maximum Price
              </label>
              <input
                id="filter-max-price"
                type="number"
                min="0"
                step="0.01"
                value={localFilters.maxPrice || ''}
                onChange={(e) => handleChange('maxPrice', e.target.value ? parseFloat(e.target.value) : null)}
                placeholder="$500"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Maximum price filter"
              />
            </div>
          </div>
        </fieldset>

        {/* Discount Filter */}
        <fieldset>
          <legend className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span aria-hidden="true">📉</span> Discount
          </legend>
          <div className="space-y-2" role="radiogroup" aria-label="Minimum discount filter">
            {[
              { value: null, label: 'Any discount' },
              { value: 20, label: '20% or more off' },
              { value: 50, label: '50% or more off' },
              { value: 75, label: '75% or more off' }
            ].map((option, index) => (
              <label key={option.label} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="discount"
                  checked={localFilters.minDiscount === option.value}
                  onChange={() => handleChange('minDiscount', option.value)}
                  className="text-blue-600 focus:ring-2 focus:ring-blue-500"
                  aria-label={option.label}
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Rating Filter */}
        <fieldset>
          <legend className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span aria-hidden="true">⭐</span> Rating
          </legend>
          <div className="space-y-2" role="radiogroup" aria-label="Minimum rating filter">
            {[
              { value: null, label: 'Any rating' },
              { value: 3.0, label: '3 stars or higher' },
              { value: 4.0, label: '4 stars or higher' },
              { value: 4.5, label: '4.5 stars or higher' }
            ].map((option) => (
              <label key={option.label} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="rating"
                  checked={localFilters.minRating === option.value}
                  onChange={() => handleChange('minRating', option.value)}
                  className="text-blue-600 focus:ring-2 focus:ring-blue-500"
                  aria-label={option.label}
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Prime Filter */}
        <fieldset>
          <legend className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span aria-hidden="true">📦</span> Shipping
          </legend>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              id="filter-prime-only"
              type="checkbox"
              checked={localFilters.primeOnly}
              onChange={(e) => handleChange('primeOnly', e.target.checked)}
              className="text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              aria-label="Show only Prime eligible products"
            />
            <span className="text-sm text-gray-700">Prime eligible only</span>
          </label>
        </fieldset>

        {/* Sponsored Filter */}
        <fieldset>
          <legend className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span aria-hidden="true">🔍</span> Advanced
          </legend>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              id="filter-hide-sponsored"
              type="checkbox"
              checked={localFilters.hideSponsored}
              onChange={(e) => handleChange('hideSponsored', e.target.checked)}
              className="text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              aria-label="Hide sponsored advertisements"
            />
            <span className="text-sm text-gray-700">Hide sponsored ads</span>
          </label>
        </fieldset>

        {/* Apply Button */}
        <button
          onClick={applyFilters}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-white font-semibold rounded-lg transition-colors"
          aria-label="Apply all selected filters to search results"
        >
          Apply Filters
        </button>
      </div>
    </aside>
  )
}
