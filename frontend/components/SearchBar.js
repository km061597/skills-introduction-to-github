import { useState } from 'react'

export default function SearchBar({ onSearch, initialValue = '' }) {
  const [query, setQuery] = useState(initialValue)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Amazon without sponsored noise..."
          className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-l-lg focus:outline-none focus:border-blue-500 transition-colors"
        />
        <button
          type="submit"
          className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-r-lg hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          Search
        </button>
      </div>
    </form>
  )
}
