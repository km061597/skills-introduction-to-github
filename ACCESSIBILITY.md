# Accessibility Features

SmartAmazon Search Platform is built with accessibility as a core principle, following WCAG 2.1 Level AA guidelines.

## Table of Contents

- [Keyboard Navigation](#keyboard-navigation)
- [Screen Reader Support](#screen-reader-support)
- [Visual Accessibility](#visual-accessibility)
- [ARIA Attributes](#aria-attributes)
- [Focus Management](#focus-management)
- [Accessibility Testing](#accessibility-testing)

## Keyboard Navigation

### Skip Links

Press `Tab` on any page to reveal skip links that allow quick navigation to:
- Main content
- Search bar
- Filters
- Results

### Navigation Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Move forward through interactive elements |
| `Shift + Tab` | Move backward through interactive elements |
| `Enter` / `Space` | Activate buttons and links |
| `Esc` | Close modals and dialogs |
| `Arrow Keys` | Navigate through product grid |
| `Home` | Jump to first product |
| `End` | Jump to last product |

### Focus Indicators

All interactive elements have visible focus indicators:
- **Blue ring** (2px solid #0066cc) with 2px offset
- Works for keyboard users while hiding from mouse users
- High contrast support in high contrast mode

## Screen Reader Support

### Semantic HTML

- Proper heading hierarchy (`h1` → `h2` → `h3`)
- Semantic HTML5 elements (`<article>`, `<aside>`, `<nav>`, `<main>`)
- Form labels properly associated with inputs
- Lists use proper `<ul>`, `<ol>` structures

### ARIA Labels

All interactive elements have descriptive labels:

```jsx
// Search input
<input aria-label="Search for products on Amazon without sponsored content" />

// Product card
<article aria-label="Optimum Nutrition Whey Protein - Sponsored">

// Filter button
<button aria-label="Apply all selected filters to search results">
```

### ARIA Live Regions

Dynamic content changes are announced:

```jsx
// Search initiated
announceToScreenReader("Searching for protein powder", "assertive")

// Filters applied
announceToScreenReader("Filters applied. 3 active filters", "assertive")

// Results loaded
<div role="status" aria-live="polite">
  Found 24 products
</div>
```

### Price & Rating Formatting

Prices and ratings are formatted for natural screen reader pronunciation:

```jsx
// $54.99 → "54 dollars and 99 cents"
formatPriceForScreenReader(54.99)

// 4.7 stars (5,000 reviews) → "Rated 4.7 out of 5 stars, based on 5,000 reviews"
formatRatingForScreenReader(4.7, 5000)
```

## Visual Accessibility

### Color Contrast

All text meets WCAG AA standards:
- Normal text: minimum 4.5:1 contrast ratio
- Large text: minimum 3:1 contrast ratio
- Interactive elements: minimum 3:1 contrast ratio

### High Contrast Mode

Supports `prefers-contrast: high` media query:

```css
@media (prefers-contrast: high) {
  :root {
    --foreground-rgb: 0, 0, 0;
    --background-start-rgb: 255, 255, 255;
  }
}
```

### Reduced Motion

Respects `prefers-reduced-motion` preference:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Dark Mode

Supports `prefers-color-scheme: dark`:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 18, 18, 18;
  }
}
```

### Text Scaling

- All font sizes use relative units (rem, em)
- Layout responsive up to 200% zoom
- No horizontal scrolling at 200% zoom

## ARIA Attributes

### Landmarks

```html
<!-- Main search area -->
<form role="search" aria-label="Product search">

<!-- Filter sidebar -->
<aside role="complementary" aria-label="Product filters">

<!-- Results area -->
<div role="list" aria-label="Search results - 24 products found">
```

### Form Controls

```html
<!-- Price filter with fieldset -->
<fieldset>
  <legend>Price</legend>
  <label for="min-price">Minimum Price</label>
  <input id="min-price" type="number" aria-label="Minimum price filter" />
</fieldset>

<!-- Rating filter with radio group -->
<div role="radiogroup" aria-label="Minimum rating filter">
  <input type="radio" aria-label="4 stars or higher" />
</div>
```

### Status Messages

```html
<!-- Sponsored badge -->
<span role="status" aria-label="This is a sponsored product">
  SPONSORED
</span>

<!-- Best value badge -->
<span role="status" aria-label="Best unit price in category">
  🏆 BEST UNIT PRICE
</span>

<!-- Discount badge -->
<span role="status" aria-label="25 percent discount">
  -25% OFF
</span>
```

### Hidden Content

Emojis and decorative icons are hidden from screen readers:

```html
<span aria-hidden="true">💰</span> Price
<svg aria-hidden="true" focusable="false">...</svg>
```

## Focus Management

### Focus Trapping

Modals and dialogs trap focus:

```js
import { trapFocus } from '../utils/accessibility'

const cleanup = trapFocus(modalElement)
// Press Tab: cycles through modal elements only
// Press Esc: closes modal
```

### Focus Restoration

When closing modals, focus returns to trigger element:

```js
import { saveFocus, restoreFocus } from '../utils/accessibility'

// Before opening modal
saveFocus()

// After closing modal
restoreFocus()
```

### First Error Focus

Form validation focuses first error:

```js
import { focusFirstError } from '../utils/accessibility'

if (hasErrors) {
  focusFirstError(formElement)
}
```

## Accessibility Testing

### Manual Testing

**Keyboard Navigation:**
1. Unplug mouse
2. Navigate entire site using only keyboard
3. Verify all functionality is accessible

**Screen Reader Testing:**
- **macOS:** VoiceOver (`Cmd + F5`)
- **Windows:** NVDA (free) or JAWS
- **Mobile:** VoiceOver (iOS) or TalkBack (Android)

### Automated Testing

**Tools:**
- [axe DevTools](https://www.deque.com/axe/devtools/) - Browser extension
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Built into Chrome DevTools
- [WAVE](https://wave.webaim.org/) - Web accessibility evaluation tool

**Run Lighthouse:**
```bash
# Open Chrome DevTools
# Go to Lighthouse tab
# Check "Accessibility"
# Click "Generate report"
```

### Test Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] Skip links appear on Tab
- [ ] Focus indicators are visible
- [ ] Screen reader announces all content correctly
- [ ] Forms have proper labels and error messages
- [ ] Images have descriptive alt text
- [ ] Color contrast meets WCAG AA
- [ ] Page works at 200% zoom
- [ ] Reduced motion is respected
- [ ] High contrast mode works

## Implementation Examples

### Accessible Form

```jsx
<form role="search" aria-label="Product search">
  <label htmlFor="search-input" className="sr-only">
    Search for products
  </label>
  <input
    id="search-input"
    type="text"
    aria-label="Search for products on Amazon"
    aria-describedby="search-description"
  />
  <span id="search-description" className="sr-only">
    Enter product name to search for deals
  </span>
  <button type="submit" aria-label="Search for products">
    Search
  </button>
</form>
```

### Accessible Product Card

```jsx
<article aria-label="Optimum Nutrition Whey Protein - Sponsored">
  <img
    src={image_url}
    alt="Optimum Nutrition Whey Protein by Optimum Nutrition"
    loading="lazy"
  />

  <h3>
    <span className="sr-only">Product: </span>
    Optimum Nutrition Whey Protein
  </h3>

  <span aria-label="Current price: 54 dollars and 99 cents">
    <span aria-hidden="true">$54.99</span>
  </span>

  <div aria-label="Rated 4.7 out of 5 stars, based on 5,000 reviews">
    <span aria-hidden="true">★ 4.7 (5,000 reviews)</span>
  </div>

  <a
    href={amazon_url}
    aria-label="View Optimum Nutrition Whey Protein on Amazon (opens in new tab)"
  >
    View on Amazon
  </a>
</article>
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Articles](https://webaim.org/articles/)
- [The A11Y Project](https://www.a11yproject.com/)
- [Inclusive Components](https://inclusive-components.design/)

## Reporting Accessibility Issues

If you encounter an accessibility issue:

1. Open a GitHub issue with the "accessibility" label
2. Describe the issue and steps to reproduce
3. Mention your assistive technology (screen reader, browser, OS)
4. Include screenshots if applicable

We're committed to maintaining WCAG 2.1 Level AA compliance and will address all accessibility issues promptly.

---

**Accessibility is not a feature, it's a fundamental right. We build for everyone.**
