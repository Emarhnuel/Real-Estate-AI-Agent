import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Navigation from '@/components/Navigation';
import { HalloweenCard } from '@/components/ui/HalloweenCard';
import { SpookyButton } from '@/components/ui/SpookyButton';
import { PumpkinIcon, GhostIcon, SkullIcon } from '@/components/ui/HalloweenIcons';

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0A0A0A] relative">
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
            Your <span className="text-[#00FF41] font-bold">supernatural</span> assistant for property search, location analysis, and real estate insights
          </p>
          
          <SignedOut>
            <SignInButton mode="modal">
              <SpookyButton variant="primary" className="text-lg py-4 px-8">
                🎃 Enter If You Dare
              </SpookyButton>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/agent">
              <SpookyButton variant="primary" className="text-lg py-4 px-8">
                👻 Start Haunting Now
              </SpookyButton>
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

          <HalloweenCard variant="corners" className="p-6 float-animation" style={{ animationDelay: '0.4s' }}>
            <div className="text-5xl mb-4">
              <SkullIcon className="w-16 h-16 text-[#00FF41]" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-[#00FF41]" style={{ fontFamily: "'Creepster', cursive" }}>
              Deadly Reports
            </h3>
            <p className="text-[#E0E0E0]">
              Receive bone-chilling property reports with cursed images and location pros & cons from the grave
            </p>
          </HalloweenCard>
        </div>
      </div>
    </main>
  );
}
