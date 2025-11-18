/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree
 * and displays a fallback UI
 */
import React from 'react'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Log error to error reporting service
    console.error('Error caught by boundary:', error, errorInfo)

    // You can also log to an error reporting service here
    // logErrorToService(error, errorInfo)

    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      return this.props.fallback ? (
        this.props.fallback(this.state.error, this.handleReset)
      ) : (
        <DefaultErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onReset={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}

function DefaultErrorFallback({ error, errorInfo, onReset }) {
  const isDev = process.env.NODE_ENV === 'development'

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full">
        <div className="bg-white shadow-lg rounded-lg p-8">
          {/* Error Icon */}
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-red-100 p-3">
              <svg
                className="h-12 w-12 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
          </div>

          {/* Error Message */}
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
            Oops! Something went wrong
          </h2>

          <p className="text-gray-600 text-center mb-6">
            We're sorry for the inconvenience. The error has been logged and we'll look into it.
          </p>

          {/* Development Error Details */}
          {isDev && error && (
            <div className="mb-6 p-4 bg-gray-100 rounded border border-gray-300 overflow-auto max-h-64">
              <p className="text-sm font-mono text-red-600 mb-2">
                <strong>Error:</strong> {error.toString()}
              </p>
              {errorInfo && (
                <pre className="text-xs font-mono text-gray-700 overflow-auto">
                  {errorInfo.componentStack}
                </pre>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onReset}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
            >
              Go Home
            </button>
          </div>

          {/* Support Link */}
          <p className="text-center text-sm text-gray-500 mt-4">
            Need help?{' '}
            <a href="mailto:support@smartamazon.com" className="text-blue-600 hover:underline">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook for error handling in functional components
 */
export function useErrorHandler() {
  const [error, setError] = React.useState(null)

  React.useEffect(() => {
    if (error) {
      throw error
    }
  }, [error])

  return setError
}

/**
 * Specialized error boundaries for different parts of the app
 */
export function SearchErrorBoundary({ children }) {
  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 my-4">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            Search Error
          </h3>
          <p className="text-red-600 mb-4">
            We couldn't complete your search. Please try again.
          </p>
          <button
            onClick={reset}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
          >
            Retry Search
          </button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  )
}

export function ProductCardErrorBoundary({ children }) {
  return (
    <ErrorBoundary
      fallback={() => (
        <div className="bg-gray-100 border border-gray-300 rounded-lg p-4">
          <p className="text-gray-600 text-sm text-center">
            Error loading product
          </p>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  )
}
