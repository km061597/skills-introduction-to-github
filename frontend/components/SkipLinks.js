/**
 * Skip Links Component
 *
 * Provides keyboard users with quick navigation to main content areas
 * Following WCAG 2.1 Level AA guidelines
 */

export default function SkipLinks() {
  return (
    <div className="skip-links">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#search" className="skip-link">
        Skip to search
      </a>
      <a href="#filters" className="skip-link">
        Skip to filters
      </a>
      <a href="#results" className="skip-link">
        Skip to results
      </a>

      <style jsx>{`
        .skip-links {
          position: absolute;
          top: 0;
          left: 0;
          z-index: 9999;
        }

        .skip-link {
          position: absolute;
          left: -10000px;
          top: auto;
          width: 1px;
          height: 1px;
          overflow: hidden;
          background: #0066cc;
          color: white;
          padding: 0.75rem 1.5rem;
          font-weight: 600;
          text-decoration: none;
          border-radius: 0 0 0.25rem 0.25rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .skip-link:focus {
          position: fixed;
          left: 0.5rem;
          top: 0.5rem;
          width: auto;
          height: auto;
          overflow: visible;
          z-index: 10000;
          outline: 3px solid #ffbf47;
          outline-offset: 2px;
        }

        @media (prefers-reduced-motion: reduce) {
          .skip-link {
            transition: none;
          }
        }
      `}</style>
    </div>
  )
}
