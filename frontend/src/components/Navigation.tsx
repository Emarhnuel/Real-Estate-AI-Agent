import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';
import { SpookyButton } from '@/components/ui/SpookyButton';
import { BatIcon } from '@/components/ui/HalloweenIcons';

export default function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();

  return (
    <nav className="bg-[#1a1a1a]/90 backdrop-blur-lg border-b-2 border-[#FF6B00] relative z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 skeleton-shake">
            <BatIcon className="w-8 h-8 text-[#FF6B00] pumpkin-pulse" />
            <span className="text-2xl font-bold text-[#FF6B00]" style={{ fontFamily: "'Creepster', cursive", textShadow: '0 0 10px rgba(255,107,0,0.8)' }}>
              Haunted Homes
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <SignedIn>
              <Link 
                href="/" 
                className={`transition-all font-semibold ${
                  router.pathname === '/' 
                    ? 'text-[#FF6B00] drop-shadow-[0_0_8px_rgba(255,107,0,0.8)]' 
                    : 'text-[#E0E0E0] hover:text-[#FF6B00] hover:drop-shadow-[0_0_8px_rgba(255,107,0,0.6)]'
                }`}
              >
                🏚️ Home
              </Link>
              <Link 
                href="/agent" 
                className={`transition-all font-semibold ${
                  router.pathname === '/agent' 
                    ? 'text-[#8B00FF] drop-shadow-[0_0_8px_rgba(139,0,255,0.8)]' 
                    : 'text-[#E0E0E0] hover:text-[#8B00FF] hover:drop-shadow-[0_0_8px_rgba(139,0,255,0.6)]'
                }`}
              >
                👻 Spirit Guide
              </Link>
              <Link 
                href="/profile" 
                className={`transition-all font-semibold ${
                  router.pathname.startsWith('/profile') 
                    ? 'text-[#00FF41] drop-shadow-[0_0_8px_rgba(0,255,65,0.8)]' 
                    : 'text-[#E0E0E0] hover:text-[#00FF41] hover:drop-shadow-[0_0_8px_rgba(0,255,65,0.6)]'
                }`}
              >
                💀 Profile
              </Link>
              <UserButton 
                showName={true}
                appearance={{
                  elements: {
                    userButtonAvatarBox: "w-10 h-10 border-2 border-[#FF6B00] shadow-[0_0_10px_rgba(255,107,0,0.6)]",
                    userButtonPopoverCard: "bg-[#1a1a1a] border-2 border-[#FF6B00] shadow-xl"
                  }
                }}
              />
            </SignedIn>
            <SignedOut>
              <SignInButton mode="modal">
                <SpookyButton variant="secondary" className="py-2 px-6">
                  🧛 Sign In
                </SpookyButton>
              </SignInButton>
            </SignedOut>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-4">
            <SignedIn>
              <UserButton 
                appearance={{
                  elements: {
                    userButtonAvatarBox: "w-10 h-10 border-2 border-[#FF6B00]"
                  }
                }}
              />
            </SignedIn>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-[#FF6B00] hover:text-[#ff8533] transition-colors"
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {mobileMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t-2 border-[#8B00FF]">
            <div className="flex flex-col gap-4">
              <SignedIn>
                <Link 
                  href="/" 
                  className="text-[#E0E0E0] hover:text-[#FF6B00] transition-colors py-2 font-semibold"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  🏚️ Home
                </Link>
                <Link 
                  href="/agent" 
                  className="text-[#E0E0E0] hover:text-[#8B00FF] transition-colors py-2 font-semibold"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  👻 Spirit Guide
                </Link>
                <Link 
                  href="/profile" 
                  className="text-[#E0E0E0] hover:text-[#00FF41] transition-colors py-2 font-semibold"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  💀 Profile
                </Link>
              </SignedIn>
              <SignedOut>
                <SignInButton mode="modal">
                  <SpookyButton variant="secondary" className="w-full py-2 px-6">
                    🧛 Sign In
                  </SpookyButton>
                </SignInButton>
              </SignedOut>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
