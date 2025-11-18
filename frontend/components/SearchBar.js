import { useState, useRef } from 'react'
import { announceToScreenReader } from '../utils/accessibility'

export default function SearchBar({ onSearch, initialValue = '' }) {
  const [query, setQuery] = useState(initialValue)
  const inputRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
      announceToScreenReader(`Searching for ${query.trim()}`, 'assertive')
    } else {
      announceToScreenReader('Please enter a search term', 'assertive')
      inputRef.current?.focus()
    }
  }

  const handleClear = () => {
    setQuery('')
    inputRef.current?.focus()
    announceToScreenReader('Search cleared', 'polite')
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="relative"
      role="search"
      aria-label="Product search"
      id="search"
    >
      <div className="flex items-center">
        <label htmlFor="search-input" className="sr-only">
          Search for products
        </label>
        <input
          ref={inputRef}
          id="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Amazon without sponsored noise..."
          className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-l-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          aria-label="Search for products on Amazon without sponsored content"
          aria-describedby="search-description"
          autoComplete="off"
        />
        <span id="search-description" className="sr-only">
          Enter product name to search for deals and compare prices
        </span>

        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-32 p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            aria-label="Clear search"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        <button
          type="submit"
          className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center gap-2 whitespace-nowrap"
          aria-label="Search for products"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
            focusable="false"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <span>Search</span>
        </button>
      </div>
    </form>
  )
}
