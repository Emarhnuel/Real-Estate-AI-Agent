import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Navigation from '@/components/Navigation';
import { HalloweenCard } from '@/components/ui/HalloweenCard';
import { SpookyButton } from '@/components/ui/SpookyButton';
import { PumpkinIcon, GhostIcon, SkullIcon } from '@/components/ui/HalloweenIcons';

export default function Home() {
  return (
    <main className="min-h-screen relative">
      {/* Background Image with Dark Overlay */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: 'url(https://img.freepik.com/free-photo/location-symbol-with-building_23-2151649463.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        <div className="absolute inset-0 bg-black/85"></div>
      </div>
      
      {/* Content */}
      <div className="relative z-10">
      {/* Cobwebs */}
      <div className="cobweb-corner cobweb-top-left">
        <svg viewBox="0 0 150 150" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 0 L75 75 L0 150 M0 0 L150 0 L75 75 M75 75 L150 150" stroke="#E0E0E0" strokeWidth="1" opacity="0.3"/>
          <circle cx="75" cy="75" r="3" fill="#E0E0E0" opacity="0.5"/>
        </svg>
      </div>
      <div className="cobweb-corner cobweb-top-right">
        <svg viewBox="0 0 150 150" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 0 L75 75 L0 150 M0 0 L150 0 L75 75 M75 75 L150 150" stroke="#E0E0E0" strokeWidth="1" opacity="0.3"/>
          <circle cx="75" cy="75" r="3" fill="#E0E0E0" opacity="0.5"/>
        </svg>
      </div>

      <Navigation />
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Hero Section */}
        <div className="text-center py-16">
          <h2 className="text-7xl font-bold mb-6 glitch pumpkin-pulse" style={{ fontFamily: "'Creepster', cursive", color: '#FF6B00', textShadow: '0 0 20px rgba(255,107,0,0.8), 0 0 40px rgba(139,0,255,0.5)' }}>
            Find Your Perfect
            <br />
            <span className="text-[#8B00FF]">Haunted</span> Property
          </h2>
          <p className="text-xl text-[#E0E0E0] mb-12 max-w-2xl mx-auto">
            Your <span className="text-[#FF6B00] font-bold">supernatural</span> assistant for property search, location analysis, and real estate insights
          </p>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="text-lg py-4 px-8 bg-gradient-to-r from-[#FF6B00] to-[#8B00FF] hover:from-[#ff8533] hover:to-[#a333ff] text-white font-bold rounded-lg shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_30px_rgba(255,107,0,0.8)] uppercase tracking-wider transition-all transform hover:scale-105" style={{ fontFamily: "'Creepster', cursive" }}>
                🎃 Enter If You Dare
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/agent">
              <button className="text-lg py-4 px-8 bg-gradient-to-r from-[#FF6B00] to-[#8B00FF] hover:from-[#ff8533] hover:to-[#a333ff] text-white font-bold rounded-lg shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_30px_rgba(255,107,0,0.8)] uppercase tracking-wider transition-all transform hover:scale-105" style={{ fontFamily: "'Creepster', cursive" }}>
                👻 Start Haunting Now
              </button>
            </Link>
          </SignedIn>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-16">
          <HalloweenCard variant="neubrutalism" className="p-6 float-animation">
            <div className="text-5xl mb-4 pumpkin-pulse">
              <PumpkinIcon className="w-16 h-16 text-[#FF6B00]" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-[#FF6B00]" style={{ fontFamily: "'Creepster', cursive" }}>
              Cursed Property Search
            </h3>
            <p className="text-[#E0E0E0]">
              Describe your ideal haunted property and let our AI spirits find the perfect matches from the beyond
            </p>
          </HalloweenCard>

          <HalloweenCard variant="lifted" className="p-6 float-animation" style={{ animationDelay: '0.2s' }}>
            <div className="text-5xl mb-4">
              <GhostIcon className="w-16 h-16 text-[#8B00FF]" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-[#8B00FF]" style={{ fontFamily: "'Creepster', cursive" }}>
              Spectral Analysis
            </h3>
            <p className="text-[#E0E0E0]">
              Get paranormal insights on nearby amenities, ghostly attractions, and neighborhood hauntings
            </p>
          </HalloweenCard>

          <HalloweenCard variant="neubrutalism" className="p-6 float-animation" style={{ animationDelay: '0.4s' }}>
            <div className="text-5xl mb-4">
              <SkullIcon className="w-16 h-16 text-[#FF6B00]" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-[#FF6B00]" style={{ fontFamily: "'Creepster', cursive" }}>
              Deadly Reports
            </h3>
            <p className="text-[#E0E0E0]">
              Receive bone-chilling property reports with cursed images and location pros & cons from the grave
            </p>
          </HalloweenCard>
        </div>

        {/* How It Works Section */}
        <div className="max-w-5xl mx-auto mt-32 mb-16">
          <h2 className="text-5xl font-bold text-center mb-4 text-[#8B00FF]" style={{ fontFamily: "'Creepster', cursive" }}>
            🔮 How The Curse Works
          </h2>
          <p className="text-center text-[#E0E0E0] mb-16 text-lg">
            Follow these mystical steps to find your haunted dwelling
          </p>

          <div className="space-y-12">
            {/* Step 1 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-[#FF6B00] to-[#8B00FF] rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-[0_0_20px_rgba(255,107,0,0.6)]">
                1
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#FF6B00] mb-2" style={{ fontFamily: "'Creepster', cursive" }}>
                  Cast Your Search Spell
                </h3>
                <p className="text-[#E0E0E0] text-lg">
                  Tell our AI spirits what kind of haunted property you seek - location, bedrooms, budget, and any supernatural preferences
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-[#8B00FF] to-[#FF6B00] rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-[0_0_20px_rgba(139,0,255,0.6)]">
                2
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#8B00FF] mb-2" style={{ fontFamily: "'Creepster', cursive" }}>
                  Review Cursed Properties
                </h3>
                <p className="text-[#E0E0E0] text-lg">
                  Our spirits will summon matching properties from the realm. Review each haunted dwelling and select the ones that call to you
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-[#FF6B00] to-[#8B00FF] rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-[0_0_20px_rgba(255,107,0,0.6)]">
                3
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[#FF6B00] mb-2" style={{ fontFamily: "'Creepster', cursive" }}>
                  Receive Paranormal Report
                </h3>
                <p className="text-[#E0E0E0] text-lg">
                  Get a comprehensive investigation report with location analysis, nearby haunts, cursed images, and spectral insights
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Why Choose Us Section */}
        <div className="max-w-5xl mx-auto mt-32 mb-16">
          <h2 className="text-5xl font-bold text-center mb-4 text-[#FF6B00]" style={{ fontFamily: "'Creepster', cursive" }}>
            👻 Why Haunt With Us?
          </h2>
          <p className="text-center text-[#E0E0E0] mb-16 text-lg">
            The most powerful supernatural real estate experience
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            <HalloweenCard variant="neubrutalism" className="p-6">
              <div className="flex items-start gap-4">
                <span className="text-4xl">⚡</span>
                <div>
                  <h3 className="text-xl font-bold text-[#FF6B00] mb-2">Lightning Fast Spirits</h3>
                  <p className="text-[#E0E0E0]">
                    Our AI spirits work at supernatural speed to find your perfect property in seconds, not days
                  </p>
                </div>
              </div>
            </HalloweenCard>

            <HalloweenCard variant="lifted" className="p-6">
              <div className="flex items-start gap-4">
                <span className="text-4xl">🎯</span>
                <div>
                  <h3 className="text-xl font-bold text-[#8B00FF] mb-2">Deadly Accurate</h3>
                  <p className="text-[#E0E0E0]">
                    Advanced AI ensures only properties matching your exact cursed criteria are summoned
                  </p>
                </div>
              </div>
            </HalloweenCard>

            <HalloweenCard variant="lifted" className="p-6">
              <div className="flex items-start gap-4">
                <span className="text-4xl">🗺️</span>
                <div>
                  <h3 className="text-xl font-bold text-[#8B00FF] mb-2">Spectral Location Intel</h3>
                  <p className="text-[#E0E0E0]">
                    Deep analysis of nearby haunts, amenities, and neighborhood spirits for informed decisions
                  </p>
                </div>
              </div>
            </HalloweenCard>

            <HalloweenCard variant="neubrutalism" className="p-6">
              <div className="flex items-start gap-4">
                <span className="text-4xl">🔒</span>
                <div>
                  <h3 className="text-xl font-bold text-[#FF6B00] mb-2">Cursed Privacy</h3>
                  <p className="text-[#E0E0E0]">
                    Your search remains in the shadows - secure, private, and protected by dark magic
                  </p>
                </div>
              </div>
            </HalloweenCard>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto mt-32 mb-16 text-center">
          <HalloweenCard variant="lifted" className="p-12">
            <h2 className="text-4xl font-bold mb-4 text-[#8B00FF]" style={{ fontFamily: "'Creepster', cursive" }}>
              Ready to Find Your Haunted Home?
            </h2>
            <p className="text-[#E0E0E0] text-lg mb-8">
              Join the spirits and start your supernatural property search today
            </p>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="text-lg py-4 px-8 bg-gradient-to-r from-[#FF6B00] to-[#8B00FF] hover:from-[#ff8533] hover:to-[#a333ff] text-white font-bold rounded-lg shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_30px_rgba(255,107,0,0.8)] uppercase tracking-wider transition-all transform hover:scale-105" style={{ fontFamily: "'Creepster', cursive" }}>
                  🎃 Begin Your Journey
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/agent">
                <button className="text-lg py-4 px-8 bg-gradient-to-r from-[#FF6B00] to-[#8B00FF] hover:from-[#ff8533] hover:to-[#a333ff] text-white font-bold rounded-lg shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_30px_rgba(255,107,0,0.8)] uppercase tracking-wider transition-all transform hover:scale-105" style={{ fontFamily: "'Creepster', cursive" }}>
                  👻 Enter Spirit Portal
                </button>
              </Link>
            </SignedIn>
          </HalloweenCard>
        </div>
      </div>
      </div>
    </main>
  );
}
