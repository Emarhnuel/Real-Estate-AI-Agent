import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Navigation from '@/components/Navigation';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center py-16">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Find Your Perfect
            <br />
            Property with AI
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Your intelligent assistant for property search, location analysis, and real estate insights
          </p>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Get Started Free
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/agent">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Searching Now
              </button>
            </Link>
          </SignedIn>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-16">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="text-4xl mb-4">🏠</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">Smart Property Search</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Describe your ideal property in natural language and let AI find the perfect matches
              </p>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="text-4xl mb-4">📍</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">Location Analysis</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Get detailed insights on nearby amenities, attractions, and neighborhood quality
              </p>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
            <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">Comprehensive Reports</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receive detailed property reports with images, reviews, and location pros & cons
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
