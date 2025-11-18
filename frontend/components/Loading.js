/**
 * Loading States Component Library
 *
 * Provides various loading states for better UX
 */

export function LoadingSpinner({ size = 'md', color = 'blue' }) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  }

  const colors = {
    blue: 'border-blue-600',
    white: 'border-white',
    gray: 'border-gray-600'
  }

  return (
    <div className={`animate-spin rounded-full border-b-2 ${sizes[size]} ${colors[color]}`} />
  )
}

export function LoadingSkeleton({ className = '', width = 'w-full', height = 'h-4' }) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${width} ${height} ${className}`} />
  )
}

export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 space-y-4 animate-pulse">
      {/* Image placeholder */}
      <div className="w-full h-48 bg-gray-200 rounded" />

      {/* Title placeholder */}
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        <div className="h-4 bg-gray-200 rounded w-1/2" />
      </div>

      {/* Price placeholder */}
      <div className="space-y-2">
        <div className="h-8 bg-gray-200 rounded w-1/3" />
        <div className="h-6 bg-gray-200 rounded w-1/2" />
      </div>

      {/* Rating placeholder */}
      <div className="h-4 bg-gray-200 rounded w-2/3" />

      {/* Button placeholder */}
      <div className="h-10 bg-gray-200 rounded" />
    </div>
  )
}

export function FullPageLoader({ message = 'Loading...' }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="xl" />
        <p className="mt-4 text-gray-600 text-lg">{message}</p>
      </div>
    </div>
  )
}

export function InlineLoader({ message }) {
  return (
    <div className="flex items-center justify-center py-8">
      <LoadingSpinner size="md" />
      {message && <span className="ml-3 text-gray-600">{message}</span>}
    </div>
  )
}

export function TableRowSkeleton({ columns = 4 }) {
  return (
    <tr className="animate-pulse">
      {[...Array(columns)].map((_, i) => (
        <td key={i} className="p-4">
          <div className="h-4 bg-gray-200 rounded" />
        </td>
      ))}
    </tr>
  )
}

export function GridSkeleton({ count = 12 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[...Array(count)].map((_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
    </div>
  )
}
