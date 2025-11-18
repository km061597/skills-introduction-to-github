export default function SortDropdown({ value, onChange }) {
  const sortOptions = [
    { value: 'unit_price_asc', label: '💎 Best Unit Price' },
    { value: 'discount_desc', label: '📉 Highest Discount' },
    { value: 'rating_desc', label: '⭐ Highest Rated' },
    { value: 'review_count_desc', label: '📊 Most Reviews' },
    { value: 'price_asc', label: '💰 Price: Low to High' },
    { value: 'price_desc', label: '💰 Price: High to Low' },
    { value: 'hidden_gem_desc', label: '🏆 Hidden Gems' },
  ]

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
    >
      {sortOptions.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
}
