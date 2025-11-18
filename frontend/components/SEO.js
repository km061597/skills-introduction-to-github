/**
 * SEO Component for Meta Tags and Open Graph
 *
 * Improves search engine visibility and social sharing
 */
import Head from 'next/head'

export default function SEO({
  title = 'SmartDeal - Amazon Search Without the BS',
  description = 'Find the best Amazon deals with true unit price comparison. Filter out sponsored ads and discover hidden gems with the most intelligent Amazon search tool.',
  keywords = 'amazon deals, unit price comparison, best amazon prices, amazon search, deal finder, price comparison, hidden deals',
  ogImage = '/og-image.png',
  ogType = 'website',
  twitterCard = 'summary_large_image',
  canonical,
  noindex = false,
  nofollow = false
}) {
  const siteUrl = process.env.NEXT_PUBLIC_URL || 'https://smartdeal.com'
  const fullTitle = title.includes('SmartDeal') ? title : `${title} | SmartDeal`
  const fullCanonical = canonical || siteUrl

  return (
    <Head>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

      {/* Robots */}
      {(noindex || nofollow) && (
        <meta
          name="robots"
          content={`${noindex ? 'noindex' : 'index'},${nofollow ? 'nofollow' : 'follow'}`}
        />
      )}

      {/* Canonical URL */}
      <link rel="canonical" href={fullCanonical} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={fullCanonical} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={`${siteUrl}${ogImage}`} />
      <meta property="og:site_name" content="SmartDeal" />

      {/* Twitter */}
      <meta property="twitter:card" content={twitterCard} />
      <meta property="twitter:url" content={fullCanonical} />
      <meta property="twitter:title" content={fullTitle} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={`${siteUrl}${ogImage}`} />

      {/* Additional Meta Tags */}
      <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      <meta httpEquiv="Content-Type" content="text/html; charset=utf-8" />
      <meta name="language" content="English" />
      <meta name="author" content="SmartDeal" />

      {/* Favicons */}
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="manifest" href="/site.webmanifest" />
      <meta name="theme-color" content="#0066cc" />

      {/* PWA Meta Tags */}
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      <meta name="apple-mobile-web-app-title" content="SmartDeal" />

      {/* Structured Data - Organization */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'SmartDeal',
            description: description,
            url: siteUrl,
            logo: `${siteUrl}/logo.png`,
            sameAs: [
              // Add social media links
            ]
          })
        }}
      />
    </Head>
  )
}

/**
 * Product-specific SEO component
 */
export function ProductSEO({ product }) {
  const title = `${product.title} - Best Price Comparison`
  const description = `${product.title} for $${product.current_price}. Unit price: $${product.unit_price}/${product.unit_type}. Compare prices and find the best deal on Amazon.`

  return (
    <>
      <SEO
        title={title}
        description={description}
        ogType="product"
        ogImage={product.image_url}
      />
      <Head>
        {/* Product Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Product',
              name: product.title,
              image: product.image_url,
              description: product.title,
              brand: {
                '@type': 'Brand',
                name: product.brand
              },
              offers: {
                '@type': 'Offer',
                price: product.current_price,
                priceCurrency: 'USD',
                availability: product.in_stock
                  ? 'https://schema.org/InStock'
                  : 'https://schema.org/OutOfStock',
                url: product.amazon_url
              },
              aggregateRating: product.rating && {
                '@type': 'AggregateRating',
                ratingValue: product.rating,
                reviewCount: product.review_count
              }
            })
          }}
        />
      </Head>
    </>
  )
}

/**
 * Search Results SEO
 */
export function SearchSEO({ query, resultCount }) {
  const title = `${query} - ${resultCount} Results`
  const description = `Find the best deals on ${query} with unit price comparison. We found ${resultCount} products with true price analysis and no sponsored clutter.`

  return (
    <>
      <SEO
        title={title}
        description={description}
        noindex={true} // Don't index search result pages
      />
      <Head>
        {/* Search Results Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SearchResultsPage',
              name: title,
              description: description
            })
          }}
        />
      </Head>
    </>
  )
}
