import { useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import SearchBar from '../components/SearchBar'
import Header from '../components/Header'

export default function Home() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (query) => {
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <>
      <Head>
        <title>SmartDeal - Amazon Search Without the BS</title>
        <meta name="description" content="Find the best Amazon deals with true unit price comparison and zero sponsored clutter" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />

        <main className="container mx-auto px-4 py-16">
          {/* Hero Section */}
          <div className="text-center max-w-4xl mx-auto mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Search Smarter, Save More
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-12">
              The Amazon search Amazon should have built - minus the BS
            </p>

            {/* Search Box */}
            <div className="max-w-2xl mx-auto mb-8">
              <SearchBar onSearch={handleSearch} />
            </div>

            {/* Feature Highlights */}
            <div className="grid md:grid-cols-3 gap-6 text-left">
              <FeatureCard
                icon="🚫"
                title="Zero Sponsored Clutter"
                description="Only organic results. No ads. No BS."
              />
              <FeatureCard
                icon="💰"
                title="True Unit Price"
                description="Compare $/oz, $/count across all products"
              />
              <FeatureCard
                icon="🏆"
                title="Find Hidden Gems"
                description="Discover deals Amazon buries"
              />
            </div>
          </div>

          {/* Example Searches */}
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 text-center">
              Try searching for:
            </h2>
            <div className="flex flex-wrap gap-3 justify-center">
              {[
                'protein powder',
                'coffee beans',
                'laundry detergent',
                'paper towels',
                'vitamins',
                'dog food'
              ].map((term) => (
                <button
                  key={term}
                  onClick={() => handleSearch(term)}
                  className="px-4 py-2 bg-white hover:bg-blue-50 text-blue-600 rounded-lg shadow-sm hover:shadow-md transition-all border border-blue-200"
                >
                  {term}
                </button>
              ))}
            </div>
          </div>

          {/* Stats Section */}
          <div className="max-w-4xl mx-auto mt-16 p-8 bg-white rounded-lg shadow-lg">
            <div className="grid md:grid-cols-3 gap-8 text-center">
              <StatCard number="30-60%" label="Sponsored results we filter out" />
              <StatCard number="100%" label="True unit price accuracy" />
              <StatCard number="$" label="Money saved per search" />
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-white py-8 mt-16">
          <div className="container mx-auto px-4 text-center">
            <p className="text-gray-400">
              SmartDeal is not affiliated with Amazon. We earn from qualifying purchases through affiliate links.
            </p>
            <p className="text-gray-500 mt-2 text-sm">
              © 2025 SmartDeal. Built with ❤️ for smart shoppers.
            </p>
          </div>
        </footer>
      </div>
    </>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function StatCard({ number, label }) {
  return (
    <div>
      <div className="text-4xl font-bold text-blue-600 mb-2">{number}</div>
      <div className="text-gray-600">{label}</div>
    </div>
  )
}
