import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import Header from '../components/Header'
import SearchBar from '../components/SearchBar'
import FilterSidebar from '../components/FilterSidebar'
import ProductGrid from '../components/ProductGrid'
import SortDropdown from '../components/SortDropdown'
import { searchProducts } from '../utils/api'

export default function SearchPage() {
  const router = useRouter()
  const { q, sort = 'unit_price_asc' } = router.query

  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [totalResults, setTotalResults] = useState(0)
  const [sponsoredHidden, setSponsoredHidden] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  // Filters state
  const [filters, setFilters] = useState({
    minPrice: null,
    maxPrice: null,
    minRating: null,
    primeOnly: false,
    hideSponsored: true,
    minDiscount: null,
    brands: [],
    excludeBrands: []
  })

  // Fetch products when query or filters change
  useEffect(() => {
    if (q) {
      fetchProducts()
    }
  }, [q, sort, filters, currentPage])

  const fetchProducts = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = {
        q,
        sort,
        page: currentPage,
        limit: 48,
        ...filters
      }

      const data = await searchProducts(params)

      setProducts(data.results)
      setTotalResults(data.total)
      setTotalPages(data.pages)
      setSponsoredHidden(data.sponsored_hidden)
    } catch (err) {
      setError(err.message || 'Failed to fetch products')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (newQuery) => {
    router.push(`/search?q=${encodeURIComponent(newQuery)}&sort=${sort}`)
    setCurrentPage(1)
  }

  const handleSortChange = (newSort) => {
    router.push(`/search?q=${encodeURIComponent(q)}&sort=${newSort}`)
    setCurrentPage(1)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setCurrentPage(1)
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <>
      <Head>
        <title>{q ? `${q} - SmartDeal` : 'Search - SmartDeal'}</title>
        <meta name="description" content={`Find the best deals on ${q} with true unit price comparison`} />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <Header />

        {/* Search Bar */}
        <div className="bg-white shadow-sm border-b sticky top-0 z-10">
          <div className="container mx-auto px-4 py-4">
            <SearchBar onSearch={handleSearch} initialValue={q} />
          </div>
        </div>

        <div className="container mx-auto px-4 py-6">
          <div className="flex gap-6">
            {/* Filters Sidebar */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <div className="sticky top-24">
                <FilterSidebar
                  filters={filters}
                  onFilterChange={handleFilterChange}
                />
              </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 min-w-0">
              {/* Results Header */}
              <div className="mb-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                      Search Results for "{q}"
                    </h1>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>
                        Showing {products.length} of {totalResults} results
                      </span>
                      {sponsoredHidden > 0 && (
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">
                          🚫 {sponsoredHidden} sponsored ads hidden
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Sort Dropdown */}
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-gray-700">
                      Sort by:
                    </label>
                    <SortDropdown
                      value={sort}
                      onChange={handleSortChange}
                    />
                  </div>
                </div>
              </div>

              {/* Error State */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <p className="text-red-800">
                    <strong>Error:</strong> {error}
                  </p>
                </div>
              )}

              {/* Loading State */}
              {loading && (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  <p className="mt-4 text-gray-600">Loading products...</p>
                </div>
              )}

              {/* Product Grid */}
              {!loading && products.length > 0 && (
                <>
                  <ProductGrid products={products} />

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="mt-8 flex justify-center">
                      <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={handlePageChange}
                      />
                    </div>
                  )}
                </>
              )}

              {/* No Results */}
              {!loading && products.length === 0 && q && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔍</div>
                  <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                    No products found
                  </h2>
                  <p className="text-gray-600 mb-6">
                    Try adjusting your search or filters
                  </p>
                  <button
                    onClick={() => {
                      setFilters({
                        minPrice: null,
                        maxPrice: null,
                        minRating: null,
                        primeOnly: false,
                        hideSponsored: true,
                        minDiscount: null,
                        brands: [],
                        excludeBrands: []
                      })
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Clear Filters
                  </button>
                </div>
              )}
            </main>
          </div>
        </div>
      </div>
    </>
  )
}

function Pagination({ currentPage, totalPages, onPageChange }) {
  const pages = []
  const maxVisible = 7

  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages, startPage + maxVisible - 1)

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Previous
      </button>

      {startPage > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            className="px-3 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
          >
            1
          </button>
          {startPage > 2 && <span className="px-2">...</span>}
        </>
      )}

      {pages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-3 py-2 rounded-lg border ${
            page === currentPage
              ? 'bg-blue-600 text-white border-blue-600'
              : 'border-gray-300 hover:bg-gray-50'
          }`}
        >
          {page}
        </button>
      ))}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="px-2">...</span>}
          <button
            onClick={() => onPageChange(totalPages)}
            className="px-3 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
          >
            {totalPages}
          </button>
        </>
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Next
      </button>
    </div>
  )
}
