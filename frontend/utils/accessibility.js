/**
 * Accessibility Utilities
 *
 * Helper functions for keyboard navigation, focus management, and ARIA attributes
 */

/**
 * Trap focus within a container (for modals, dialogs)
 */
export function trapFocus(container) {
  const focusableElements = container.querySelectorAll(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )

  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  const handleTabKey = (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          lastElement.focus()
          e.preventDefault()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          firstElement.focus()
          e.preventDefault()
        }
      }
    }

    // Escape key closes modal
    if (e.key === 'Escape') {
      container.dispatchEvent(new CustomEvent('escape-pressed'))
    }
  }

  container.addEventListener('keydown', handleTabKey)

  return () => {
    container.removeEventListener('keydown', handleTabKey)
  }
}

/**
 * Announce message to screen readers
 */
export function announceToScreenReader(message, priority = 'polite') {
  const announcement = document.createElement('div')
  announcement.setAttribute('role', 'status')
  announcement.setAttribute('aria-live', priority)
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message

  document.body.appendChild(announcement)

  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Focus the first error in a form
 */
export function focusFirstError(formElement) {
  const firstError = formElement.querySelector('[aria-invalid="true"]')
  if (firstError) {
    firstError.focus()
    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

/**
 * Generate unique ID for ARIA relationships
 */
let idCounter = 0
export function generateId(prefix = 'a11y') {
  return `${prefix}-${++idCounter}-${Date.now()}`
}

/**
 * Keyboard navigation handler for grid/list items
 */
export function handleGridKeyNavigation(e, currentIndex, totalItems, onNavigate) {
  const itemsPerRow = Math.floor(window.innerWidth / 300) // Approximate items per row

  switch (e.key) {
    case 'ArrowRight':
      e.preventDefault()
      if (currentIndex < totalItems - 1) {
        onNavigate(currentIndex + 1)
      }
      break
    case 'ArrowLeft':
      e.preventDefault()
      if (currentIndex > 0) {
        onNavigate(currentIndex - 1)
      }
      break
    case 'ArrowDown':
      e.preventDefault()
      if (currentIndex + itemsPerRow < totalItems) {
        onNavigate(currentIndex + itemsPerRow)
      }
      break
    case 'ArrowUp':
      e.preventDefault()
      if (currentIndex - itemsPerRow >= 0) {
        onNavigate(currentIndex - itemsPerRow)
      }
      break
    case 'Home':
      e.preventDefault()
      onNavigate(0)
      break
    case 'End':
      e.preventDefault()
      onNavigate(totalItems - 1)
      break
  }
}

/**
 * Format price for screen readers
 */
export function formatPriceForScreenReader(price) {
  if (!price) return 'Price not available'
  const numPrice = Number(price)
  const dollars = Math.floor(numPrice)
  const cents = Math.round((numPrice - dollars) * 100)

  if (cents === 0) {
    return `${dollars} dollars`
  }
  return `${dollars} dollars and ${cents} cents`
}

/**
 * Format rating for screen readers
 */
export function formatRatingForScreenReader(rating, reviewCount) {
  if (!rating) return 'No rating available'
  return `Rated ${rating} out of 5 stars, based on ${reviewCount || 0} reviews`
}

/**
 * Check if element is visible
 */
export function isElementVisible(element) {
  return !!(
    element.offsetWidth ||
    element.offsetHeight ||
    element.getClientRects().length
  )
}

/**
 * Restore focus to previous element
 */
let focusStack = []

export function saveFocus() {
  focusStack.push(document.activeElement)
}

export function restoreFocus() {
  const element = focusStack.pop()
  if (element && isElementVisible(element)) {
    element.focus()
  }
}
