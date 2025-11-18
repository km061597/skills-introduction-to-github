import ProductCard from './ProductCard'

export default function ProductGrid({ products, ariaLabel = 'Search results' }) {
  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      role="list"
      aria-label={`${ariaLabel} - ${products.length} products found`}
      id="results"
    >
      {products.map((product, index) => (
        <div key={product.asin} role="listitem">
          <ProductCard product={product} index={index} />
        </div>
      ))}
    </div>
  )
}
