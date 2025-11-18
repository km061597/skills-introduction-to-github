/**
 * API utility functions for communicating with backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

/**
 * Search for products
 */
export async function searchProducts(params) {
  const queryString = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => queryString.append(key, v))
      } else {
        queryString.append(key, value)
      }
    }
  })

  return fetchAPI(`/api/search?${queryString.toString()}`)
}

/**
 * Get product details by ASIN
 */
export async function getProductDetail(asin) {
  return fetchAPI(`/api/product/${asin}`)
}

/**
 * Compare multiple products
 */
export async function compareProducts(asins) {
  return fetchAPI('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ asins }),
  })
}

/**
 * Get all categories
 */
export async function getCategories() {
  return fetchAPI('/api/categories')
}

/**
 * Get all brands (optionally filtered by category)
 */
export async function getBrands(category = null) {
  const query = category ? `?category=${encodeURIComponent(category)}` : ''
  return fetchAPI(`/api/brands${query}`)
}

/**
 * Get category statistics
 */
export async function getCategoryStats(category) {
  return fetchAPI(`/api/category-stats/${encodeURIComponent(category)}`)
}
